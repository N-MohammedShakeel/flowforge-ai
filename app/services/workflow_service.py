# app/services/workflow_service.py
from app.models.request import WorkflowRequest, ReviewRequest, EnhanceRequest
from app.models.state import ArchitectureState
from app.agents.requirement_agent import RequirementAgent
from app.agents.architecture_agent import ArchitectureAgent
from app.agents.review_agent import ReviewAgent
from app.agents.enhancement_agent import EnhancementAgent
from app.rag.service import RagService
from app.mcp.filesystem import McpService

class WorkflowService:
    def __init__(self):
        self.rag_service = RagService()
        self.mcp_service = McpService()
        self.requirement_agent = RequirementAgent()
        self.architecture_agent = ArchitectureAgent()
        self.review_agent = ReviewAgent()
        self.enhancement_agent = EnhancementAgent()

    async def generate_architecture(self, request: WorkflowRequest) -> ArchitectureState:
        """Main flow: Idea/SRS/Project → Architecture"""
        state = ArchitectureState(
            project_id=request.project_id,
            source=request.source,
            user_input=request.payload.get("description")
        )

        # Handle different sources
        if request.source == "SRS" and request.srs_file_path:
            state.rag_context = await self.rag_service.process_document(request.srs_file_path)
        elif request.source == "PROJECT" and request.project_zip_path:
            state.project_context = await self.mcp_service.analyze_project(request.project_zip_path)

        # Run agents
        state = await self.requirement_agent.execute(state)
        state = await self.architecture_agent.execute(state)

        return state

    async def review_architecture(self, request: ReviewRequest) -> ArchitectureState:
        """Review only"""
        state = ArchitectureState(
            project_id=request.project_id,
            nodes=request.nodes,
            edges=request.edges
        )
        state = await self.review_agent.execute(state)
        return state

    async def enhance_architecture(self, request: EnhanceRequest) -> ArchitectureState:
        """Enhancement only - returns improved architecture"""
        state = ArchitectureState(
            project_id=request.project_id,
            nodes=request.nodes,
            edges=request.edges,
            review=request.review
        )
        state = await self.enhancement_agent.execute(state)
        return state