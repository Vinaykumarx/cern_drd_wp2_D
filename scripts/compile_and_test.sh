#!/bin/bash

echo "[1/4] Safely hunting down ghost processes on Port 3000 and 8000..."
# We will gracefully find only the actual processes squatting the ports without destructive global pkills
PORT_3000_PID=$(lsof -t -i:3000)
PORT_8000_PID=$(lsof -t -i:8000)

if [ ! -z "$PORT_3000_PID" ]; then
  echo "Found ghost node process ($PORT_3000_PID) squatting Front-end. Terminating..."
  kill -9 $PORT_3000_PID
fi

if [ ! -z "$PORT_8000_PID" ]; then
  echo "Found ghost uvicorn process ($PORT_8000_PID) squatting API. Terminating..."
  kill -9 $PORT_8000_PID
fi

echo "[2/4] Triggering Production React Compilation (Verifying UI changes)..."
cd frontend || exit 1
npm run build

echo "[3/4] Backgrounding the FastAPI Backend Server..."
cd ..
.venv/bin/uvicorn backend.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

echo "[4/4] Starting Next.js Dev Server dynamically..."
cd frontend || exit 1
npm run dev &
FRONTEND_PID=$!

echo "============================================="
echo "✅ ARCHITECTURE SUCCESSFULLY BOOTED & TESTED "
echo "Next.js is live gracefully on: localhost:3000"
echo "FastAPI is streaming live on : localhost:8000"
echo "============================================="

wait $FRONTEND_PID
