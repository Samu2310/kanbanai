# 🚀 Guía de Despliegue en Red Local (LAN)

Esta guía explica cómo ejecutar KanbanAI para que sea accesible desde cualquier computadora o teléfono móvil conectado a tu misma red WiFi (ideal para exposiciones académicas).

---

## 1️⃣ Encuentra tu IP Local

Debes averiguar la dirección IP de la computadora donde ejecutarás el proyecto.

* **En Windows:**
  1. Abre la consola (`cmd` o PowerShell).
  2. Escribe `ipconfig` y presiona Enter.
  3. Busca "Dirección IPv4" (ej. `192.168.1.7`).
* **En Mac:**
  1. Abre la Terminal.
  2. Escribe `ipconfig getifaddr en0` (o `en1`).
* **En Linux:**
  1. Escribe `hostname -I` o `ip a`.

---

## 2️⃣ Archivos a modificar

Una vez que tengas tu IP (ej. `192.168.1.7`), debes modificar solo **dos archivos** para que todo el proyecto se comunique a través de esa red:

### A. `frontend/.env`
Abre este archivo y cambia la IP de `localhost` por tu IP local:
```env
VITE_API_URL=http://192.168.1.7:8000/api/v1
```

### B. `backend/app/main.py`
Abre este archivo, busca la sección de CORS (cerca de la línea 21) y asegúrate de que tu IP esté en la lista `allow_origins`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://192.168.1.7:5173",  # <-- TU IP AQUÍ
    ],
    ...
```

---

## 3️⃣ Comandos de Despliegue

Abre una terminal en la carpeta **raíz** del proyecto y ejecuta estos comandos en orden:

1. **Limpiar despliegues anteriores (opcional pero recomendado):**
   ```bash
   docker-compose down -v
   ```

2. **Levantar los servicios:**
   ```bash
   docker-compose up --build
   ```
   *(Este comando descargará imágenes, instalará dependencias de Python/Node y levantará la BD, el backend y el frontend. La terminal se quedará corriendo mostrando logs).*

3. **Aplicar Migraciones (En una nueva pestaña de terminal):**
   ```bash
   docker exec kanbanai_backend alembic upgrade head
   ```

---

## 4️⃣ Cómo acceder a la aplicación

* **Desde la misma PC (Host):**
  * Aplicación Web: `http://localhost:5173` o `http://tu-ip:5173`
  * Documentación API (Swagger): `http://localhost:8000/docs`

* **Desde un celular u otra PC en la misma red WiFi:**
  * Aplicación Web: `http://tu-ip:5173` (ej. `http://192.168.1.7:5173`)

---

## 🧰 Solución de Problemas (Troubleshooting)

* ❌ **Error: "Failed to fetch" o "Network Error" en el frontend:**
  * **Causa:** El frontend no encuentra el backend.
  * **Solución:** Verifica que el `frontend/.env` tiene la IP correcta y que reiniciaste el contenedor del frontend si hiciste el cambio después de hacer `docker-compose up`.
* ❌ **Error: "CORS policy" en la consola del navegador:**
  * **Causa:** El backend bloquea la petición por seguridad.
  * **Solución:** Asegúrate de haber puesto tu IP (con el puerto `:5173`) en el arreglo `allow_origins` de `backend/app/main.py`.
* ❌ **Error 500 al crear proyectos o "relation does not exist":**
  * **Causa:** La base de datos no tiene las tablas creadas.
  * **Solución:** Ejecuta el comando de migraciones del paso 3 (`alembic upgrade head`).
* ❌ **Error FATAL: database "kanbanai" does not exist en logs de DB:**
  * **Causa:** Suele ser el healthcheck. Esto ya fue parcheado, pero si ocurre, asegúrate de que el healthcheck del `docker-compose.yml` usa la bandera `-d kanbanai_db`.
