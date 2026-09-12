import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.simulation import simulate_request
from app.graph import graph
from app.schemas import RequestContract, GraphState
from app.utils import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)


async def polling_loop(interval: float = 10.0):
    while True:
        try:
            req = await simulate_request()
            result = await graph.ainvoke({"request": req, "error": None})
            logger.info("tick: %s → %s", req.task_type, result.get("file_path"))
        except Exception as e:
            logger.error("tick failed: %s", e)
        await asyncio.sleep(interval)

@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(polling_loop())
    logger.info("polling started")
    yield
    task.cancel()
    logger.info("polling stopped")


app = FastAPI(title="Graph Service", lifespan=lifespan)

@app.post("/run-graph")
async def run_graph(req: RequestContract):
    result = await graph.ainvoke({"request": req, "error": None})
    return {"file_path": result.get("file_path"), "error": result.get("error")}

@app.get("/health")
async def health():
    return {"status": "ok"}