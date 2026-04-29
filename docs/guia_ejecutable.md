# Guía del Ejecutable de Arranque Automático

KanbanAI incluye scripts ejecutables para hacer el despliegue del proyecto automático y transparente, facilitando las demostraciones académicas.

---

## 📋 Requisitos Previos
1. Tener instalado **Docker Desktop** (en Windows/Mac) o **Docker Engine** (en Linux).
2. Tener Docker Desktop **abierto y corriendo** en segundo plano antes de usar el ejecutable.

---

## 🚀 Cómo usar el ejecutable

### En Windows
1. Abre la carpeta del proyecto.
2. Haz **doble clic** sobre el archivo `iniciar.bat`.
3. Se abrirá una ventana de terminal negra mostrando el progreso. Simplemente espera.
4. Al finalizar, la terminal te mostrará dos URLs con la IP local de tu PC para que accedas desde otros dispositivos.

### En Mac / Linux
1. Abre la terminal en la carpeta del proyecto.
2. Dale permisos de ejecución al script (solo la primera vez):
   ```bash
   chmod +x iniciar.sh
   ```
3. Ejecuta el script:
   ```bash
   ./iniciar.sh
   ```

---

## ⚙️ ¿Qué hace el script exactamente? (Paso a paso)

El script automatiza todos los procesos técnicos que normalmente tomarían 10 minutos a mano:

1. **Detecta tu IP:** Identifica dinámicamente tu dirección IP local en la red WiFi.
2. **Reconfigura el Frontend:** Modifica el archivo `frontend/.env` para que el frontend sepa dónde buscar la API.
3. **Reconfigura el Backend (CORS):** Reemplaza automáticamente la IP permitida en el archivo `backend/app/main.py` para permitir peticiones seguras.
4. **Limpia y Levanta Docker:** Corre un `docker-compose down -v` para borrar datos basura antiguos y levanta el sistema limpio con `docker-compose up --build -d` (en segundo plano).
5. **Espera la Base de Datos:** Pausa unos segundos para permitir que PostgreSQL se inicie.
6. **Migraciones:** Ejecuta `alembic upgrade head` dentro del backend para crear las tablas de base de datos actualizadas.

---

## 🛑 Cómo detener el proyecto

Cuando termines tu exposición y quieras apagar el servidor, abre una terminal en la carpeta del proyecto y ejecuta:
```bash
docker-compose down
```

---

## ⚠️ ¿Qué hacer si algo falla?

* **Mensaje: "Docker no está corriendo"**: Abre la aplicación Docker Desktop y espera a que el icono se ponga verde. Luego intenta de nuevo.
* **Se queda pegado descargando cosas**: Es normal la primera vez (puede demorar 3-5 minutos dependiendo del internet).
* **Las URLs no cargan en el celular**: Asegúrate de que el celular esté conectado exactamente al **mismo WiFi** que tu computadora. A veces los antivirus o firewalls de Windows bloquean el puerto 5173; asegúrate de darle "Permitir red privada" si salta una alerta de firewall.
