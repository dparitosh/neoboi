from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn
import logging
import os
from dotenv import load_dotenv
from contextlib import asynccontextmanager

# Load environment variables from .env.local file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env.local'))

# Configure logging first
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import and include routes
try:
    from .routes.routes import router
    from .routes.unstructured import router as unstructured_router
    from .neo4j_service import get_neo4j_service
    neo4j_service = get_neo4j_service()
    routes_loaded = True
    logger.info("Routes and services imported successfully")
except ImportError as e:
    logger.warning(f"Could not load routes/services: {e}")
    routes_loaded = False
    router = None
    unstructured_router = None
    neo4j_service = None
except Exception as e:
    logger.error(f"Unexpected error loading routes/services: {e}")
    routes_loaded = False
    router = None
    unstructured_router = None
    neo4j_service = None

# Create FastAPI app
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application startup - Neo4j connection deferred")
    yield
    logger.info("Application shutdown")

app = FastAPI(
    title="Neo4j Graph Visualization API",
    description="Python-based API for Neo4j graph visualization",
    version="1.0.0",
    lifespan=lifespan
)

# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'static')
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    logger.info(f"Static files mounted from: {static_dir}")
else:
    logger.warning(f"Static directory not found: {static_dir}")

# Add CORS middleware
cors_origins = os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000,http://localhost:3001,http://127.0.0.1:3001")
cors_origins_list = [origin.strip() for origin in cors_origins.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    favicon_path = os.path.join(static_dir, 'favicon.ico')
    return FileResponse(favicon_path)

# Include API routes
if routes_loaded and router:
    try:
        app.include_router(router, prefix="/api", tags=["api"])
        logger.info("API routes included successfully")
    except Exception as e:
        logger.error(f"Error including API routes: {e}")
        routes_loaded = False

if routes_loaded and unstructured_router:
    try:
        app.include_router(unstructured_router)
        logger.info("Unstructured routes included successfully")
    except Exception as e:
        logger.error(f"Error including unstructured routes: {e}")
else:
    logger.warning("Unstructured routes not included - some functionality may be unavailable")

# Startup and shutdown events
# Removed deprecated on_event handlers, using lifespan instead

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "Backend API Server is running",
        "services": {
            "fastapi": "running",
            "neo4j": "service_not_loaded",
            "routes_loaded": routes_loaded
        }
    }

@app.get("/")
async def root():
    """Serve the main frontend application"""
    return {"message": "Neo4j Graph Visualization API", "status": "running"}

if __name__ == "__main__":
    import os
    port = int(os.getenv("BACKEND_PORT", "3001"))
    logger.info(f"Starting server on port {port}")

    try:
        # Simple server start
        logger.info("About to start uvicorn...")
        uvicorn.run(app, host="127.0.0.1", port=port)
        logger.info("Uvicorn started successfully")
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        import traceback
        traceback.print_exc()