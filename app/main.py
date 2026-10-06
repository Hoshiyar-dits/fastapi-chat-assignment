import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.authentication.router import router as authentication_router
from app.config.settings import settings
from app.conversation.router import router as conversation_router
from app.core.exception_handlers import register_exception_handlers
from app.database.session import DbSession, close_database
from app.studio.router import router as studio_router
from app.user.router import router as user_router


logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting %s (%s)", settings.app_name, settings.app_env)

    yield

    logger.info("Shutting down %s", settings.app_name)

    await close_database()


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    debug=settings.debug,
    lifespan=lifespan,
)

register_exception_handlers(app)

app.include_router(authentication_router)
app.include_router(user_router)
app.include_router(conversation_router)
app.include_router(studio_router)


@app.get("/health", tags=["Health"])
async def health_check(db: DbSession):
    try:
        await db.execute(text("SELECT 1"))
    except SQLAlchemyError:
        logger.exception("Health check: database unreachable")

        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unavailable",
                "database": "unreachable",
                "environment": settings.app_env,
            },
        )

    return {
        "status": "ok",
        "database": "ok",
        "environment": settings.app_env,
    }
