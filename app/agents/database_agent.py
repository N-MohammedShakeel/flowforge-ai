# app/agents/database_agent.py
import logging
from pydantic import BaseModel
from app.agents.base import BaseAgent
from app.models.state import ArchitectureState, DatabaseSchema
from app.prompts import DATABASE_SYSTEM_PROMPT

logger = logging.getLogger("flowforge.ai.database")


class DatabaseOutput(BaseModel):
    database_schema: DatabaseSchema

    class Config:
        extra = "allow"


class DatabaseAgent(BaseAgent):
    """
    Database Design Specialist.
    Analyses requirements and existing db-type nodes to produce a high-level
    database schema (tables, columns, relationships, design notes).
    The schema is attached to the state as `database_schema` and also
    written into the metadata of the database Node for frontend display.
    """

    async def execute(self, state: ArchitectureState) -> ArchitectureState:
        db_nodes = [n for n in state.nodes if n.type == "database"]
        db_tech = db_nodes[0].technology if db_nodes else "PostgreSQL"

        req_text = (
            state.requirements.model_dump_json(indent=2)
            if state.requirements
            else "No structured requirements"
        )

        user_prompt = f"""
Database Technology: {db_tech}

Project Requirements:
{req_text}

Architecture Nodes (for context):
{chr(10).join(f"  - {n.label} ({n.type})" for n in state.nodes)}
"""

        prompt = self.create_prompt(DATABASE_SYSTEM_PROMPT, user_prompt)
        chain = prompt | self.structured_llm.with_structured_output(
            DatabaseOutput, method="json_mode"
        )

        try:
            result = await chain.ainvoke({})
            schema: DatabaseSchema = result.database_schema
            logger.info(
                "DatabaseAgent done %s, %d tables",
                schema.database_technology,
                len(schema.tables),
            )
            state.database_schema = schema

            # Write schema summary into the DB node metadata for UI display
            for node in state.nodes:
                if node.type == "database":
                    node.metadata["schema"] = {
                        "tables": [t.table_name for t in schema.tables],
                        "design_notes": schema.design_notes,
                    }

        except Exception as e:
            logger.error("DatabaseAgent LLM failed: %s", e)
            state.database_schema = DatabaseSchema(
                database_technology=db_tech,
                design_notes="Schema design failed manual schema design required",
            )

        state.last_updated = __import__("datetime").datetime.utcnow()
        return state
