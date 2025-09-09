@echo off
echo Starting Party Planning Assistant Services...

REM Activate virtual environment
call .venv\Scripts\activate.bat

echo.
echo Starting FastAPI backend on port 8000...
start "FastAPI Backend" cmd /k "cd /d "%~dp0" && call .venv\Scripts\activate.bat && uvicorn ai.api:app --reload --port 8000"

timeout /t 5 /nobreak > nul

echo.
echo Starting Streamlit frontend on port 8501...
start "Streamlit Frontend" cmd /k "cd /d "%~dp0" && call .venv\Scripts\activate.bat && cd frontend && streamlit run streamlit.py --server.port 8501"

echo.
echo Services are starting...
echo FastAPI Backend: http://localhost:8000
echo Streamlit Frontend: http://localhost:8501
echo.
echo Press any key to exit...
pause > nul
