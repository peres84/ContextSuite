"""LangGraph workflow definition for the Context Agent."""

from __future__ import annotations

from langgraph.graph import END, StateGraph

from contextsuite_agent.workflow.nodes.approve import approve
from contextsuite_agent.workflow.nodes.classify import classify
from contextsuite_agent.workflow.nodes.dispatch import dispatch
from contextsuite_agent.workflow.nodes.intake import intake
from contextsuite_agent.workflow.nodes.package import package
from contextsuite_agent.workflow.nodes.plan import plan
from contextsuite_agent.workflow.nodes.retrieve import retrieve
from contextsuite_agent.workflow.state import AgentState


def should_dispatch(state: AgentState) -> str:
    """Decide whether to proceed to packaging or end early."""
    approval = state.get("approval")
    if approval and approval.approved:
        return "package"
    return "end"


def build_graph() -> StateGraph:
    """Build and compile the Context Agent workflow graph.

    Pipeline: intake → retrieve → plan → classify → approve → (package → dispatch | end)
    """
    graph = StateGraph(AgentState)

    # Add nodes
    graph.add_node("intake", intake)
    graph.add_node("retrieve", retrieve)
    graph.add_node("plan", plan)
    graph.add_node("classify", classify)
    graph.add_node("approve", approve)
    graph.add_node("package", package)
    graph.add_node("dispatch", dispatch)

    # Linear flow through the pipeline
    graph.set_entry_point("intake")
    graph.add_edge("intake", "retrieve")
    graph.add_edge("retrieve", "plan")
    graph.add_edge("plan", "classify")
    graph.add_edge("classify", "approve")

    # Conditional: approved → package → dispatch, rejected → end
    graph.add_conditional_edges("approve", should_dispatch, {
        "package": "package",
        "end": END,
    })
    graph.add_edge("package", "dispatch")
    graph.add_edge("dispatch", END)

    return graph.compile()


# Singleton compiled graph
workflow = build_graph()
