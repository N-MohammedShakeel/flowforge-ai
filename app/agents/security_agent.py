# app/agents/security_agent.py
import logging
import os
from typing import Optional
from pydantic import BaseModel
from app.agents.base import BaseAgent
from app.models.state import ArchitectureState, SecurityReport, ComplianceItem, Node, Edge
from app.prompts import SECURITY_SYSTEM_PROMPT
from app.rag.service import RagService

logger = logging.getLogger("flowforge.ai.security")


def _get_tavily():
    """Lazily import TavilySearchResults so the app still works without the key."""
    try:
        from langchain_tavily import TavilySearch
        api_key = os.getenv("TAVILY_API_KEY", "")
        if not api_key:
            return None
        return TavilySearch(max_results=5, tavily_api_key=api_key)
    except Exception:
        return None


class SecurityOutput(BaseModel):
    security_report: SecurityReport

    class Config:
        extra = "allow"


class SecurityAgent(BaseAgent):
    """
    Security & Compliance Auditor.

    Workflow:
    1. Build a compliance query from project type (e.g. "HIPAA requirements for healthcare app")
    2. Check the RAG knowledge base FIRST if cached results exist, use them
    3. If RAG returns nothing (or is thin), fire a Tavily web search and cache the results back into RAG
    4. Feed everything to the LLM for structured compliance + vulnerability analysis
    """

    def __init__(self):
        super().__init__()
        self.rag = RagService()
        self.search_tool = _get_tavily()

    async def execute(self, state: ArchitectureState) -> ArchitectureState:
        # -- 1. Build compliance query -----------------------------------------
        project_desc = ""
        if state.requirements:
            project_desc = (
                f"{state.requirements.project_name} {state.requirements.description}. "
                f"Features: {', '.join(state.requirements.features[:5])}"
            )
        elif state.user_input:
            project_desc = state.user_input

        compliance_query = f"Security compliance requirements and standards for: {project_desc}"
        logger.info("SecurityAgent compliance query: %s", compliance_query[:120])

        # -- 2. Check RAG knowledge base first --------------------------------
        rag_knowledge = await self.rag.retrieve(
            query=compliance_query, k=6, doc_type="compliance"
        )

        web_search_results = ""
        web_sources = []

        # -- 3. Web search if RAG is thin / empty -----------------------------
        if not rag_knowledge or len(rag_knowledge) < 200:
            logger.info("RAG knowledge thin triggering Tavily web search")
            if self.search_tool:
                try:
                    search_results = self.search_tool.invoke(compliance_query)
                    if search_results:
                        for r in search_results:
                            web_sources.append(r.get("url", ""))
                            web_search_results += f"\n\n[{r.get('url', '')}]\n{r.get('content', '')}"

                        # Cache the web results into RAG so next time we skip the web call
                        if web_search_results.strip():
                            await self.rag.index_text(
                                web_search_results,
                                metadata={
                                    "doc_type": "compliance",
                                    "source": "tavily_web_search",
                                    "query": compliance_query,
                                },
                            )
                            logger.info(
                                "Cached %d web search chars into RAG knowledge base",
                                len(web_search_results),
                            )
                except Exception as e:
                    logger.warning("Tavily search failed: %s", e)
            else:
                logger.warning("Tavily not configured skipping web search (set TAVILY_API_KEY)")
        else:
            logger.info("RAG knowledge base hit skipping web search (%d chars)", len(rag_knowledge))

        # -- 4. Assemble user prompt -------------------------------------------
        nodes_text = "\n".join(
            f"  - {n.label} ({n.technology}, type={n.type})" for n in state.nodes
        )
        edges_text = "\n".join(
            f"  - {e.source} ? {e.target} [{e.type}]" for e in state.edges
        )
        req_text = (
            state.requirements.model_dump_json(indent=2)
            if state.requirements
            else "No structured requirements yet"
        )

        user_prompt = f"""
Project: {project_desc or "Unknown project"}

Current Architecture:
Nodes:
{nodes_text or "  (none yet)"}

Edges:
{edges_text or "  (none yet)"}

Requirements:
{req_text}

--- RAG Knowledge Base Results ---
{rag_knowledge or "(No cached compliance knowledge found)"}

--- Live Web Search Results ---
{web_search_results or "(No web search performed or no results)"}
"""

        # -- 5. LLM structured output ------------------------------------------
        prompt = self.create_prompt(SECURITY_SYSTEM_PROMPT, user_prompt)
        chain = prompt | self.structured_llm.with_structured_output(
            SecurityOutput, method="json_mode"
        )

        try:
            result = await chain.ainvoke({})
            report: SecurityReport = result.security_report
            report.web_sources = web_sources
            logger.info(
                "SecurityAgent done risk: %s, %d compliance items, %d required nodes",
                report.risk_level,
                len(report.compliance_items),
                len(report.required_nodes),
            )
            state.security_report = report

            # Merge required nodes/edges into the main architecture
            existing_ids = {n.id for n in state.nodes}
            for node in report.required_nodes:
                if node.id not in existing_ids:
                    state.nodes.append(node)
                    existing_ids.add(node.id)

            for edge in report.required_edges:
                state.edges.append(edge)

        except Exception as e:
            logger.error("SecurityAgent LLM failed: %s", e)
            # Minimal fallback
            state.security_report = SecurityReport(
                risk_level="high",
                vulnerabilities=["Unable to complete security audit manual review required"],
                security_recommendations=["Add API Gateway", "Implement Auth layer", "Enable TLS"],
            )

        state.last_updated = __import__("datetime").datetime.utcnow()
        return state
