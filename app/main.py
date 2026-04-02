import logging
from contextlib import asynccontextmanager

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import health, leads

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

# Global scheduler instance — shared with routers via app.state
scheduler = BackgroundScheduler(timezone="UTC")


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.start()
    app.state.scheduler = scheduler
    logger.info("Lead Automation API starting up... Scheduler started.")
    yield
    scheduler.shutdown(wait=False)
    logger.info("Lead Automation API shutting down... Scheduler stopped.")


app = FastAPI(
    title="Lead Automation API",
    description="Lead capture, qualification, and follow-up automation system.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(leads.router)
