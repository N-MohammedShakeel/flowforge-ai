# app/graph/workflow.py
from langgraph.graph import StateGraph, START, END
from app.graph.state import GraphState
from app.graph.nodes import (
    requirement_node,
    architecture_node,
    review_node,
    enhancement_node
)

def create_flowforge_graph():
    workflow = StateGraph(GraphState)

    workflow.add_node("requirement", requirement_node)
    workflow.add_node("architecture", architecture_node)
    workflow.add_node("review", review_node)
    workflow.add_node("enhancement", enhancement_node)

    # Basic edges
    workflow.add_edge(START, "requirement")
    workflow.add_edge("requirement", "architecture")

    # Conditional routing
    def should_continue(graph_state):
        workflow_type = graph_state.get("workflow_type", "")
        if workflow_type == "GENERATE_ARCHITECTURE_WITH_REVIEW":
            return "review"
        elif workflow_type in ["GENERATE_ARCHITECTURE_WITH_ENHANCEMENT", "FULL"]:
            return "review"
        else:
            return END

    def should_enhance(graph_state):
        workflow_type = graph_state.get("workflow_type", "")
        if workflow_type in ["GENERATE_ARCHITECTURE_WITH_ENHANCEMENT", "FULL"]:
            return "enhancement"
        else:
            return END

    workflow.add_conditional_edges(
        "architecture",
        should_continue,
        {"review": "review", END: END}
    )

    workflow.add_conditional_edges(
        "review",
        should_enhance,
        {"enhancement": "enhancement", END: END}
    )

    workflow.add_edge("enhancement", END)

    return workflow.compile()