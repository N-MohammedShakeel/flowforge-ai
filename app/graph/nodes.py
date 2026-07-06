# app/graph/nodes.py
from app.agents.requirement_agent import RequirementAgent
from app.agents.architecture_agent import ArchitectureAgent
from app.agents.review_agent import ReviewAgent
from app.agents.enhancement_agent import EnhancementAgent
from app.agents.supervisor_agent import SupervisorAgent
from app.agents.security_agent import SecurityAgent
from app.agents.infrastructure_agent import InfrastructureAgent
from app.agents.database_agent import DatabaseAgent

requirement_agent   = RequirementAgent()
architecture_agent  = ArchitectureAgent()
review_agent        = ReviewAgent()
enhancement_agent   = EnhancementAgent()
supervisor_agent    = SupervisorAgent()
security_agent      = SecurityAgent()
infrastructure_agent = InfrastructureAgent()
database_agent      = DatabaseAgent()


async def supervisor_node(graph_state):
    result = await supervisor_agent.execute(graph_state["state"])
    graph_state["state"] = result
    return graph_state

async def requirement_node(graph_state):
    result = await requirement_agent.execute(graph_state["state"])
    graph_state["state"] = result
    return graph_state

async def architecture_node(graph_state):
    result = await architecture_agent.execute(graph_state["state"])
    graph_state["state"] = result
    return graph_state

async def security_node(graph_state):
    result = await security_agent.execute(graph_state["state"])
    graph_state["state"] = result
    return graph_state

async def database_node(graph_state):
    result = await database_agent.execute(graph_state["state"])
    graph_state["state"] = result
    return graph_state

async def infrastructure_node(graph_state):
    result = await infrastructure_agent.execute(graph_state["state"])
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