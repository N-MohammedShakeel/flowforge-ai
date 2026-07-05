# app/agents/requirement_agent.py
from app.agents.base import BaseAgent
from app.models.state import ArchitectureState, Requirements
from app.prompts import REQUIREMENT_SYSTEM_PROMPT

class RequirementAgent(BaseAgent):
    async def execute(self, state: ArchitectureState) -> ArchitectureState:
        user_prompt = "User Request: " + (state.user_input or "No description provided")

        prompt = self.create_prompt(REQUIREMENT_SYSTEM_PROMPT, user_prompt)
        
        chain = prompt | self.structured_llm.with_structured_output(
            Requirements, 
            method="json_mode"
        )
        
        try:
            requirements = await chain.ainvoke({})
            state.requirements = requirements
        except Exception as e:
            print(f"Structured output failed: {e}")
            # Safe fallback
            state.requirements = Requirements(
                project_name="Bus Ticket Booking System",
                description=state.user_input or "Bus booking platform",
                actors=["Customer", "Admin"],
                modules=["User Management", "Booking Management", "Payment", "Admin Panel"],
                features=["Bus Search", "Seat Selection", "Booking", "Payment Gateway"],
                non_functional=["High Availability", "Secure Payment", "Responsive Design"],
                tech_preferences={"frontend": "React", "backend": "Spring Boot", "database": "PostgreSQL"}
            )
        
        state.last_updated = __import__('datetime').datetime.utcnow()
        return state