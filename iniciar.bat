@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
cd /d "%~dp0"

echo.
echo ===================================================
echo    KanbanAI - Inicio Automatico
echo ===================================================
echo.

:: Verificar Docker
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker no esta corriendo.
    echo Abre Docker Desktop, espera a que cargue y vuelve a ejecutar.
    pause
    exit /b 1
)
echo [OK] Docker esta corriendo.

:: Detectar IP local WiFi (192.168.1.x)
echo.
echo [1/5] Detectando IP local...
set "IP_LOCAL="
for /f "tokens=2 delims=:" %%A in ('ipconfig ^| findstr /i "IPv4"') do (
    set "LINEA=%%A"
    set "LINEA=!LINEA: =!"
    echo !LINEA! | findstr /b "192.168.1." >nul
    if !errorlevel! == 0 (
        if "!IP_LOCAL!"=="" set "IP_LOCAL=!LINEA!"
    )
)

if "!IP_LOCAL!"=="" (
    echo No se detecto IP automaticamente.
    set /p IP_LOCAL="Escribe tu IP local (ej: 192.168.1.7): "
)
echo [OK] IP: !IP_LOCAL!

:: Actualizar frontend/.env
echo.
echo [2/5] Actualizando frontend/.env...
echo VITE_API_URL=http://!IP_LOCAL!:8000/api/v1> frontend\.env
echo [OK] frontend/.env actualizado.

:: Actualizar CORS
echo.
echo [3/5] Actualizando CORS en el backend...
powershell -Command "(Get-Content backend\app\main.py -Raw) -replace 'http://[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+:5173', 'http://!IP_LOCAL!:5173' | Set-Content backend\app\main.py"
echo [OK] CORS actualizado.

:: Levantar Docker
echo.
echo [4/5] Levantando contenedores...
docker-compose down >nul 2>&1
docker-compose up --build -d
if %errorlevel% neq 0 (
    echo [ERROR] Fallo al levantar Docker.
    pause
    exit /b 1
)
echo [OK] Contenedores levantados.

:: Esperar backend
echo.
echo     Esperando que el backend este listo...
set "INTENTOS=0"
:ESPERAR
set /a INTENTOS+=1
if !INTENTOS! gtr 30 (
    echo [ERROR] El backend no respondio a tiempo.
    echo Revisa los logs: docker logs kanbanai_backend
    pause
    exit /b 1
)
timeout /t 10 /nobreak >nul
docker inspect --format="{{.State.Running}}" kanbanai_backend 2>nul | findstr "true" >nul
if %errorlevel% neq 0 goto ESPERAR
echo [OK] Backend listo.

:: Migraciones con ruta absoluta correcta
echo [OK] Migraciones aplicadas automaticamente al arrancar.

:: Resultado
echo.
echo ===================================================
echo   Proyecto listo!
echo.
echo   Tu PC:       http://!IP_LOCAL!:5173
echo   Companeros:  http://!IP_LOCAL!:5173
echo   API Docs:    http://!IP_LOCAL!:8000/docs
echo ===================================================
echo.
pause