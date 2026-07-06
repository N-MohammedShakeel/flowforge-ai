from pydantic import BaseModel, Field
from app.agents.base import BaseAgent
from app.prompts import GUARDRAIL_SYSTEM_PROMPT

class GuardrailResult(BaseModel):
    is_valid: bool = Field(description="True if the request is related to software architecture, false otherwise")
    reason: str = Field(description="If is_valid is false, the reason or polite warning message to the user. Empty if valid.")

class GuardrailAgent(BaseAgent):
    async def evaluate(self, user_input: str) -> GuardrailResult:
        if not user_input or not user_input.strip():
            return GuardrailResult(is_valid=False, reason="Please provide a project description or idea.")
            
        user_prompt = "User Request: " + user_input
        prompt = self.create_prompt(GUARDRAIL_SYSTEM_PROMPT, user_prompt)
        
        chain = prompt | self.structured_llm.with_structured_output(
            GuardrailResult, 
            method="json_mode"
        )
        
        try:
            result = await chain.ainvoke({})
            return result
        except Exception as e:
            print(f"Guardrail Agent failed: {e}")
            # If the LLM fails, default to allowing it to avoid blocking valid requests
            return GuardrailResult(is_valid=True, reason="")

    async def execute(self, state):
        # Dummy implementation to satisfy BaseAgent abstract method.
        # GuardrailAgent uses evaluate() instead of standard state execution.
        return state
