#!/bin/bash
set -e

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║           PHISHLAB PRO - SETUP                            ║"
echo "╚═══════════════════════════════════════════════════════════╝"

echo "📦 Installing system dependencies..."
sudo apt update && sudo apt install -y python3 python3-pip python3-venv

echo "🐍 Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo "📚 Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

echo "🔑 Setting up environment..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env file - EDIT IT with your API keys!"
    nano .env
fi

echo "🗄️  Initializing database..."
python3 -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all(); print('✅ Database initialized!')"

echo ""
echo "✅ SETUP COMPLETE!"
echo ""
echo "To start: python3 run.py"
echo "First time: Go to http://localhost:5000/auth/register"
