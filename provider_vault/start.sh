#!/bin/bash

echo "🚀 Starting Provider Vault..."
echo ""

# Check if AI service venv exists
if [ ! -d "apps/ai_service/.venv" ]; then
    echo "❌ AI service virtual environment not found!"
    echo "Please set up the AI service first:"
    echo "  cd apps/ai_service"
    echo "  uv venv"
    echo "  source .venv/bin/activate"
    echo "  uv pip install -e ."
    exit 1
fi

# Start AI service in background
echo "✅ Starting AI Service on port 8000..."
cd apps/ai_service
source .venv/bin/activate
.venv/bin/uvicorn api:app --port 8000 &
AI_PID=$!
cd ../..

# Give AI service time to start
sleep 2

# Start Phoenix
echo "✅ Starting Phoenix Web on port 4000..."
echo ""
cd apps/web
iex -S mix phx.server

# Cleanup when Phoenix stops
echo ""
echo "🛑 Stopping services..."
kill $AI_PID 2>/dev/null
