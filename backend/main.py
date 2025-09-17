from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
import os
from dotenv import load_dotenv

# Load environment variables from .env.local file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env.local'))

# Import and include routes
from routes import router
from neo4j_service import neo4j_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Neo4j Graph Visualization API",
    description="Python-based API for Neo4j graph visualization",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api", tags=["api"])

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    try:
        logger.info("Initializing Neo4j connection...")
        await neo4j_service.initialize_driver()
        logger.info("Neo4j connection initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Neo4j connection: {e}")
        # Don't raise exception here to allow the app to start even if Neo4j is not available

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up services on shutdown"""
    try:
        logger.info("Closing Neo4j connection...")
        await neo4j_service.close_driver()
        logger.info("Neo4j connection closed")
    except Exception as e:
        logger.error(f"Error closing Neo4j connection: {e}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    neo4j_status = "unknown"
    try:
        if neo4j_service.driver:
            neo4j_service.driver.verify_connectivity()
            neo4j_status = "connected"
        else:
            neo4j_status = "disconnected"
    except Exception as e:
        neo4j_status = f"error: {str(e)}"

    return {
        "status": "healthy" if neo4j_status == "connected" else "degraded",
        "message": "Backend API Server is running",
        "services": {
            "fastapi": "running",
            "neo4j": neo4j_status
        }
    }

@app.get("/")
async def root():
    return {"message": "Neo4j Graph Visualization API"}

if __name__ == "__main__":
    import os
    port = int(os.getenv("PORT", 3001))
    logger.info(f"Starting server on port {port}")

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=port,
        reload=False,
        log_level="info"
    )