#!/bin/bash

echo "--- [1/3] Hunting project ghost processes... ---"
# Kill all local dev processes
pkill -f "uvicorn"
pkill -f "next-dev"
pkill -f "node" 
pkill -f "scripts/compile_and_test.sh"

# In case they are stubborn, find by port and kill
PORT_8000=$(lsof -t -i:8000)
if [ ! -z "$PORT_8000" ]; then
    echo "Killing remaining uvicorn on :8000..."
    kill -9 $PORT_8000
fi

PORT_3000=$(lsof -t -i:3000)
if [ ! -z "$PORT_3000" ]; then
    echo "Killing remaining node on :3000..."
    kill -9 $PORT_3000
fi

echo "--- [2/3] Cleaning up temporary socket artifacts... ---"
# This clears out the uvicorn socket files if any
find . -name "*.sock" -delete

echo "--- [3/3] System Health Check ---"
ps aux | grep -p "uvicorn\|next-dev" | grep -v grep
echo "Current open file count: $(lsof | wc -l)"
echo "Current socket backlog (CLOSE_WAIT): $(ss -tunp | grep CLOSE_WAIT | wc -l)"

echo "DONE. Resources have been flushed. Ready to restart cleanly."
