from app.agents.base import BaseAgent
from app.models.state import ArchitectureState, EnhancedArchitectureOutput, Node
from app.prompts import ENHANCEMENT_SYSTEM_PROMPT

class EnhancementAgent(BaseAgent):
    async def execute(self, state: ArchitectureState) -> ArchitectureState:
        current_nodes_summary = ", ".join([n.label for n in state.nodes])

        user_prompt = f"""
Current Architecture Nodes: {current_nodes_summary}

Review Feedback:
{state.review.model_dump_json(indent=2) if state.review else 'No review available.'}

Provide a complete improved architecture.
"""

        prompt = self.create_prompt(ENHANCEMENT_SYSTEM_PROMPT, user_prompt)
        
        chain = prompt | self.structured_llm.with_structured_output(
            EnhancedArchitectureOutput, 
            method="json_mode"
        )
        
        try:
            result = await chain.ainvoke({})
            print(f"EnhancementAgent Response:\n{result}")
            state.nodes = result.nodes
            state.edges = result.edges
            print("✅ Enhancement successful with new architecture")
        except Exception as e:
            print(f"Enhancement structured output failed: {e}")
            # Keep current architecture + add one improvement
            if not any(n.technology == "Redis" for n in state.nodes):
                state.nodes.append(
                    Node(
                        id="redis",
                        label="Redis Cache",
                        type="cache",
                        technology="Redis",
                        description="Caching layer for better performance"
                    )
                )
        
        state.last_updated = __import__('datetime').datetime.utcnow()
        return state