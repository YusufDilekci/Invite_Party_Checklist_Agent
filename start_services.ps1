# PowerShell script to start both FastAPI and Streamlit services

Write-Host "Starting Party Planning Assistant Services..." -ForegroundColor Green
Write-Host ""

# Install FastAPI dependencies
Write-Host "Installing FastAPI dependencies..." -ForegroundColor Yellow
pip install -r requirements-fastapi.txt

Write-Host ""
Write-Host "Starting FastAPI backend on port 8000..." -ForegroundColor Yellow

# Start FastAPI backend in a new PowerShell window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "uvicorn fastapi_backend:app --reload --port 8000"

# Wait a bit for FastAPI to start
Start-Sleep -Seconds 5

Write-Host ""
Write-Host "Starting Streamlit frontend on port 8501..." -ForegroundColor Yellow

# Start Streamlit frontend in a new PowerShell window  
Start-Process powershell -ArgumentList "-NoExit", "-Command", "streamlit run streamlit_fastapi_frontend.py --server.port 8501"

Write-Host ""
Write-Host "Services are starting..." -ForegroundColor Green
Write-Host "FastAPI Backend: http://localhost:8000" -ForegroundColor Cyan
Write-Host "Streamlit Frontend: http://localhost:8501" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
