# app/agents/architecture_agent.py
from app.agents.base import BaseAgent
from app.models.state import ArchitectureState, Node, Edge
from app.prompts import ARCHITECTURE_SYSTEM_PROMPT
from pydantic import BaseModel
from typing import List

class ArchitectureOutput(BaseModel):
    nodes: List[Node]
    edges: List[Edge]
    summary: str

class ArchitectureAgent(BaseAgent):
    async def execute(self, state: ArchitectureState) -> ArchitectureState:
        
        from app.rag.service import RagService
        rag_service = RagService()

        # Build context safely
        context = ""
        if state.source == "SRS" and state.project_id:
            query = f"Architecture requirements, technical stack, modules for {state.requirements.project_name if state.requirements else 'project'}"
            retrieved_chunks = await rag_service.retrieve_srs_context(query, state.project_id, k=5)
            if retrieved_chunks:
                context += f"\n--- SRS Context (Retrieved) ---\n{retrieved_chunks}\n"
        elif state.rag_context: # fallback
            context += f"\n--- SRS Context (Full) ---\n{state.rag_context}\n"
            
        if state.project_context:
            context += f"\n--- Existing Project Context ---\n{state.project_context}\n"

        # Safe user prompt
        user_prompt = f"""
                        Project Idea: {state.user_input or 'No description provided'}

                        Requirements: 
                        {state.requirements.model_dump_json(indent=2) if state.requirements else 'Not available'}

                        Additional Context:
                        {context or 'No additional context'}
                    """

        prompt = self.create_prompt(ARCHITECTURE_SYSTEM_PROMPT, user_prompt)
        
        chain = prompt | self.structured_llm.with_structured_output(
            ArchitectureOutput, 
            method="json_mode"
        )
        
        try:
            result = await chain.ainvoke({})
            print(f"ArchitectureAgent Response:\n{result}")
            state.nodes = result.nodes
            state.edges = result.edges
        except Exception as e:
            print(f"Architecture generation failed: {e}")
            # Safe fallback
            state.nodes = [
                Node(id="frontend", label="Frontend", type="frontend", technology="React", description="User Interface"),
                Node(id="backend", label="Backend", type="backend", technology="Spring Boot", description="Main Application Server"),
                Node(id="db", label="Database", type="database", technology="PostgreSQL", description="Data Storage")
            ]
            state.edges = [
                Edge(source="frontend", target="backend", type="rest")
            ]
        
        state.last_updated = __import__('datetime').datetime.utcnow()
        return state