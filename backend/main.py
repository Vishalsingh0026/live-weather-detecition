import logging
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
import structlog

from backend.config import settings
from backend.database import init_db, close_db, get_db
from backend.services import data_processor

# Configure logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logging.basicConfig(
    format="%(message)s",
    level=getattr(logging, settings.log_level),
)

logger = logging.getLogger(__name__)


# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"Client connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(
            f"Client disconnected. Total connections: {len(self.active_connections)}"
        )

    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients."""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to connection: {e}")
                disconnected.append(connection)

        # Remove disconnected clients
        for connection in disconnected:
            self.active_connections.remove(connection)


manager = ConnectionManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown."""
    # Startup
    logger.info(f"Starting {settings.app_name} v1.0.0")
    await init_db()
    await data_processor.start()
    yield

    # Shutdown
    logger.info(f"Shutting down {settings.app_name}")
    await close_db()
    await data_processor.stop()


# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Real-time disaster detection and AI response platform",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add GZIP compression
app.add_middleware(GZipMiddleware, minimum_size=1000)


# Health check endpoint
@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "environment": settings.app_env,
        "version": "1.0.0",
    }


# WebSocket endpoint for real-time updates
@app.websocket("/api/ws/events")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time disaster event streaming."""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            logger.info(f"Received WebSocket message: {data}")
            # Echo back for now; will be enhanced with real data
            await websocket.send_json(
                {"type": "message_received", "data": data, "status": "ok"}
            )
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


# Import and include routers
try:
    from backend.api.events import router as events_router
    from backend.api.alerts import router as alerts_router
    from backend.api.response_plans import router as plans_router
    from backend.api.data_feeds import router as feeds_router

    app.include_router(events_router, prefix="/api/events", tags=["events"])
    app.include_router(alerts_router, prefix="/api/alerts", tags=["alerts"])
    app.include_router(plans_router, prefix="/api/response-plans", tags=["response_plans"])
    app.include_router(feeds_router, prefix="/api/data-feeds", tags=["data_feeds"])
except ImportError as e:
    logger.warning(f"Could not import routers: {e}. Routes will be added later.")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.main:app",
        host=settings.host,
        port=settings.port,
        workers=settings.workers,
        reload=settings.reload,
    )
