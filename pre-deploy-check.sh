#!/bin/bash

# Pre-deployment checklist script
# Run this before deploying to catch common issues

echo "🚀 Pre-Deployment Checklist"
echo "======================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

ERRORS=0

# Check 1: Git status
echo "📋 Checking Git status..."
if git diff-index --quiet HEAD --; then
    echo -e "${GREEN}✓${NC} No uncommitted changes"
else
    echo -e "${YELLOW}⚠${NC} You have uncommitted changes"
    echo "  Run: git add . && git commit -m 'Your message'"
fi
echo ""

# Check 2: Backend requirements.txt exists
echo "📦 Checking backend dependencies..."
if [ -f "research_assistant/api/requirements.txt" ]; then
    echo -e "${GREEN}✓${NC} requirements.txt found"
else
    echo -e "${RED}✗${NC} requirements.txt missing"
    ERRORS=$((ERRORS + 1))
fi
echo ""

# Check 3: Frontend package.json exists
echo "📦 Checking frontend dependencies..."
if [ -f "kg-viz-frontend/package.json" ]; then
    echo -e "${GREEN}✓${NC} package.json found"
else
    echo -e "${RED}✗${NC} package.json missing"
    ERRORS=$((ERRORS + 1))
fi
echo ""

# Check 4: Environment variables documented
echo "🔐 Checking environment variables..."
if grep -q "NEO4J_URI" research_assistant/.env 2>/dev/null; then
    echo -e "${GREEN}✓${NC} .env file exists with Neo4j credentials"
    echo -e "${YELLOW}⚠${NC} Remember to set these in Render dashboard!"
else
    echo -e "${RED}✗${NC} .env file missing or incomplete"
    ERRORS=$((ERRORS + 1))
fi
echo ""

# Check 5: Verify API can import
echo "🔍 Testing backend imports..."
cd research_assistant
if python -c "from api.main import app" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} Backend imports successfully"
else
    echo -e "${RED}✗${NC} Backend import errors"
    echo "  Run: python -m pip install -r api/requirements.txt"
    ERRORS=$((ERRORS + 1))
fi
cd ..
echo ""

# Check 6: Verify frontend builds
echo "🏗️  Testing frontend build..."
cd kg-viz-frontend
if [ -f "package-lock.json" ] && [ -d "node_modules" ]; then
    echo -e "${GREEN}✓${NC} Dependencies installed"
else
    echo -e "${YELLOW}⚠${NC} Run: npm install"
fi
cd ..
echo ""

# Check 7: Deployment files exist
echo "📄 Checking deployment configuration files..."
if [ -f "research_assistant/api/render.yaml" ]; then
    echo -e "${GREEN}✓${NC} render.yaml exists"
else
    echo -e "${YELLOW}⚠${NC} render.yaml missing (optional)"
fi

if [ -f "kg-viz-frontend/vercel.json" ]; then
    echo -e "${GREEN}✓${NC} vercel.json exists"
else
    echo -e "${YELLOW}⚠${NC} vercel.json missing (optional)"
fi

if [ -f "DEPLOYMENT.md" ]; then
    echo -e "${GREEN}✓${NC} DEPLOYMENT.md guide exists"
else
    echo -e "${RED}✗${NC} DEPLOYMENT.md missing"
fi
echo ""

# Summary
echo "======================================"
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✅ All checks passed! Ready to deploy.${NC}"
    echo ""
    echo "Next steps:"
    echo "1. git push origin main"
    echo "2. Follow DEPLOYMENT.md guide"
else
    echo -e "${RED}❌ Found $ERRORS error(s). Fix them before deploying.${NC}"
fi
echo ""

# Show deployment URLs placeholder
echo "📝 After deployment, your URLs will be:"
echo "  Frontend: https://your-project.vercel.app"
echo "  Backend:  https://ai-education-api.onrender.com"
echo "  API Docs: https://ai-education-api.onrender.com/docs"
echo ""
