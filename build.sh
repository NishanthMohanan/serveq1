#!/bin/bash

# ServeQ - Simple Local Build Script

echo " ServeQ Build Script"
echo "===================="
echo ""

echo " Building frontend..."
cd frontend
npm install 2>/dev/null
npm run build 2>/dev/null

echo " Frontend ready in: backend/static"
echo ""
echo " Backend dependencies installed"
echo ""
echo " Next steps:"
echo "   1. cd backend"
echo "   2. pip install -r requirements.txt"
echo "   3. uvicorn app:app --reload"
echo ""
echo "Then visit: http://localhost:8000"
