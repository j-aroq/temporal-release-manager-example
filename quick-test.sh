#!/bin/bash

# Quick test script to verify the system is working
# Run this after all services are started

echo "🧪 Quick System Test"
echo "===================="
echo ""

# Test 1: Temporal Server
echo "1️⃣  Testing Temporal Server (http://localhost:8080)..."
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8080 | grep -q "200"; then
    echo "   ✅ Temporal UI accessible"
else
    echo "   ❌ Temporal UI not accessible"
    echo "   Run: temporal server start-dev"
fi
echo ""

# Test 2: Backend Health
echo "2️⃣  Testing Backend API (http://localhost:8000/health)..."
HEALTH_RESPONSE=$(curl -s http://localhost:8000/health)
if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
    echo "   ✅ Backend API healthy"
    echo "   Response: $HEALTH_RESPONSE"
else
    echo "   ❌ Backend API not healthy"
    echo "   Run: cd backend && source venv/bin/activate && uvicorn src.main:app --reload"
fi
echo ""

# Test 3: Backend API Docs
echo "3️⃣  Testing Backend API Docs (http://localhost:8000/docs)..."
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/docs | grep -q "200"; then
    echo "   ✅ API docs accessible"
else
    echo "   ❌ API docs not accessible"
fi
echo ""

# Test 4: Frontend
echo "4️⃣  Testing Frontend (http://localhost:3000)..."
if curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 | grep -q "200"; then
    echo "   ✅ Frontend accessible"
else
    echo "   ❌ Frontend not accessible"
    echo "   Run: cd frontend && npm start"
fi
echo ""

# Test 5: Login API
echo "5️⃣  Testing Login API..."
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8000/api/auth/login \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=admin@example.com&password=admin123")

if echo "$LOGIN_RESPONSE" | grep -q "access_token"; then
    echo "   ✅ Login successful"
    TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
    echo "   Token: ${TOKEN:0:50}..."

    # Test 6: Get Releases with Auth
    echo ""
    echo "6️⃣  Testing Get Releases (authenticated)..."
    RELEASES_RESPONSE=$(curl -s http://localhost:8000/api/releases \
        -H "Authorization: Bearer $TOKEN")

    if echo "$RELEASES_RESPONSE" | grep -q "items"; then
        RELEASE_COUNT=$(echo "$RELEASES_RESPONSE" | grep -o '"id"' | wc -l | tr -d ' ')
        echo "   ✅ Releases API working"
        echo "   Found $RELEASE_COUNT releases"

        if [ "$RELEASE_COUNT" -eq "0" ]; then
            echo ""
            echo "   ⚠️  No releases found. Create test data:"
            echo "      cd backend && source venv/bin/activate && python test_workflows.py"
        fi
    else
        echo "   ❌ Releases API not working"
        echo "   Response: $RELEASES_RESPONSE"
    fi
else
    echo "   ❌ Login failed"
    echo "   Response: $LOGIN_RESPONSE"
fi

echo ""
echo "===================="
echo "📋 Summary"
echo "===================="
echo ""
echo "If all tests passed:"
echo "  ✅ System is ready!"
echo "  🌐 Open: http://localhost:3000"
echo "  🔐 Login: admin@example.com / admin123"
echo ""
echo "If tests failed, check the terminal running each service for errors."
echo ""
