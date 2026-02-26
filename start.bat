@echo off
chcp 65001 >nul
REM chen-AI test package - one-click start (Windows)

echo.
echo ================================
echo   chen-AI One-Click Start
echo ================================
echo.

cd /d "%~dp0"

python --version >nul 2>&1 || (echo [ERROR] Python3 required && pause && exit /b 1)
node --version >nul 2>&1 || (echo [ERROR] Node.js required && pause && exit /b 1)

if not exist "backend\.env" (
    echo [WARN] backend\.env not found. Run setup.bat first.
    (
        echo SECRET_KEY=test-secret-key-change-in-production
        echo DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/ai_qa_system
        echo DEEPSEEK_API_KEY=your-key
        echo DEBUG=True
        echo ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
    ) > backend\.env
    echo Edit backend\.env with your DB password and API key, then run start.bat again.
    pause
    exit /b 1
)

echo [1/2] Starting backend...
cd backend
if not exist ".venv" (
    python -m venv .venv
)
call .venv\Scripts\activate.bat
pip install -q -r requirements-minimal.txt
python manage.py migrate --noinput
start "chen-AI Backend" cmd /k "python manage.py runserver 0.0.0.0:8000"
cd ..

timeout /t 5 /nobreak >nul

echo [2/2] Starting frontend...
cd frontend
if not exist "node_modules" (
    call npm install
)
start "chen-AI Frontend" cmd /k "npm run dev"
cd ..

echo.
echo ================================
echo [OK] Started!
echo ================================
echo.
echo Frontend: http://localhost:3000
echo Backend:  http://localhost:8000
echo Admin:   http://localhost:8000/admin
echo.
echo Close the backend/frontend windows to stop services.
echo.
pause
