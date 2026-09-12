import uuid
import random

from app.config import OUTPUT_DIR_ORDERS, OUTPUT_DIR_CLAIMS
from app.utils import setup_logging, get_logger
from app.schemas import RequestContract, OrderContract, ClaimContract, GraphState

setup_logging()
logger = get_logger(__name__)

async def validate_request(state: dict) -> dict:
    """
    Note: 
        Проверяет корректность запроса контракта.

    Args:
        state (GraphState): Состояние графа, содержащее данные запроса контракта.

    Returns:
        GraphState: Обновленное состояние графа после проверки корректности запроса.
    """

    try:
        _: RequestContract = state["request"]
        logger.info(f"Request validated")
        return {}
    except Exception as e:
        logger.error(f"Error validating request: {e}")
        return {"error": str(e)}


async def build_order(state: dict) -> dict:
    """
    Note:
        Создает объект заказа на основе данных запроса контракта.

    Args:
        state (dict): Состояние графа, содержащее данные запроса контракта.

    Returns:
        dict: Обновленное состояние графа с созданным объектом заказа.
    """
    req: RequestContract = state["request"]
    contract = OrderContract(
        order_id=str(uuid.uuid4()),
        description=random.choice(["Поставка оборудования", "Разработка ПО", "Монтажные работы"]),
        amount=req.amount,
        urgent=req.urgent,
        approval_needed=req.amount > 1_000_000,
    )
    logger.info(f"Order created: {contract}")
    return {"contract": contract}


async def build_claim(state: dict) -> dict:
    req: RequestContract = state["request"]
    contract = ClaimContract(
        claim_id=str(uuid.uuid4()),
        reasons = random.choice(["Брак товара", "Нарушение сроков", "Неполная комплектация"]),
        compensation=req.amount,
        urgent=req.urgent,
        approval_needed=req.amount > 1_000_000,
    )
    logger.info(f"Claim created: {contract}")
    return {"contract": contract}


async def save_contract(state: dict) -> dict:
    contract = state["contract"]
    prefix = "order" if isinstance(contract, OrderContract) else "claim"
    file_name = f"{prefix}_{contract.order_id if prefix == 'order' else contract.claim_id}.json"
    path = (OUTPUT_DIR_ORDERS if prefix == "order" else OUTPUT_DIR_CLAIMS) / file_name
    path.write_text(contract.model_dump_json(indent=2), encoding="utf-8")
    logger.info(f"Contract saved to {path}")

    return {"file_path": str(path)}

def fallback(state: dict) -> dict:
    logger.error(f"Fallback called with state: {state}")
    return {"error": state.get("error", "unknown")}