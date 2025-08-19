"""
FastAPI Application Entry Point

This is the main FastAPI application that serves as the backend for the CUA project.
It provides API endpoints for the Cloudflare AI Gateway integration and MCP orchestration.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app instance
app = FastAPI(
    title="CUA Backend API",
    description="Computer User Assistance Backend with Cloudflare AI Gateway integration",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # Frontend origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_root():
    """Root endpoint for health checking."""
    return {
        "message": "CUA Backend API",
        "status": "running",
        "version": "0.1.0",
        "environment": os.getenv("ENVIRONMENT", "development")
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring and readiness probes."""
    return {
        "status": "healthy",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "debug": os.getenv("DEBUG", "false").lower() == "true"
    }

@app.get("/api/status")
async def api_status():
    """API status endpoint with environment information."""
    return {
        "api": "CUA Backend",
        "status": "operational",
        "features": {
            "cloudflare_ai_gateway": True,
            "mcp_protocol": True,
            "redis_cache": True,
            "vector_search": True
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )