#!/bin/bash
# Driver for Gram meal tracker development environment
# Starts both backend (FastAPI on :8000) and frontend (Vite on :5173)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
cd "$PROJECT_ROOT"

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Commands available to agents
case "${1:-start}" in
  start)
    echo -e "${GREEN}Setting up Gram development environment...${NC}"

    # Set up Python venv if needed
    if [ ! -d .venv ]; then
      echo "Creating Python venv..."
      python3 -m venv .venv
    fi

    # Install backend dependencies
    echo "Installing backend dependencies..."
    ./.venv/bin/pip install -q -r backend/requirements.txt 2>/dev/null || \
      ./.venv/bin/pip install -q -r backend/requirements.txt

    # Install frontend dependencies
    echo "Installing frontend dependencies..."
    cd frontend
    npm install -q 2>/dev/null || true
    cd ..

    # Start backend
    echo "Starting backend on :8000..."
    ./.venv/bin/uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000 > /tmp/gram-backend.log 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > /tmp/gram-backend.pid

    # Wait for backend to be ready
    for i in {1..30}; do
      if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
        echo -e "${GREEN}Backend ready${NC}"
        break
      fi
      if [ $i -eq 30 ]; then
        echo -e "${RED}Backend failed to start${NC}"
        kill $BACKEND_PID 2>/dev/null || true
        exit 1
      fi
      sleep 0.5
    done

    # Start frontend
    echo "Starting frontend on :5173..."
    cd frontend
    npm run dev > /tmp/gram-frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > /tmp/gram-frontend.pid
    cd ..

    # Wait for frontend to be ready
    for i in {1..30}; do
      if curl -s http://localhost:5173/ > /dev/null 2>&1; then
        echo -e "${GREEN}Frontend ready${NC}"
        break
      fi
      if [ $i -eq 30 ]; then
        echo -e "${RED}Frontend failed to start${NC}"
        kill $FRONTEND_PID 2>/dev/null || true
        exit 1
      fi
      sleep 0.5
    done

    echo ""
    echo -e "${GREEN}✓ Gram running!${NC}"
    echo "  Frontend: http://localhost:5173/"
    echo "  Backend:  http://localhost:8000/"
    echo "  API docs: http://localhost:8000/docs"
    echo ""
    echo "Logs:"
    echo "  Backend: tail -f /tmp/gram-backend.log"
    echo "  Frontend: tail -f /tmp/gram-frontend.log"
    echo ""
    echo "To stop, use: $0 stop"
    ;;

  stop)
    echo "Stopping Gram..."
    kill $(cat /tmp/gram-backend.pid 2>/dev/null) 2>/dev/null || true
    kill $(cat /tmp/gram-frontend.pid 2>/dev/null) 2>/dev/null || true
    rm -f /tmp/gram-backend.pid /tmp/gram-frontend.pid
    echo -e "${GREEN}Stopped${NC}"
    ;;

  status)
    if curl -s http://localhost:8000/api/health > /dev/null 2>&1 && \
       curl -s http://localhost:5173/ > /dev/null 2>&1; then
      echo -e "${GREEN}✓ Both servers running${NC}"
      exit 0
    else
      echo -e "${RED}✗ Not all servers running${NC}"
      exit 1
    fi
    ;;

  *)
    echo "Usage: $0 {start|stop|status}"
    exit 1
    ;;
esac
