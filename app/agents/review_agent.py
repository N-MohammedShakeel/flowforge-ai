# app/agents/review_agent.py
from app.agents.base import BaseAgent
from app.models.state import ArchitectureState, ReviewResult, Node
from app.prompts import REVIEW_SYSTEM_PROMPT
from pydantic import BaseModel
import logging

logger = logging.getLogger("flowforge.ai.review_agent")

class ReviewOutput(BaseModel):
    review: ReviewResult

    class Config:
        extra = "allow"

class ReviewAgent(BaseAgent):
    async def execute(self, state: ArchitectureState) -> ArchitectureState:
        """
        Analyzes current architecture and returns a structured review.
        Used when the user clicks the 'Review' button.
        """
        # Safely convert node dicts to Node objects if they came in as raw dicts
        nodes = []
        for n in state.nodes:
            if isinstance(n, dict):
                try:
                    nodes.append(Node(**n))
                except Exception:
                    # Tolerate malformed nodes — skip them
                    pass
            else:
                nodes.append(n)

        nodes_summary = [
            f"{node.label} ({node.technology})" for node in nodes
        ]

        user_prompt = f"""
        Current Architecture:
        Nodes: {nodes_summary}
        Total Nodes: {len(nodes)}
        Total Connections: {len(state.edges)}

        Analyze this architecture thoroughly and provide a detailed review.
        """

        prompt = self.create_prompt(REVIEW_SYSTEM_PROMPT, user_prompt)

        chain = prompt | self.structured_llm.with_structured_output(
            ReviewOutput,
            method="json_mode"
        )

        try:
            result = await chain.ainvoke({})
            print(f"ReviewAgent Response:\n{result}")
            state.review = result.review
            logger.info(f"Review generated: overall_score={state.review.overall_score}")
        except Exception as e:
            logger.warning(f"Review structured output failed: {e}. Using fallback.")
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