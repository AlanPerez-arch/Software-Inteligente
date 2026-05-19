# Software Inteligente

Este proyecto es una aplicación web en Flask que genera planes de negocio, marketing y finanzas usando un motor de IA.

## Requisitos

- Python 3.11+ (se recomienda usar un entorno virtual)
- PostgreSQL configurado y accesible
- Archivo `.env` con las variables de entorno necesarias

## Instalación

1. Activar el entorno virtual:
   - PowerShell:
     ```powershell
     .\venve\Scripts\Activate.ps1
     ```
   - CMD:
     ```cmd
     .\venve\Scripts\activate.bat
     ```

2. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

3. Crear el archivo `.env` con los valores de conexión y la clave de la API:
   ```env
   DB_HOST=localhost
   DB_NAME=tu_base_de_datos
   DB_USER=tu_usuario
   DB_PASSWORD=tu_contraseña
   DB_PORT=5432
   GROQ_API_KEY=tu_api_key
   FLASK_DEBUG=true
   ```

## Ejecución

```bash
python app.py
```

Luego abrir `http://127.0.0.1:5000` en el navegador.

## Rutas principales

- `/` - Login
- `/formulario` - Formulario para enviar la información del proyecto y recibir respuestas de IA
- `/historial` - Historial de proyectos
- `/test-db` - Prueba de conexión a PostgreSQL
- `/registro` - API para registrar usuarios
- `/login` - API para iniciar sesión
- `/proyectos` - API para crear un proyecto vinculado a un `usuario_id`

## Notas

- Asegúrate de que la tabla `usuarios` exista en la base de datos antes de registrar usuarios.
- La clave `GROQ_API_KEY` debe estar disponible en `.env` para llamar al servicio de IA.
