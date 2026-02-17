# install.ps1
Write-Host "🚀 Installing RIzzAssistant..." -ForegroundColor Green

# Check Python
python --version
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Python tidak ditemukan!" -ForegroundColor Red
    exit 1
}

# Virtual env
Write-Host "📦 Creating virtual environment..." -ForegroundColor Yellow
python -m venv venv
.\venv\Scripts\Activate

# Install deps
Write-Host "📚 Installing dependencies..." -ForegroundColor Yellow
pip install --upgrade pip
pip install -r requirements.txt

Write-Host "✅ Install selesai!" -ForegroundColor Green
Write-Host "Jalankan dengan: .\venv\Scripts\Activate; python rizz_assistant.py" -ForegroundColor Cyan