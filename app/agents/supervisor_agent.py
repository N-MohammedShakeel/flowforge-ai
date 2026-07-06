# app/agents/supervisor_agent.py
import logging
from pydantic import BaseModel
from app.agents.base import BaseAgent
from app.models.state import ArchitectureState
from app.prompts import SUPERVISOR_SYSTEM_PROMPT

logger = logging.getLogger("flowforge.ai.supervisor")


class SupervisorDecision(BaseModel):
    decision: str
    reasoning: str


class SupervisorAgent(BaseAgent):
    """
    The Orchestrator Brain.
    Analyses the current ArchitectureState and decides which agent to
    invoke next, or terminates the loop by returning "DONE".
    """

    async def execute(self, state: ArchitectureState) -> ArchitectureState:
        # Guard: never exceed max iterations
        if state.iteration >= state.max_iterations:
            logger.warning("Max iterations reached forcing DONE")
            state.supervisor_decision = "DONE"
            return state

        snapshot = f"""
Current State Snapshot (iteration {state.iteration}/{state.max_iterations}):
- requirements:       {"present" if state.requirements else "MISSING"}
- architecture nodes: {len(state.nodes)} nodes, {len(state.edges)} edges
- security_report:    {"present (risk: " + state.security_report.risk_level + ")" if state.security_report else "MISSING"}
- database_schema:    {"present (" + str(len(state.database_schema.tables)) + " tables)" if state.database_schema else "MISSING"}
- infrastructure:     {"present" if state.infrastructure_plan else "MISSING"}
- review:             {"present (score: " + str(state.review.overall_score) + ")" if state.review else "MISSING"}

Has database nodes: {any(n.type == "database" for n in state.nodes)}
"""

        prompt = self.create_prompt(SUPERVISOR_SYSTEM_PROMPT, snapshot)
        chain = prompt | self.structured_llm.with_structured_output(
            SupervisorDecision, method="json_mode"
        )

        try:
            result = await chain.ainvoke({})
            logger.info("Supervisor ? %s | reason: %s", result.decision, result.reasoning)
            state.supervisor_decision = result.decision
        except Exception as e:
            logger.error("Supervisor failed: %s defaulting to DONE", e)
            state.supervisor_decision = "DONE"

        state.iteration += 1
        state.last_updated = __import__("datetime").datetime.utcnow()
        return state
