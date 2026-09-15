@echo off
echo ==============================================
echo  VoxShield — Backend Startup
echo ==============================================
echo.

cd /d "%~dp0backend"

echo [1/3] Checking Python environment...
python -c "import fastapi; print('FastAPI OK')" 2>nul || (echo FastAPI not installed. Run: pip install -r requirements.txt && exit /b 1)

echo [2/3] Seeding demo data (if needed)...
python -m db.seed_demo

echo [3/3] Starting VoxShield API server...
echo.
echo Backend: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo Health:   http://localhost:8000/api/health
echo.
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
