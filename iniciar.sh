#!/bin/bash

echo "==================================================="
echo "   Iniciando KanbanAI - Configuración Automática"
echo "==================================================="
echo ""

# 1. Verificar si Docker está corriendo
if ! docker info > /dev/null 2>&1; then
  echo "[ERROR] Docker no está corriendo o no está instalado."
  echo "Por favor, abre Docker Desktop y vuelve a ejecutar este archivo."
  exit 1
fi

# 2. Detectar IP Local
echo "[1/5] Detectando IP Local..."
if command -v ip > /dev/null; then
    IP_LOCAL=$(ip route get 1.2.3.4 | awk '{print $7}')
elif command -v ifconfig > /dev/null; then
    IP_LOCAL=$(ifconfig | grep "inet " | grep -Fv 127.0.0.1 | awk '{print $2}' | head -n 1)
elif command -v ipconfig > /dev/null; then
    IP_LOCAL=$(ipconfig getifaddr en0)
else
    IP_LOCAL="localhost"
fi

if [ -z "$IP_LOCAL" ]; then
    echo "[ERROR] No se pudo detectar la IP. Se usará localhost."
    IP_LOCAL="localhost"
else
    echo "IP Detectada: $IP_LOCAL"
fi

# 3. Actualizar frontend/.env
echo "[2/5] Actualizando frontend/.env..."
echo "VITE_API_URL=http://$IP_LOCAL:8000/api/v1" > frontend/.env

# 4. Actualizar CORS en backend/app/main.py
echo "[3/5] Actualizando CORS en el backend..."
if [[ "$OSTYPE" == "darwin"* ]]; then
  sed -i '' -E "s/\"http:\/\/[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+:5173\"/\"http:\/\/$IP_LOCAL:5173\"/g" backend/app/main.py
else
  sed -i -E "s/\"http:\/\/[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+:5173\"/\"http:\/\/$IP_LOCAL:5173\"/g" backend/app/main.py
fi

# 5. Levantar Docker Compose
echo "[4/5] Levantando contenedores con Docker Compose..."
docker-compose down -v
docker-compose up --build -d

echo "Esperando a que los contenedores estén listos (15 segundos)..."
sleep 15

# 6. Correr migraciones
echo "[5/5] Ejecutando migraciones de base de datos..."
docker exec kanbanai_backend alembic upgrade head

echo ""
echo "==================================================="
echo "✅ Proyecto listo!"
echo "📱 Comparte esta URL con tus compañeros: http://$IP_LOCAL:5173"
echo "🖥️  Panel admin: http://$IP_LOCAL:8000/docs"
echo "==================================================="
