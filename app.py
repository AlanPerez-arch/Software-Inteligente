from flask import Flask, jsonify, request, render_template
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db_connection
import json

app = Flask(__name__)

# ======================================================
# VISTAS FRONTEND (Rutas HTML)
# ======================================================

# 🏠 HOME - Renderiza la landing page principal
@app.route("/")
def inicio():
    return render_template("index.html")

# 👤 LOGIN (Vista) - Cambiado a método GET para mostrar el formulario visual
@app.route("/login", methods=['GET'])
def principal():
    return render_template("login.html")

# 📝 FORMULARIO - Vista para registrar las ideas de negocio
@app.route("/formulario")
def formulario():
    return render_template("formulario.html")

# 📊 DASHBOARD - Muestra los resultados generados (Versión Inicial con Mockup)
@app.route("/dashboard")
def dashboard():
    return render_template(
        "dashboard.html",
        estado="Generado",
        fecha_creacion="18 Mayo 2026",
        resumen_negocio="""
        Negocio enfocado en la venta de pasteles artesanales
        personalizados a domicilio, dirigido a clientes que buscan
        productos únicos y de calidad para celebraciones y eventos.
        """,
        propuesta_valor="""
        Entrega rápida, personalización completa de diseños
        y sabores, además de atención cercana por redes sociales.
        """,
        publico_objetivo="""
        Jóvenes, familias y personas entre 18 y 40 años
        que buscan productos personalizados para cumpleaños,
        reuniones y eventos especiales.
        """,
        canales_venta="""
        Instagram, Facebook Marketplace, WhatsApp Business
        y entregas locales a domicilio.
        """,
        publicaciones_redes="""
        🎂 ¡Haz tus momentos más dulces!
        Personalizamos pasteles artesanales para cualquier ocasión.
        Ordena hoy por WhatsApp y recibe en casa.
        """,
        estimacion_costos="""
        Materia prima: $3,000 MXN
        Publicidad: $1,000 MXN
        Empaques y envíos: $1,000 MXN
        """,
        posibles_ingresos="""
        Ventas mensuales estimadas:
        entre $12,000 y $18,000 MXN
        dependiendo de la temporada y demanda.
        """
    )

# ⏳ HISTORIAL - Vista estática inicial del listado de proyectos
@app.route("/historial")
def historial():
    proyectos = [
        {
            "idea": "Pastelería artesanal a domicilio",
            "contexto": "Ventas locales mediante Instagram y WhatsApp en colonias urbanas.",
            "estado": "Generado",
            "fecha": "18 Mayo 2026"
        },
        {
            "idea": "Cafetería temática gamer",
            "contexto": "Enfocado en estudiantes universitarios y comunidad gaming local.",
            "estado": "Procesando",
            "fecha": "17 Mayo 2026"
        },
        {
            "idea": "Tienda de ropa vintage",
            "contexto": "Venta online enfocada en jóvenes mediante TikTok e Instagram.",
            "estado": "Generado",
            "fecha": "15 Mayo 2026"
        }
    ]
    return render_template("historial.html", proyectos=proyectos)

# ⚠️ ERROR PAGE - Vista para fallos de servidor o IA
@app.route("/error")
def error():
    return render_template(
        "error.html",
        estado="error",
        error_mensaje="""
        Error de conexión con el modelo de IA.
        La solicitud excedió el tiempo de espera
        permitido por el servidor.
        """
    )


# ======================================================
# API ENDPOINTS (Procesamiento de Datos & JSON)
# ======================================================

# 🚀 Diagnóstico - Verifica la respuesta del motor de PostgreSQL en la Web
@app.route('/test-db', methods=['GET'])
def test_database():
    conn = get_db_connection()
    if conn:
        try:
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

# 👥 API Registro - Inserta nuevos usuarios desde los formularios del front
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
    
    password_encriptada = generate_password_hash(contrasena)
    
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
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

# 🔑 API Login - Valida credenciales e interactúa con el backend
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
            query = "SELECT id, nombre_completo, contrasena_hash FROM usuarios WHERE correo_electronico = %s;"
            cursor.execute(query, (correo,))
            usuario = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            if usuario:
                usuario_id, nombre_completo, hash_almacenado = usuario
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

# 📊 API Proyectos - Crea un proyecto enlazándolo con un usuario_id
@app.route('/proyectos', methods=['POST'])
def crear_proyecto():
    datos = request.get_json()
    
    if not datos or 'session_id' not in datos or 'idea_negocio' not in datos or 'usuario_id' not in datos:
        return jsonify({
            "status": "error",
            "message": "Faltan campos obligatorios: 'session_id', 'idea_negocio' y 'usuario_id'."
        }), 400
        
    session_id = datos['session_id']
    idea_negocio = datos['idea_negocio']
    usuario_id = datos['usuario_id']
    contexto_local = datos.get('contexto_local', '')
        
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            query = """
                INSERT INTO proyectos (session_id, idea_negocio, contexto_local, estado, usuario_id) 
                VALUES (%s, %s, %s, 'pendiente', %s)
                RETURNING id;
            """
            cursor.execute(query, (session_id, idea_negocio, contexto_local, usuario_id))
            nuevo_id = cursor.fetchone()[0]
            
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
                conn.rollback()
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

# ======================================================
# ARRANQUE DEL SERVIDOR
# ======================================================
if __name__ == '__main__':
    app.run(debug=True)