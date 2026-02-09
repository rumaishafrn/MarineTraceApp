#!/bin/bash

echo "=================================================="
echo "   MarineTrace - Setup & Installation Script"
echo "=================================================="
echo ""

# Check if we're in the right directory
if [ ! -f "README.md" ]; then
    echo "❌ Error: Please run this script from marine-trace-app directory"
    exit 1
fi

echo "📦 Step 1: Installing Backend Dependencies..."
cd backend
pip install flask flask-cors ultralytics opencv-python pillow numpy pandas --break-system-packages
if [ $? -ne 0 ]; then
    echo "❌ Failed to install backend dependencies"
    exit 1
fi
cd ..

echo ""
echo "📦 Step 2: Installing Frontend Dependencies..."
cd frontend
npm install
if [ $? -ne 0 ]; then
    echo "❌ Failed to install frontend dependencies"
    exit 1
fi
cd ..

echo ""
echo "✅ Installation Complete!"
echo ""
echo "=================================================="
echo "   Next Steps:"
echo "=================================================="
echo ""
echo "1. Add your YOLO model:"
echo "   cp your-model.pt backend/models/best.pt"
echo ""
echo "2. Add tracking images:"
echo "   - Copy takalar_tracking.png to backend/static/"
echo "   - Copy mamuju_tracking.png to backend/static/"
echo ""
echo "3. Start the backend:"
echo "   cd backend"
echo "   python app.py"
echo ""
echo "4. In another terminal, start frontend:"
echo "   cd frontend"
echo "   npm run dev"
echo ""
echo "5. Open browser at: http://localhost:5173"
echo ""
echo "=================================================="
echo "   For more info, check README.md"
echo "=================================================="
