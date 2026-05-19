from flask import Flask, jsonify, request, render_template, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db_connection, guardar_proyecto_con_respuestas, obtener_proyectos_por_usuario
import json
from groq import Groq
from flask_cors import CORS
import os
import uuid
from dotenv import load_dotenv


load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "supersecretkey123")
CORS(app)

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def llamar_ia(sistema, datos_usuario):
    try:
        chat = client.chat.completions.create(
            messages=[
                {"role": "system", "content": sistema},
                {"role": "user", "content": datos_usuario}
            ],
            model="llama-3.1-8b-instant",
            temperature=0.7,
        )
        return chat.choices[0].message.content
    except Exception as e:
        return f"Error al generar esta sección: {str(e)}"

# ======================================================
# VISTAS FRONTEND (Rutas HTML)
# ======================================================

# 🏠 HOME - Renderiza la landing page principal
@app.route("/")
def inicio():
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ======================================================
# FORMULARIO
# ======================================================

@app.route("/formulario", methods=["GET", "POST"])
def formulario():
    # 📌 ACCIÓN 1: SI EL USUARIO ENTRA A LA URL (GET)
    if request.method == 'GET':
        # Cambiamos index.html por formulario.html para que apunte al archivo correcto
        return render_template('formulario.html') 

    # 📌 ACCIÓN 2: SI EL USUARIO ENVÍA LOS DATOS (POST desde JS)
    if request.method == 'POST':
        # Extraer los datos enviados por el formulario estructurado
        idea = request.form.get('idea_negocio')
        descripcion = request.form.get('descripcion_idea')
        problema = request.form.get('problema_resuelve')
        publico = request.form.get('publico_objetivo')
        contexto = request.form.get('contexto_local')
        experiencia = request.form.get('experiencia', 'Sin experiencia previa')
        habilidades = request.form.get('habilidades')
        actividades = request.form.get('actividades', 'Ninguna en específico')
        equipo = request.form.get('equipo')
        presupuesto = request.form.get('presupuesto', 'No especificado')
        dificultad = request.form.get('dificultad', 'No especificada')
        comentarios = request.form.get('comentarios_extra', 'Ninguno')

        # Procesar los arreglos de los checkboxes
        recursos = request.form.getlist('recursos')
        ayuda_solicitada = request.form.getlist('ayuda')
        redes_sociales = request.form.getlist('redes')

        recursos_txt = ", ".join(recursos) if recursos else "Ninguno"
        ayuda_txt = ", ".join(ayuda_solicitada) if ayuda_solicitada else "Todo lo anterior"
        redes_txt = ", ".join(redes_sociales) if redes_sociales else "Ninguna en específico"

        # Construir el bloque de contexto optimizado para Llama 3
        contexto_usuario = f"""
        DATOS DEL PROYECTO:
        - Idea base: {idea}
        - Descripción detallada: {descripcion}
        - Problema que resuelve: {problema}
        - Público objetivo ideal: {publico}
        - Ubicación/Contexto local: {contexto}
        
        PERFIL DEL EMPRENDEDOR:
        - Experiencia relacionada: {experiencia}
        - Habilidades clave: {habilidades}
        - Actividades habituales: {actividades}
        - Estructura de equipo: {equipo}
        - Presupuesto inicial: {presupuesto}
        - Obstáculo principal: {dificultad}
        
        RECURSOS Y PREFERENCIAS:
        - Herramientas técnicas disponibles: {recursos_txt}
        - Redes de interés seleccionadas: {redes_txt}
        - Ayuda prioritaria solicitada: {ayuda_txt}
        - Notas adicionales: {comentarios}
        """

        # System Prompts calibrados para actuar como el ecosistema Bloom AI
        prompt_negocio = (
            "Eres Bloom AI, un consultor de negocios empático que democratiza el conocimiento. "
            "Usa el contexto proporcionado para estructurar una estrategia comercial viable. "
            "Incluye de forma clara: 1) Resumen de la Propuesta de Valor, 2) Ventaja competitiva usando las habilidades del usuario, "
            "y 3) Un plan de acción paso a paso adaptado a su contexto local. Tono motivador."
        )

        prompt_marketing = (
            f"Eres el motor de marketing de Bloom AI. Genera un kit básico de presencia digital basado "
            f"en las redes sociales de interés del usuario ({redes_txt}) y su público objetivo. Incluye ideas "
            f"estratégicas de contenido y dos propuestas de publicaciones con copies listos para copiar y usar."
        )

        prompt_finanzas = (
            f"Eres el asesor financiero de Bloom AI. Diseña un presupuesto de arranque crítico basándote "
            f"en el presupuesto estimado por el usuario ({presupuesto}) y los recursos que ya posee. "
            f"Identifica con precisión en qué gastar los primeros fondos de forma inteligente, evitando sugerir compras redundantes."
        )

        # Consultas al modelo Open Source
        negocio_res = llamar_ia(prompt_negocio, contexto_usuario)
        marketing_res = llamar_ia(prompt_marketing, contexto_usuario)
        finanzas_res = llamar_ia(prompt_finanzas, contexto_usuario)

        usuario_id = session.get('usuario_id') or request.form.get('usuario_id', 1)
        proyecto_id = guardar_proyecto_con_respuestas(
            session_id=request.form.get('session_id') or str(uuid.uuid4()),
            idea_negocio=idea,
            contexto_local=contexto,
            usuario_id=usuario_id,
            plan_negocio={"texto": negocio_res},
            kit_marketing={"texto": marketing_res},
            datos_financieros={"texto": finanzas_res},
            estado='completado'
        )

        if proyecto_id is None:
            return jsonify({
                "error": "No se pudo guardar el proyecto en la base de datos."
            }), 500

        return jsonify({
            "negocio": negocio_res,
            "marketing": marketing_res,
            "finanzas": finanzas_res,
            "proyecto_id": proyecto_id
        })

# 📊 DASHBOARD - Muestra los resultados generados por el usuario
@app.route("/dashboard")
def dashboard():
    usuario_id = session.get('usuario_id', 1)
    proyectos = obtener_proyectos_por_usuario(usuario_id)
    proyecto = proyectos[0] if proyectos else None

    return render_template(
        "dashboard.html",
        proyecto=proyecto,
        proyectos=proyectos,
        usuario_id=usuario_id
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
                    session['usuario_id'] = usuario_id
                    session['usuario_nombre'] = nombre_completo
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
    app.run(debug=os.environ.get("FLASK_DEBUG", "true").lower() == "true")