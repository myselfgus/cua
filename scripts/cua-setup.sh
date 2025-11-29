#!/bin/bash
#
# CUA (Computer User Assistance) - Setup Script
# This script sets up the development environment for the CUA project
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
info() { echo -e "${BLUE}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo ""
echo "==========================================="
echo "  CUA - Computer User Assistance Setup    "
echo "==========================================="
echo ""

# Check prerequisites
info "Checking prerequisites..."

# Check Python
if ! command -v python3 &> /dev/null; then
    error "Python 3 is required but not installed."
fi
if ! python3 -c 'import sys; exit(0 if sys.version_info >= (3, 11) else 1)' 2>/dev/null; then
    error "Python 3.11+ is required. You have $(python3 --version)."
fi
PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
success "Python ${PYTHON_VERSION} found"

# Check Node.js
if ! command -v node &> /dev/null; then
    error "Node.js is required but not installed."
fi
if ! node -e 'process.exit(Number(process.versions.node.split(".")[0]) >= 22 ? 0 : 1)'; then
    error "Node.js 22+ is required. You have $(node --version)."
fi
NODE_VERSION=$(node --version)
success "Node.js ${NODE_VERSION} found"

# Check pnpm
if ! command -v pnpm &> /dev/null; then
    warning "pnpm not found, installing..."
    npm install -g pnpm
fi
PNPM_VERSION=$(pnpm --version)
success "pnpm ${PNPM_VERSION} found"

echo ""
info "Setting up environment files..."

# Create root .env if not exists
if [ ! -f "$PROJECT_ROOT/.env" ]; then
    cat > "$PROJECT_ROOT/.env" << EOF
# CUA Development Environment Variables
POSTGRES_PASSWORD=\$(openssl rand -hex 16)
NEO4J_PASSWORD=\$(openssl rand -hex 16)
SECRET_OPENAI_API_KEY=sk-placeholder-set-your-real-key
ENVIRONMENT=development
DEBUG=true
CORS_ORIGINS=http://localhost:3000,http://localhost:3001,http://localhost:3010
DATABASE_URL=postgresql://cua_user:\\\{POSTGRES_PASSWORD\\\}@localhost:5432/cua_dev
REDIS_URL=redis://localhost:6379
QDRANT_URL=http://localhost:6333
NEO4J_URL=bolt://localhost:7687
EOF
    success "Created .env file"
else
    info ".env file already exists"
fi

# Create frontend .env.local if not exists
if [ ! -f "$PROJECT_ROOT/frontend/.env.local" ]; then
    cat > "$PROJECT_ROOT/frontend/.env.local" << 'EOF'
# CUA Frontend Environment Variables
APP_URL=http://localhost:3010
NEXT_PUBLIC_BASE_PATH=
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_MCP_GATEWAY_URL=http://localhost:8001
NEXT_PUBLIC_QDRANT_URL=http://localhost:6333
NEXT_PUBLIC_NEO4J_URL=bolt://localhost:7687
NEXT_PUBLIC_REDIS_URL=redis://localhost:6379
NEXT_PUBLIC_E2B_ENDPOINT=http://localhost:8000/e2b
NEXT_PUBLIC_SERVICE_MODE=client
NEXT_PUBLIC_IS_DESKTOP_APP=0
NEXT_PUBLIC_ENABLE_NEXT_AUTH=0
NEXTAUTH_URL=http://localhost:3010
NEXTAUTH_SECRET=cua-dev-secret-key-change-in-production
NEXT_PUBLIC_ENABLE_SENTRY=false
MCP_TOOL_TIMEOUT=60000
ENABLE_GITHUB_MCP=true
ENABLE_PLAYWRIGHT_MCP=true
ENABLE_E2B_MCP=true
EOF
    success "Created frontend/.env.local file"
else
    info "frontend/.env.local file already exists"
fi

echo ""
info "Setting up backend virtual environment..."

cd "$PROJECT_ROOT/backend"

# Create virtual environment if not exists
if [ ! -d "venv" ]; then
    python3 -m venv venv
    success "Created Python virtual environment"
else
    info "Virtual environment already exists"
fi

# Activate and install dependencies
source venv/bin/activate
pip install --upgrade pip -q
pip install fastapi uvicorn pydantic python-multipart httpx aiofiles redis structlog prometheus-client -q
success "Installed backend dependencies"

echo ""
info "Setting up frontend dependencies..."

cd "$PROJECT_ROOT/frontend"
pnpm install --silent 2>/dev/null || pnpm install
success "Installed frontend dependencies"

echo ""
echo "==========================================="
echo "  Setup Complete!                         "
echo "==========================================="
echo ""
echo "To start the CUA development environment:"
echo ""
echo "1. Start the backend API:"
echo "   cd backend && source venv/bin/activate && python -m uvicorn main:app --reload --port 8000"
echo ""
echo "2. Start the frontend (in another terminal):"
echo "   cd frontend && pnpm dev"
echo ""
echo "3. Access the CUA interface:"
echo "   - Frontend: http://localhost:3010"
echo "   - Backend API: http://localhost:8000"
echo "   - API Docs: http://localhost:8000/docs"
echo ""
echo "==========================================="
