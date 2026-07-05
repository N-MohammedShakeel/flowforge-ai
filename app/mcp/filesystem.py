# app/mcp/filesystem.py
import os
import zipfile
import tempfile
from pathlib import Path
from typing import List, Dict, Any
from app.config import get_settings

settings = get_settings()

class McpService:
    def __init__(self):
        
        self.upload_dir = Path(settings.uploaded_projects_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    async def analyze_project(self, zip_path: str) -> str:
        """Extract and analyze uploaded project ZIP"""
        if not os.path.exists(zip_path):
            raise FileNotFoundError(f"ZIP file not found: {zip_path}")

        project_summary = []

        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                # Extract ZIP
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
                
                root_path = Path(temp_dir)
                
                # Analyze project structure
                project_summary.append("=== PROJECT ANALYSIS ===\n")
                
                # Look for key files
                key_files = self._find_key_files(root_path)
                for file_path, content in key_files.items():
                    project_summary.append(f"\n--- {file_path} ---\n")
                    project_summary.append(content[:1500])  # Limit content size
                
                # Directory structure summary
                structure = self._get_directory_structure(root_path)
                project_summary.append("\n=== DIRECTORY STRUCTURE ===\n")
                project_summary.append(structure)

        except Exception as e:
            return f"Error analyzing project: {str(e)}"

        return "\n".join(project_summary)

    def _find_key_files(self, root: Path) -> Dict[str, str]:
        """Find and read important project files"""
        key_patterns = [
            "pom.xml", "build.gradle", "package.json", "requirements.txt",
            "README.md", "application.yml", "application.properties",
            "*.java", "*.py", "*.ts", "*.js"
        ]
        
        found = {}
        
        for pattern in key_patterns:
            for file in root.rglob(pattern):
                try:
                    if file.is_file() and file.stat().st_size < 50000:  # Skip huge files
                        with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            rel_path = str(file.relative_to(root))
                            found[rel_path] = content
                except:
                    continue
                    
        return found

    def _get_directory_structure(self, root: Path, max_depth: int = 3) -> str:
        """Generate simplified directory tree"""
        lines = []
        for path in sorted(root.rglob("*")):
            if path.is_dir() or path.name.startswith("."):
                continue
            depth = len(path.relative_to(root).parts)
            if depth > max_depth:
                continue
            prefix = "  " * (depth - 1) + "├── " if depth > 1 else ""
            lines.append(f"{prefix}{path.name}")
        return "\n".join(lines[:50])  # Limit output