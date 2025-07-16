# zaproxyMCP

## Pasos para utilizar el backend

1. **Clona el repositorio** (si aún no lo has hecho):
   ```sh
   git clone <URL_DEL_REPOSITORIO>
   cd DAST-MCP
   ```

2. **Crea un entorno virtual (venv):**
   ```sh
   python -m venv venv
   ```

3. **Activa el entorno virtual:**
   - En Windows PowerShell:
     ```sh
     .\venv\Scripts\Activate.ps1
     ```
   - En Windows CMD:
     ```sh
     .\venv\Scripts\activate.bat
     ```
   - En Linux/Mac:
     ```sh
     source venv/bin/activate
     ```

4. **Instala los requerimientos:**
   ```sh
   pip install -r requirements.txt
   ```

5. **Configura las variables de entorno:**
   Crea un archivo `.env` en la carpeta `backend/` con el siguiente contenido (reemplaza los valores por los de tu cuenta de Latitude y otros servicios):
   ```env
   LATITUDE_API_KEY=tu_api_key_de_latitude
   LATITUDE_PROJECT_ID=tu_project_id_de_latitude
   ZAP_API_KEY=tu_api_key_de_zap
   LOG_FILE_PATH=logs.txt
   ZAP_PROXY=http://localhost:8080
   ```
   - **LATITUDE_PROJECT_ID**: Es el identificador de tu proyecto en Latitude. Es obligatorio para que el SDK funcione correctamente.

6. **Ejecuta el backend:**
   ```sh
   cd backend
   uvicorn main:app --reload
   ```

Esto pondrá en marcha el servidor en `http://localhost:8000`.

---

¿Tienes dudas o necesitas ayuda adicional? ¡No dudes en preguntar!