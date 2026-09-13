import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
import time

from app.service.simulation import simulate_request
from app.graph.graph import graph
from app.models.schemas import RequestContract, GraphState
from app.utils import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)

async def polling_loop(interval: float = 10.0):
    """
    Note:
        Асинхронная функция для периодической проверки состояния графа.
    Args:
        interval (float): Интервал между проверками в секундах (по умолчанию 10.0).
    """
    while True:
        try:
            req = await simulate_request()
            result = await run_graph(req= req, error=None)
            logger.info("tick: %s, elapsed: %sms", req.task_type, result.get("elapsed_ms"))
        except Exception as e:
            logger.error(f"tick failed: {e}")
        await asyncio.sleep(interval)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Note:
        Контекстный менеджер для управления жизненным циклом приложения FastAPI.
        Запускает асинхронный цикл опроса при старте приложения и останавливает его при завершении.
    """
    task = asyncio.create_task(polling_loop())
    logger.info("polling started")
    yield
    task.cancel()
    logger.info("polling stopped")


app = FastAPI(title="Graph Service", lifespan=lifespan)

@app.post("/run-graph")
async def run_graph(req: RequestContract):
    """
    Note:
        Обрабатывает POST-запрос для запуска графа с предоставленным объектом запроса контракта.
    """
    result = await run_graph(req= req, error=None)
    logger.info("run_graph: %s -> %s", req.task_type, result)
    return {"file_path": result.get("file_path"), "error": result.get("error")}

@app.get("/health")
async def health():#Бля, а точно тут надо писать докстринг?
    """ 
    Note:
        Проверяет состояние сервиса и возвращает статус "ok".
    Returns:
        dict: Словарь с ключом "status" и значением "ok".
    """
    return {"status": "ok"}


async def run_graph(req: dict, error: str|None) -> dict: ### В идеале создавать отдельный класс для работы с графом, чтобы не дублировать код
    #поэтому я хз куда кидать этот метод, пусть будет тут, наверное оно должно быть в graph.py (там и класс графа создать)
    """
    Note:
        Запускает граф с предоставленным состоянием и возвращает результат.
    Args:
        req (dict): Запрос для запуска графа.
        error (str | None): Ошибка, если она есть.
    Returns:
        dict: Результат запуска графа.
    """
    t0 = time.perf_counter()

    result = await graph.ainvoke({"request": req, "error": error})

    elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)

    logger.info("graph.ainvoke: %sms", elapsed_ms)
    result["elapsed_ms"] = elapsed_ms
    return result