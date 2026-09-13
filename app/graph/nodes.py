import uuid
import random
import json

from app.config import HISTORY_FILE
from app.utils import setup_logging, get_logger
from app.models.schemas import RequestContract, OrderContract, ClaimContract, GraphState
from app.utils import json_serializer

setup_logging()
logger = get_logger(__name__)

#TODO
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
        req: RequestContract = state["request"] #Короче, тут легче сделать авто-валидацию через Pydantic, 
        # но для демонстрации я оставлю ручную проверку и переход в fallback, если что-то не так
        # в генераторе ответов значения amount могут быть меньше 10_000 или больше 10_000_000, что не допустимо (представим)
        if req.amount < 10_000 or req.amount > 10_000_000:
            raise ValueError(f"Amount {req.amount} is out of bounds (10_000 - 10_000_000)")
        logger.info(f"Request validated")
        return {}
    except Exception as e:
        logger.error(f"Error validating request: {e}")
        return {"error": str(e)}


async def build_order(state: dict) -> dict:
    """
    Note:
        Создает объект заказа.

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
    """
    Note:
        Создает объект претензии.
    Args:
        state (dict): Состояние графа, содержащее данные запроса контракта.
    Returns:
        dict: Обновленное состояние графа с созданным объектом претензии.
    """
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


async def save_logs(state: dict) -> dict:
    """
    Note:
        Сохраняет логи.
    Args:
        state (dict): Состояние графа, содержащее данные запроса.
    Returns:
        dict: Обновленное состояние графа. ### фактически нихуя не меняет, можно добваить file_psth в контракт, если надо будет 
    """
    with HISTORY_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(state, default=json_serializer, ensure_ascii=False) + "\n")
    return {}

def fallback(state: dict) -> dict:
    """
    Note:
        Обрабатывает ошибку - по факту просто нода, куда можно при ошибке добавить логику уведомления, отката и т.д.
    Args:   
        state (dict): Состояние графа, содержащее данные запроса контракта и информацию об ошибке.
    Returns:
        dict: {}
    """
    logger.error(f"Fallback called with state: {state}")
    return {}