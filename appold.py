from flask import Flask, jsonify, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def llamar_ia(sistema, datos_usuario):
    try:
        chat = client.chat.completions.create(
            messages=[
                {"role": "system", "content": sistema},
                {"role": "user", "content": datos_usuario}
            ],
            model="llama3-8b-8192",
            temperature=0.7,
        )
        return chat.choices[0].message.content
    except Exception as e:
        return f"Error al generar esta sección: {str(e)}"

# ======================================================
# USUARIOS DEMO EN MEMORIA
# ======================================================

usuarios = {
    "demo@bloom.com": {
        "nombre": "Usuario Demo",
        "password": generate_password_hash("1234")
    }
}

# ======================================================
# VALIDACIÓN DE LOGIN
# ======================================================

def login_requerido():
    return "usuario" in session

# ======================================================
# HOME
# ======================================================

@app.route("/")
def inicio():

    if not login_requerido():
        return redirect(url_for("login"))

    return render_template("index.html")

# ======================================================
# LOGIN
# ======================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if login_requerido():
        return redirect(url_for("inicio"))

    if request.method == "POST":
        accion = request.form.get("accion")
        correo = request.form.get("correo")
        password = request.form.get("password")

        if accion == "registro":
            nombre = request.form.get("nombre")

            if correo in usuarios:
                flash("Ese correo ya está registrado.", "danger")
                return redirect(url_for("login"))

            usuarios[correo] = {
                "nombre": nombre,
                "password": generate_password_hash(password)
            }

            session["usuario"] = correo
            session["nombre"] = nombre
            session["es_nuevo"] = True

            return redirect(url_for("inicio"))

        usuario = usuarios.get(correo)

        if usuario and check_password_hash(usuario["password"], password):
            session["usuario"] = correo
            session["nombre"] = usuario["nombre"]
            session["es_nuevo"] = False

            return redirect(url_for("inicio"))

        flash("Correo o contraseña incorrectos.", "danger")

    return render_template("login.html")

# ======================================================
# LOGOUT
# ======================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))

# ======================================================
# DASHBOARD
# ======================================================

@app.route("/dashboard")
def dashboard():

    if not login_requerido():
        return redirect(url_for("login"))

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

# ======================================================
# HISTORIAL
# ======================================================

@app.route("/historial")
def historial():

    if not login_requerido():
        return redirect(url_for("login"))

    proyectos = [

        {
            "idea": "Pastelería artesanal a domicilio",

            "contexto": """
            Ventas locales mediante Instagram y WhatsApp
            en colonias urbanas.
            """,

            "estado": "Generado",

            "fecha": "18 Mayo 2026"
        },

        {
            "idea": "Cafetería temática gamer",

            "contexto": """
            Enfocado en estudiantes universitarios
            y comunidad gaming local.
            """,

            "estado": "Procesando",

            "fecha": "17 Mayo 2026"
        },

        {
            "idea": "Tienda de ropa vintage",

            "contexto": """
            Venta online enfocada en jóvenes
            mediante TikTok e Instagram.
            """,

            "estado": "Generado",

            "fecha": "15 Mayo 2026"
        }

    ]

    return render_template(
        "historial.html",
        proyectos=proyectos
    )

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
            "Eres el motor de marketing de Bloom AI. Genera un kit básico de presencia digital basado "
            "en las redes sociales de interés del usuario ({redes_txt}) y su público objetivo. Incluye ideas "
            "estratégicas de contenido y dos propuestas de publicaciones con copies listos para copiar y usar."
        )

        prompt_finanzas = (
            "Eres el asesor financiero de Bloom AI. Diseña un presupuesto de arranque crítico basándote "
            "en el presupuesto estimado por el usuario ({presupuesto}) y los recursos que ya posee. "
            "Identifica con precisión en qué gastar los primeros fondos de forma inteligente, evitando sugerir compras redundantes."
        )

        # Consultas al modelo Open Source
        negocio_res = llamar_ia(prompt_negocio, contexto_usuario)
        marketing_res = llamar_ia(prompt_marketing, contexto_usuario)
        finanzas_res = llamar_ia(prompt_finanzas, contexto_usuario)

        # Devolvemos la respuesta estructurada en formato JSON al JavaScript
        return jsonify({
            "negocio": negocio_res,
            "marketing": marketing_res,
            "finanzas": finanzas_res
        })

# ======================================================
# ERROR PAGE
# ======================================================

@app.route("/error")
def error():

    if not login_requerido():
        return redirect(url_for("login"))

    return render_template(

        "error.html",

        estado="error",

        error_mensaje="""
        Error de conexión con el modelo de IA.
        La solicitud excedió el tiempo de espera
        permitido por el servidor.
        """

    )
    
@app.route("/principal")
def principal():
    return render_template(

        "principal.html",
    )

# ======================================================
# RUN SERVER
# ======================================================

if __name__ == "__main__":

    app.run(debug=True)