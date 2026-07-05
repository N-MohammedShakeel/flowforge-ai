from app.models.request import WorkflowRequest, ReviewRequest, EnhanceRequest
from app.models.state import ArchitectureState, Node, Edge, ReviewResult
from app.agents.requirement_agent import RequirementAgent
from app.agents.architecture_agent import ArchitectureAgent
from app.agents.review_agent import ReviewAgent
from app.agents.enhancement_agent import EnhancementAgent
from app.graph.workflow import create_flowforge_graph
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
        # Compile your LangGraph instance
        self.graph = create_flowforge_graph()

    async def generate_architecture(self, request: WorkflowRequest) -> ArchitectureState:
        """Main flow: Idea/SRS/Project -> Requirement Gather -> Architecture Mapping"""
        state = ArchitectureState(
            project_id=request.project_id,
            source=request.source,
            user_input=request.payload.get("description")
        )

        # 1. Process files for Context
        if request.source == "SRS" and request.srs_file_path:
            state.rag_context = await self.rag_service.process_document(request.srs_file_path)
        elif request.source == "PROJECT" and request.project_zip_path:
            state.project_context = await self.mcp_service.analyze_project(request.project_zip_path)

        # 2. Feed into your LangGraph engine instead of doing it manually
        workflow_type = request.payload.get("workflow_type", "BASIC")
        initial_graph_state = {
            "state": state,
            "workflow_type": workflow_type,
            "payload": request.payload,
            "messages": []
        }
        
        final_graph_output = await self.graph.ainvoke(initial_graph_state)
        return final_graph_output["state"]

    async def review_architecture(self, request: ReviewRequest) -> ArchitectureState:
        """Standalone manual review endpoint (Triggers when clicking 'Review')"""
        state = ArchitectureState(
            project_id=request.project_id,
            nodes=[Node(**n) if isinstance(n, dict) else n for n in request.nodes],
            edges=[Edge(**e) if isinstance(e, dict) else e for e in request.edges]
        )
        return await self.review_agent.execute(state)

    async def enhance_architecture(self, request: EnhanceRequest) -> ArchitectureState:
        """Standalone manual enhancement endpoint (Triggers when clicking 'Enhance')"""
        state = ArchitectureState(
            project_id=request.project_id,
            nodes=[Node(**n) if isinstance(n, dict) else n for n in request.nodes],
            edges=[Edge(**e) if isinstance(e, dict) else e for e in request.edges],
            review=ReviewResult(**request.review) if request.review else None
        )
        return await self.enhancement_agent.execute(state)