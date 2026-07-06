# app/agents/infrastructure_agent.py
import logging
from pydantic import BaseModel
from app.agents.base import BaseAgent
from app.models.state import ArchitectureState, InfrastructurePlan, Node, Edge
from app.prompts import INFRASTRUCTURE_SYSTEM_PROMPT

logger = logging.getLogger("flowforge.ai.infrastructure")


class InfrastructureOutput(BaseModel):
    infrastructure_plan: InfrastructurePlan

    class Config:
        extra = "allow"


class InfrastructureAgent(BaseAgent):
    """
    DevOps / Infrastructure Architect.
    Wraps the logical architecture with deployment-layer nodes:
    Load Balancers, CDN, Container Registry, Monitoring, CI/CD steps, etc.
    Merges the infra nodes/edges back into the main architecture graph.
    """

    async def execute(self, state: ArchitectureState) -> ArchitectureState:
        nodes_text = "\n".join(
            f"  - {n.label} ({n.technology}, type={n.type})" for n in state.nodes
        )
        req_text = (
            state.requirements.model_dump_json(indent=2)
            if state.requirements
            else "No structured requirements"
        )

        user_prompt = f"""
Logical Architecture Nodes:
{nodes_text or "  (none)"}

Project Requirements:
{req_text}
"""

        prompt = self.create_prompt(INFRASTRUCTURE_SYSTEM_PROMPT, user_prompt)
        chain = prompt | self.structured_llm.with_structured_output(
            InfrastructureOutput, method="json_mode"
        )

        try:
            result = await chain.ainvoke({})
            plan: InfrastructurePlan = result.infrastructure_plan
            logger.info(
                "InfrastructureAgent done target: %s, %d infra nodes",
                plan.deployment_target,
                len(plan.infra_nodes),
            )
            state.infrastructure_plan = plan

            # Merge infra nodes/edges into the main graph
            existing_ids = {n.id for n in state.nodes}
            for node in plan.infra_nodes:
                if node.id not in existing_ids:
                    state.nodes.append(node)
                    existing_ids.add(node.id)
            for edge in plan.infra_edges:
                state.edges.append(edge)

        except Exception as e:
            logger.error("InfrastructureAgent LLM failed: %s", e)
            state.infrastructure_plan = InfrastructurePlan(
                deployment_target="Docker Compose",
                ci_cd_pipeline=[
                    "1. Push to GitHub",
                    "2. GitHub Actions runs tests",
                    "3. Build & push Docker image",
                    "4. Deploy with docker-compose",
                ],
            )

        state.last_updated = __import__("datetime").datetime.utcnow()
        return state
