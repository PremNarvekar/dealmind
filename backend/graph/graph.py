from langgraph.graph import StateGraph, START, END

from models.state import GraphState
from agents.supervisor import app as supervisor
from graph.checkpoint import checkpointer


def build_graph():

    graph = StateGraph(GraphState)

    graph.add_node("supervisor", supervisor)

    graph.add_edge(START, "supervisor")
    graph.add_edge("supervisor", END)

    return graph.compile(
        checkpointer=checkpointer
    )


app = build_graph()