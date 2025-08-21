#!/bin/bash

echo "🚀 Starting LexiOps Copilot AI Agent (GPT-4 Turbo)..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp .env.example .env
    echo "📝 Please edit .env and add your OPENAI_API_KEY"
    echo "   Then run this script again."
    exit 1
fi

# Check for OpenAI API key
if ! grep -q "OPENAI_API_KEY=sk-" .env 2>/dev/null; then
    echo "⚠️  Please set your OPENAI_API_KEY in .env file"
    echo "📝 Edit .env and replace 'your_openai_api_key_here' with your actual API key"
    exit 1
fi

# Install dependencies if needed
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Check if uvicorn is available
if ! command -v uvicorn &> /dev/null; then
    echo "📦 Installing uvicorn..."
    pip install uvicorn
fi

echo "🧠 AI Model: GPT-4 Turbo (gpt-4-1106-preview)"
echo "🌐 Starting server on http://localhost:8000"
echo "📚 API docs available at http://localhost:8000/docs"

# Start the server
uvicorn agent.main:app --host 0.0.0.0 --port 8000 --reload

echo "✅ Agent is ready! Try:"
echo "curl -X POST http://localhost:8000/chat -H 'Content-Type: application/json' -d '{\"message\": \"What time is it and what can you do?\"}'"
echo ""
echo "Or run: python test_ai_agent.py"
