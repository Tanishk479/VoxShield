@echo off
echo ==============================================
echo  VoxShield — Frontend Startup
echo ==============================================
echo.

cd /d "%~dp0frontend"

echo Starting Next.js development server...
echo Frontend: http://localhost:3000
echo.
npm run dev
