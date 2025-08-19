"""
FastAPI Application Entry Point

This is the main FastAPI application that serves as the backend for the CUA project.
It provides API endpoints for the Cloudflare AI Gateway integration and MCP orchestration.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from app.core import e2b_stub
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

# ---------------------- E2B STUB ENDPOINTS ----------------------
@app.post("/e2b/session")
async def e2b_create_session(user_id: str | None = None):
    """Create a stub E2B desktop session (placeholder)."""
    sess = e2b_stub.create_session(user_id=user_id)
    return {"session": sess}


@app.get("/e2b/session/{session_id}")
async def e2b_get_session(session_id: str):
    try:
        sess = e2b_stub.get_session(session_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="session_not_found")
    return {"session": sess}


@app.post("/e2b/session/{session_id}/exec")
async def e2b_exec(session_id: str, command: str):
    try:
        result = e2b_stub.exec_command(session_id, command)
    except KeyError:
        raise HTTPException(status_code=404, detail="session_not_found")
    return result


@app.post("/e2b/session/{session_id}/write")
async def e2b_write(session_id: str, path: str, content: str):
    try:
        result = e2b_stub.write_file(session_id, path, content)
    except KeyError:
        raise HTTPException(status_code=404, detail="session_not_found")
    return result


@app.post("/e2b/session/{session_id}/close")
async def e2b_close(session_id: str):
    try:
        result = e2b_stub.close_session(session_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="session_not_found")
    return result


@app.get("/e2b/sessions")
async def e2b_list_sessions():
    return e2b_stub.list_sessions()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )