from app.agents.requirement_agent import RequirementAgent
from app.agents.architecture_agent import ArchitectureAgent
from app.agents.review_agent import ReviewAgent
from app.agents.enhancement_agent import EnhancementAgent

requirement_agent = RequirementAgent()
architecture_agent = ArchitectureAgent()
review_agent = ReviewAgent()
enhancement_agent = EnhancementAgent()

async def requirement_node(graph_state):
    result = await requirement_agent.execute(graph_state["state"])
    graph_state["state"] = result
    return graph_state

async def architecture_node(graph_state):
    result = await architecture_agent.execute(graph_state["state"])
    graph_state["state"] = result
    return graph_state

async def review_node(graph_state):
    result = await review_agent.execute(graph_state["state"])
    graph_state["state"] = result
    return graph_state

async def enhancement_node(graph_state):
    result = await enhancement_agent.execute(graph_state["state"])
    graph_state["state"] = result
    return graph_state