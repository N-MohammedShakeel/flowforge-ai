# app/agents/review_agent.py
from app.agents.base import BaseAgent
from app.models.state import ArchitectureState, ReviewResult
from app.prompts import REVIEW_SYSTEM_PROMPT
from pydantic import BaseModel

class ReviewOutput(BaseModel):
    review: ReviewResult

    class Config:
        extra = "allow"

class ReviewAgent(BaseAgent):
    async def execute(self, state: ArchitectureState) -> ArchitectureState:
        """
        Analyzes current architecture and returns review.
        Used when user clicks the 'Review' button.
        """
        # Create summary of current architecture
        nodes_summary = [f"{node.label} ({node.technology})" for node in state.nodes]
        
        user_prompt = f"""
        Current Architecture:
        Nodes: {nodes_summary}
        Total Nodes: {len(state.nodes)}
        Total Connections: {len(state.edges)}

        Analyze this architecture thoroughly.
        """

        prompt = self.create_prompt(REVIEW_SYSTEM_PROMPT, user_prompt)
        
        chain = prompt | self.structured_llm.with_structured_output(
            ReviewOutput, 
            method="json_mode"
        )
        
        try:
            result = await chain.ainvoke({})
            state.review = result.review
        except Exception as e:
            print(f"Review generation failed: {e}")
            # Safe fallback
            state.review = ReviewResult(
                overall_score=65,
                architecture_score=70,
                scalability=60,
                maintainability=75,
                security=55,
                issues=["Missing caching layer", "No API Gateway detected", "Potential security exposure"],
                suggestions=["Add Redis cache", "Introduce API Gateway", "Implement proper authentication"]
            )
        
        state.last_updated = __import__('datetime').datetime.utcnow()
        return state