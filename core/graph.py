
from langgraph.graph import StateGraph, END
from core.state import ChatState
from core.nodes import planner, manager, stage_nodes, aggregator

graph = StateGraph(ChatState)
graph.add_node("planner", planner)
graph.add_node("manager", manager)
for i, node in stage_nodes.items():
    graph.add_node(f"stage_{i}", node)
graph.add_node("aggregator", aggregator)

# 连线
graph.set_entry_point("planner")
graph.add_edge("planner", "manager")

def route_manager(state: ChatState) -> str:
    return ("planner" if state["manager_decision"] == "reject"
            else f"stage_{state['classification_result']}")

graph.add_conditional_edges(
    "manager", route_manager,
    {**{f"stage_{i}": f"stage_{i}" for i in range(1, 7)},
     "planner": "planner"}
)

for i in range(1, 7):
    graph.add_edge(f"stage_{i}", "aggregator")
graph.add_edge("aggregator", END)

workflow = graph.compile()
