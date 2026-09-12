from langgraph.graph import StateGraph, END
import asyncio

from app.schemas import GraphState
from app.nodes import validate_request, build_order, build_claim, save_contract, fallback
from app.simulation import simulate_request
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




async def main():
    req = await simulate_request()
    logger.info(f"Заявка: {req.task_type}, {req.amount}₽, срочная={req.urgent}")

    state: dict = {"request": req}
    result = await graph.ainvoke(state)

    logger.info(f"Результат: {result}")
    logger.info(f"Ошибка: {result.get('error')}")
    logger.info(f"Файл: {result.get('file_path')}")
    contract = result.get("contract")
    
    if contract:
        logger.info(f"Контракт: {contract.model_dump_json(indent=2)}")


if __name__ == "__main__":
    asyncio.run(main())
