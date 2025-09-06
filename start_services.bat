@echo off
echo Starting Party Planning Assistant Services...
echo.

echo Installing FastAPI dependencies...
pip install -r requirements-fastapi.txt

echo.
echo Starting FastAPI backend on port 8000...
start "FastAPI Backend" cmd /k "uvicorn fastapi_backend:app --reload --port 8000"

timeout /t 5 /nobreak > nul

echo.
echo Starting Streamlit frontend on port 8501...
start "Streamlit Frontend" cmd /k "streamlit run streamlit_fastapi_frontend.py --server.port 8501"

echo.
echo Services are starting...
echo FastAPI Backend: http://localhost:8000
echo Streamlit Frontend: http://localhost:8501
echo.
echo Press any key to exit...
pause > nul
