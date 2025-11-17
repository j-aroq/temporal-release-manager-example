#!/bin/bash

# Quick start script for the Temporal Release Management System
# This opens multiple terminal windows/tabs to run all services

echo "🚀 Starting Temporal Release Management System..."
echo ""
echo "This will open 5 terminal tabs/windows:"
echo "  1. Temporal Server"
echo "  2. Backend API"
echo "  3. Frontend"
echo "  4. Worker"
echo "  5. Test Data Generator"
echo ""

# Check prerequisites
command -v temporal >/dev/null 2>&1 || { echo "❌ Temporal CLI not found. Install with: brew install temporal"; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "❌ Python 3 not found."; exit 1; }
command -v node >/dev/null 2>&1 || { echo "❌ Node.js not found."; exit 1; }

# Check backend .env exists
if [ ! -f "backend/.env" ]; then
    echo "⚠️  backend/.env not found. Creating from example..."
    cp backend/.env.example backend/.env
    JWT_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    echo "JWT_SECRET=$JWT_SECRET" >> backend/.env
    echo "✅ Created backend/.env with generated JWT_SECRET"
fi

# Check frontend .env exists
if [ ! -f "frontend/.env" ]; then
    echo "⚠️  frontend/.env not found. Creating from example..."
    cp frontend/.env.example frontend/.env
    echo "✅ Created frontend/.env"
fi

# Check backend virtual environment
if [ ! -d "backend/venv" ]; then
    echo "⚠️  Backend virtual environment not found. Creating..."
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install -e ".[dev]" > /dev/null 2>&1
    cd ..
    echo "✅ Created backend virtual environment"
fi

# Check frontend dependencies
if [ ! -d "frontend/node_modules" ]; then
    echo "⚠️  Frontend dependencies not installed. Installing..."
    cd frontend
    npm install > /dev/null 2>&1
    cd ..
    echo "✅ Installed frontend dependencies"
fi

echo ""
echo "✅ All prerequisites ready!"
echo ""
echo "📋 MANUAL STEPS (Open 5 terminals):"
echo ""
echo "Terminal 1 - Temporal Server:"
echo "  temporal server start-dev"
echo ""
echo "Terminal 2 - Backend API:"
echo "  cd backend && source venv/bin/activate && uvicorn src.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "Terminal 3 - Frontend:"
echo "  cd frontend && npm start"
echo ""
echo "Terminal 4 - Worker:"
echo "  cd backend && source venv/bin/activate && python worker.py"
echo ""
echo "Terminal 5 - Create Test Data (run after worker is ready):"
echo "  cd backend && source venv/bin/activate && python test_workflows.py"
echo ""
echo "🌐 Access URLs:"
echo "  Frontend: http://localhost:3000"
echo "  Backend API Docs: http://localhost:8000/docs"
echo "  Temporal UI: http://localhost:8080"
echo ""
echo "🔐 Login Credentials:"
echo "  Email: admin@example.com"
echo "  Password: admin123"
echo ""
