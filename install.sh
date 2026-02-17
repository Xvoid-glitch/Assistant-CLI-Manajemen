#!/bin/bash
echo "🚀 Installing RIzzAssistant..."

# Check Python
python3 --version > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "❌ Python3 tidak ditemukan! Install dulu bro"
    exit 1
fi

# Virtual env
echo "📦 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install deps
echo "📚 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Make executable
chmod +x rizz_assistant.py

# Symlink
echo ""
read -p "Buat symlink biar bisa ketik 'rizz'? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    sudo ln -sf "$(pwd)/rizz_assistant.py" /usr/local/bin/rizz
    echo "✅ Siap! Jalankan dengan: rizz"
else
    echo "✅ Siap! Jalankan dengan: ./rizz_assistant.py"
fi