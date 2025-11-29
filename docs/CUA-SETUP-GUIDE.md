# CUA (Computer User Assistance) - Setup Guide

This guide provides step-by-step instructions to set up, configure, verify, and audit the CUA interface.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Configuration](#configuration)
4. [Architecture Overview](#architecture-overview)
5. [API Endpoints](#api-endpoints)
6. [Security Audit](#security-audit)
7. [Troubleshooting](#troubleshooting)

## Prerequisites

Before setting up CUA, ensure you have the following installed:

| Component | Required Version | Verification Command |
|-----------|-----------------|---------------------|
| Python | 3.11+ | `python3 --version` |
| Node.js | 22+ | `node --version` |
| pnpm | 8+ | `pnpm --version` |
| Docker (optional) | 24+ | `docker --version` |

## Quick Start

### Option 1: Using Setup Script

```bash
# Run the setup script
chmod +x scripts/cua-setup.sh
./scripts/cua-setup.sh
```

### Option 2: Manual Setup

1. **Clone and configure environment:**

```bash
# Create root .env file
cp .env.example .env

# Create frontend .env.local (recommended: use setup script to ensure correct variables)
./scripts/cua-setup.sh frontend-env
# Alternatively, create frontend/.env.local manually with the following required variables:
# (see CUA Playbook for details)
cat > frontend/.env.local <<EOF
APP_API_URL=
APP_AI_GATEWAY_URL=
APP_MCP_GATEWAY_URL=
APP_QDRANT_URL=
APP_NEO4J_URL=
APP_REDIS_URL=
APP_E2B_ENDPOINT=
SECRET_OPENAI_API_KEY=
SECRET_CF_AI_TOKEN=
EOF
```

2. **Install backend dependencies:**

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. **Install frontend dependencies:**

```bash
cd frontend
pnpm install
```

4. **Start services:**

```bash
# Terminal 1 - Backend
cd backend && source venv/bin/activate
python -m uvicorn main:app --reload --port 8000

# Terminal 2 - Frontend
cd frontend && pnpm dev
```

## Configuration

### Environment Variables

#### Root `.env` File

```env
# Database Passwords
POSTGRES_PASSWORD=<secure_password>
NEO4J_PASSWORD=<secure_password>

# API Keys
SECRET_OPENAI_API_KEY=sk-your-key-here

# Environment
ENVIRONMENT=development
DEBUG=true
CORS_ORIGINS=http://localhost:3000,http://localhost:3010
```

#### Frontend `.env.local` File

```env
# URLs
APP_URL=http://localhost:3010
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_E2B_ENDPOINT=http://localhost:8000/e2b

# Service Mode
NEXT_PUBLIC_SERVICE_MODE=client
NEXT_PUBLIC_IS_DESKTOP_APP=0

# MCP Configuration
MCP_TOOL_TIMEOUT=60000
ENABLE_GITHUB_MCP=true
ENABLE_PLAYWRIGHT_MCP=true
ENABLE_E2B_MCP=true
```

## Architecture Overview

```
CUA Architecture
================

+------------------+     +------------------+     +------------------+
|    Frontend      |     |    Backend       |     |   E2B Sandbox    |
|  (Next.js 15)    |<--->|   (FastAPI)      |<--->|   (Stub/Real)    |
|  Port: 3010      |     |   Port: 8000     |     |   WebSocket      |
+------------------+     +------------------+     +------------------+
        |                        |
        v                        v
+------------------+     +------------------+
|  LobeChat UI     |     | Cloudflare AI    |
|  Components      |     |   Gateway        |
+------------------+     +------------------+
```

### Key Components

1. **Frontend (Next.js 15 + React 19)**
   - LobeChat-based interface
   - MCP tool integration
   - Agent configuration UI
   - Real-time chat interface

2. **Backend (FastAPI)**
   - REST API endpoints
   - E2B session management
   - Cloudflare AI Gateway integration
   - Health monitoring

3. **E2B Desktop Sandbox (Stub)**
   - Session creation/management
   - Command execution
   - File operations
   - Placeholder for real E2B integration

## API Endpoints

### Health & Status

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Root endpoint, API info |
| `/health` | GET | Health check |
| `/api/status` | GET | Feature status |

### E2B Session Management

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/e2b/session` | POST | Create new session |
| `/e2b/session/{id}` | GET | Get session details |
| `/e2b/session/{id}/exec` | POST | Execute command |
| `/e2b/session/{id}/write` | POST | Write file |
| `/e2b/session/{id}/close` | POST | Close session |
| `/e2b/sessions` | GET | List all sessions |

### Example API Usage

```bash
# Create a session
curl -X POST "http://localhost:8000/e2b/session?user_id=user123"

# Execute a command
curl -X POST "http://localhost:8000/e2b/session/{session_id}/exec?command=ls"

# Write a file
curl -X POST "http://localhost:8000/e2b/session/{session_id}/write?path=/tmp/test.txt&content=Hello"

# Close session
curl -X POST "http://localhost:8000/e2b/session/{session_id}/close"
```

## Security Audit

### Completed Security Measures

- [x] All hardcoded secrets removed from docker-compose files
- [x] Environment variables used for all sensitive data
- [x] CORS configured for development origins
- [x] API documentation protected in production
- [x] Pre-commit hooks for secret detection available

### Security Checklist

Before deploying to production:

1. [ ] Replace all placeholder API keys with real keys
2. [ ] Generate strong passwords for database services
3. [ ] Configure proper CORS origins
4. [ ] Enable HTTPS
5. [ ] Set `DEBUG=false`
6. [ ] Configure rate limiting
7. [ ] Enable authentication

### Files Updated for Security

| File | Change |
|------|--------|
| `frontend/docker-compose/local/docker-compose.yml` | Secrets to env vars |
| `frontend/docker-compose/local/logto/docker-compose.yml` | Secrets to env vars |
| `frontend/docker-compose/local/zitadel/docker-compose.yml` | Secrets to env vars |
| `frontend/docker-compose/production/logto/docker-compose.yml` | Secrets to env vars |
| `frontend/docker-compose/production/zitadel/docker-compose.yml` | Secrets to env vars |

## Troubleshooting

### Common Issues

**Backend won't start:**
```bash
# Ensure virtual environment is activated
source backend/venv/bin/activate

# Check if port 8000 is in use
lsof -i :8000
```

**Frontend compilation errors:**
```bash
# Clear Next.js cache
cd frontend
rm -rf .next
pnpm dev
```

**CORS errors:**
- Verify `CORS_ORIGINS` in `.env` includes your frontend URL
- Check that backend is running on port 8000

**API returns 404:**
- Ensure the session ID is valid
- Check if the session has expired (30 min default TTL)

## Access Points

After setup, access the CUA interface at:

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:3010 | CUA Web Interface |
| Backend API | http://localhost:8000 | REST API |
| API Documentation | http://localhost:8000/docs | Swagger UI |
| ReDoc | http://localhost:8000/redoc | ReDoc API Docs |

## Next Steps

1. **Configure AI Provider**: Set your OpenAI/Anthropic API keys in `.env`
2. **Enable MCP Tools**: Configure additional MCP servers for enhanced capabilities
3. **Integrate E2B**: Replace the stub with real E2B sandbox for desktop control
4. **Deploy to Production**: Follow the deployment guide in `docs/ARCHITECTURE.md`
