from flask import Flask, render_template

app = Flask(__name__)

# ======================================================
# HOME
# ======================================================

@app.route("/")
def inicio():

    return render_template(

        "index.html"

    )

# ======================================================
# DASHBOARD
# ======================================================

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

# ======================================================
# HISTORIAL
# ======================================================

@app.route("/historial")
def historial():

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
    
@app.route("/login")
def principal():
    return render_template("login.html")

@app.route("/formulario")
def formulario():

    return render_template(

        "formulario.html"

    )
# ======================================================
# ERROR PAGE
# ======================================================

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
# RUN SERVER
# ======================================================

if __name__ == "__main__":

    app.run(

        debug=True

    )