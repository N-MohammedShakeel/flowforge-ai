# app/graph/workflow.py
from langgraph.graph import StateGraph, START, END
from app.graph.state import GraphState
from app.graph.nodes import (
    supervisor_node,
    requirement_node,
    architecture_node,
    security_node,
    database_node,
    infrastructure_node,
    review_node,
    enhancement_node,
)


def _route_from_supervisor(graph_state: dict) -> str:
    """
    Read the Supervisor's decision from the state and return the next node name.
    Maps "DONE" → END so LangGraph knows when to stop the loop.
    """
    decision = graph_state["state"].supervisor_decision or "DONE"
    routing_map = {
        "requirement":    "requirement",
        "architecture":   "architecture",
        "security":       "security",
        "database":       "database",
        "infrastructure": "infrastructure",
        "review":         "review",
        "enhancement":    "enhancement",
        "DONE":           END,
    }
    return routing_map.get(decision, END)


def create_flowforge_graph():
    workflow = StateGraph(GraphState)

    # ── Register all nodes ────────────────────────────────────────────────
    workflow.add_node("supervisor",     supervisor_node)
    workflow.add_node("requirement",    requirement_node)
    workflow.add_node("architecture",   architecture_node)
    workflow.add_node("security",       security_node)
    workflow.add_node("database",       database_node)
    workflow.add_node("infrastructure", infrastructure_node)
    workflow.add_node("review",         review_node)
    workflow.add_node("enhancement",    enhancement_node)

    # ── Entry point: always start with the Supervisor ─────────────────────
    workflow.add_edge(START, "supervisor")

    # ── Supervisor decides what happens next ──────────────────────────────
    workflow.add_conditional_edges(
        "supervisor",
        _route_from_supervisor,
        {
            "requirement":    "requirement",
            "architecture":   "architecture",
            "security":       "security",
            "database":       "database",
            "infrastructure": "infrastructure",
            "review":         "review",
            "enhancement":    "enhancement",
            END:              END,
        },
    )

    # ── After every agent completes, return to the Supervisor ─────────────
    for agent_node in [
        "requirement",
        "architecture",
        "security",
        "database",
        "infrastructure",
        "review",
        "enhancement",
    ]:
        workflow.add_edge(agent_node, "supervisor")

    return workflow.compile()