@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion
REM chen-AI test package - one-click setup (Windows)

echo.
echo ================================
echo   chen-AI One-Click Setup
echo ================================
echo.

cd /d "%~dp0"

python --version >nul 2>&1 || (echo [ERROR] Python3 required. Please install from https://www.python.org/ && pause && exit /b 1)
node --version >nul 2>&1 || (echo [ERROR] Node.js required. Please install from https://nodejs.org/ && pause && exit /b 1)

echo [1/3] Configuring backend .env...
set BACKEND_ENV=backend\.env

if exist "%BACKEND_ENV%" (
    echo [WARN] backend\.env already exists
    set /p OVERWRITE="Overwrite? (y/N): "
    if /i not "!OVERWRITE!"=="y" (
        echo [INFO] Keeping existing config
        goto :skip_env
    )
    del "%BACKEND_ENV%"
)

set /p DB_PASSWORD="PostgreSQL postgres password: "
set /p DB_NAME="Database name [ai_qa_system]: "
set /p DEEPSEEK_KEY="DeepSeek API Key (optional): "

if "%DB_NAME%"=="" set DB_NAME=ai_qa_system

for /f "delims=" %%i in ('python -c "import secrets; print(secrets.token_urlsafe(50))" 2^>nul') do set SECRET_KEY=%%i
if "%SECRET_KEY%"=="" set SECRET_KEY=test-secret-key-change-in-production

(
    echo SECRET_KEY=%SECRET_KEY%
    echo DATABASE_URL=postgresql://postgres:%DB_PASSWORD%@localhost:5432/%DB_NAME%
    echo DEEPSEEK_API_KEY=%DEEPSEEK_KEY%
    echo DEBUG=True
    echo ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
) > "%BACKEND_ENV%"

echo [OK] backend\.env created

:skip_env

echo [2/3] Checking PostgreSQL...
sc query postgresql-x64-14 >nul 2>&1
if errorlevel 1 (
    sc query postgresql-x64-15 >nul 2>&1
    if errorlevel 1 (
        echo [WARN] PostgreSQL service not running
        echo Please: Win+R -^> services.msc -^> find postgresql-x64-14/15 -^> Start
        echo Then run this script again.
        echo.
        pause
        exit /b 1
    )
)
echo [INFO] PostgreSQL is running

echo.
echo Create database: open cmd, run: psql -U postgres
echo Then in psql run:
echo   CREATE DATABASE %DB_NAME%;
echo   \c %DB_NAME%
echo   CREATE EXTENSION IF NOT EXISTS vector;
echo   \q
echo.
set /p DB_CREATED="Database created? (y/N): "
if /i not "%DB_CREATED%"=="y" (
    echo Please create the database first, then run this script again.
    pause
    exit /b 1
)

echo [3/3] Setting up Python env...
cd backend

if not exist ".venv" (
    python -m venv .venv
)

call .venv\Scripts\activate.bat
pip install -q --upgrade pip
pip install -q -r requirements-minimal.txt
python manage.py migrate --noinput

cd ..

echo.
echo ================================
echo [OK] Setup done!
echo ================================
echo.
echo Next: run start.bat to start services
echo.
echo URLs: http://localhost:3000  http://localhost:8000  http://localhost:8000/admin
echo For help see: README or docs
echo.
pause
