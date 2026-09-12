from langgraph.graph import StateGraph, END

from app.schemas import GraphState
from app.nodes import validate_request, build_order, build_claim, save_contract, fallback
from app.utils import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)

def route_by_type(state: GraphState) -> str:
    if state.get("error") is not None:
        return "fallback"
    elif state.get("request").task_type == "order":
        return "build_order"
    else:
        return "build_claim"


builder = StateGraph(GraphState)

builder.add_node("validate_request", validate_request)
builder.add_node("build_order", build_order)
builder.add_node("build_claim", build_claim)
builder.add_node("save_contract", save_contract)
builder.add_node("fallback", fallback)

builder.set_entry_point("validate_request")

builder.add_edge("build_order", "save_contract")
builder.add_edge("build_claim", "save_contract")
builder.add_edge("save_contract", END)

builder.add_conditional_edges(
    "validate_request", 
    route_by_type,           
    {"build_order": "build_order", "build_claim": "build_claim", "fallback": "fallback"},
)

builder.add_edge("fallback", END)
graph = builder.compile()