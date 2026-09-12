import uuid
import random 
import datetime

from app.schemas import RequestContract
from app.utils import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)

async def simulate_request() -> RequestContract:
    """
    Note: 
        Создает случайный ответ на запрос по контракту.

    Returns:
        RequestContract: Случайный объект запроса контракта
    """
    return RequestContract(
        request_id=uuid.uuid4().hex,
        task_type=random.choice(["order", "claim"]),
        amount=random.uniform(10_000, 12_000_000),
        urgent=random.choice([True, False]),
        created_at=datetime.datetime.now(datetime.timezone.utc)
    )