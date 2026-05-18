from flask import Flask, jsonify, request
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db_connection

app = Flask(__name__)

@app.route('/')
def home():
    return '¡Hola desde Flask!'

# 🚀 Ruta de prueba para verificar la conexión a la base de datos desde la Web
@app.route('/test-db', methods=['GET'])
def test_database():
    conn = get_db_connection()
    if conn:
        try:
            # Creamos un cursor para ejecutar una consulta de prueba
            cursor = conn.cursor()
            cursor.execute('SELECT version();')
            db_version = cursor.fetchone()
            cursor.close()
            conn.close()
            return jsonify({
                "status": "success",
                "message": "✅ Conexión a la base de datos exitosa!", 
                "postgres_version": db_version[0]
            }), 200
        except Exception as e:
            print(f"Error al ejecutar consulta: {e}")
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({
            "status": "error",
            "error": "❌ No se pudo conectar a la base de datos."
        }), 500

# 📝 Ruta para registrar un nuevo proyecto vinculado a un usuario
@app.route('/proyectos', methods=['POST'])
def crear_proyecto():
    # 1. Recibir los datos enviados en formato JSON desde el frontend
    datos = request.get_json()
    
    # Validar que los campos obligatorios existan (ahora incluye usuario_id)
    if not datos or 'session_id' not in datos or 'idea_negocio' not in datos or 'usuario_id' not in datos:
        return jsonify({
            "status": "error",
            "message": "Faltan campos obligatorios: 'session_id', 'idea_negocio' y 'usuario_id'."
        }), 400
        
    session_id = datos['session_id']
    idea_negocio = datos['idea_negocio']
    usuario_id = datos['usuario_id']
    contexto_local = datos.get('contexto_local', '')
        
    # 2. Conexión a la base de datos e inserción
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            
            # Query actualizada con la llave foránea usuario_id
            query = """
                INSERT INTO proyectos (session_id, idea_negocio, contexto_local, estado, usuario_id) 
                VALUES (%s, %s, %s, 'pendiente', %s)
                RETURNING id;
            """
            cursor.execute(query, (session_id, idea_negocio, contexto_local, usuario_id))
            
            # Obtenemos el ID generado automáticamente por el SERIAL
            nuevo_id = cursor.fetchone()[0]
            
            # Guardamos los cambios de forma definitiva (COMMIT)
            conn.commit()
            
            cursor.close()
            conn.close()

            return jsonify({
                "status": "success",
                "message": "✅ Proyecto creado y vinculado exitosamente!",
                "proyecto_id": nuevo_id
            }), 201

        except Exception as e:
            if conn:
                conn.rollback()  # Revertir cualquier cambio en caso de error
            
            # Capturar error si el usuario_id proporcionado no existe en la tabla usuarios
            if "foreign key" in str(e).lower() or "llave foránea" in str(e).lower():
                return jsonify({
                    "status": "error",
                    "message": "El 'usuario_id' proporcionado no existe en el sistema."
                }), 400
                
            return jsonify({
                "status": "error",
                "message": f"Error al insertar en la base de datos: {str(e)}"
            }), 500
    else:
        return jsonify({
            "status": "error",
            "error": "❌ No se pudo conectar a la base de datos."
        }), 500

# 👤 Ruta para registrar un nuevo usuario en la plataforma
@app.route('/registro', methods=['POST'])
def registrar_usuario():
    datos = request.get_json()
    
    if not datos or 'nombre_completo' not in datos or 'correo_electronico' not in datos or 'contrasena' not in datos:
        return jsonify({
            "status": "error",
            "message": "Todos los campos ('nombre_completo', 'correo_electronico', 'contrasena') son obligatorios."
        }), 400
        
    nombre = datos['nombre_completo']
    correo = datos['correo_electronico']
    contrasena = datos['contrasena']
    
    # Encriptar la contraseña usando pbkdf2:sha256 de forma segura
    password_encriptada = generate_password_hash(contrasena)
    
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            
            # Insertar el nuevo usuario en la base de datos
            query = """
                INSERT INTO usuarios (nombre_completo, correo_electronico, contrasena_hash)
                VALUES (%s, %s, %s) RETURNING id;
            """
            cursor.execute(query, (nombre, correo, password_encriptada))
            usuario_id = cursor.fetchone()[0]
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return jsonify({
                "status": "success",
                "message": "¡Cuenta creada exitosamente!",
                "usuario_id": usuario_id
            }), 201
            
        except Exception as e:
            if conn:
                conn.rollback()
            # Validar si el correo ya está registrado por la restricción UNIQUE
            if "unique" in str(e).lower() or "ya existe" in str(e).lower():
                return jsonify({
                    "status": "error",
                    "message": "El correo electrónico ya se encuentra registrado."
                }), 400
            return jsonify({
                "status": "error",
                "message": f"Error al registrar usuario: {str(e)}"
            }), 500
    else:
        return jsonify({
            "status": "error",
            "error": "❌ No se pudo conectar a la base de datos."
        }), 500

# 🔑 Ruta para iniciar sesión
@app.route('/login', methods=['POST'])
def login_usuario():
    datos = request.get_json()
    
    if not datos or 'correo_electronico' not in datos or 'contrasena' not in datos:
        return jsonify({
            "status": "error",
            "message": "Faltan campos obligatorios: 'correo_electronico' y 'contrasena'."
        }), 400
        
    correo = datos['correo_electronico']
    contrasena = datos['contrasena']
    
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            
            # Buscar al usuario por correo para obtener su hash de contraseña
            query = "SELECT id, nombre_completo, contrasena_hash FROM usuarios WHERE correo_electronico = %s;"
            cursor.execute(query, (correo,))
            usuario = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            if usuario:
                usuario_id, nombre_completo, hash_almacenado = usuario
                # Validar si la contraseña enviada coincide con el hash guardado
                if check_password_hash(hash_almacenado, contrasena):
                    return jsonify({
                        "status": "success",
                        "message": f"¡Bienvenido de nuevo, {nombre_completo}!",
                        "usuario": {
                            "id": usuario_id,
                            "nombre": nombre_completo,
                            "correo": correo
                        }
                    }), 200
            
            # Mensaje genérico por seguridad (así no revelamos si el correo existe o no)
            return jsonify({
                "status": "error",
                "message": "Correo electrónico o contraseña incorrectos."
            }), 401
            
        except Exception as e:
            return jsonify({
                "status": "error",
                "message": f"Error en el servidor durante el login: {str(e)}"
            }), 500
    else:
        return jsonify({
            "status": "error",
            "error": "❌ No se pudo conectar a la base de datos."
        }), 500

if __name__ == '__main__':
    app.run(debug=True)