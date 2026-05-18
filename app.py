from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
# ¡CLAVE! Esto permite que tu frontend en otro puerto pueda hacer peticiones
CORS(app)

@app.route('/')
def home():
    # Esto buscará el archivo index.html dentro de la carpeta 'templates'
    return render_template('index.html')
# Configura tu API Key
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def llamar_ia(sistema, usuario):
    try:
        chat = client.chat.completions.create(
            messages=[
                {"role": "system", "content": sistema},
                {"role": "user", "content": usuario}
            ],
            model="llama3-8b-8192",
            temperature=0.7,
        )
        return chat.choices[0].message.content
    except Exception as e:
        return f"Error al generar: {str(e)}"

@app.route('/api/generar', methods=['POST'])
def generar_kit():
    # Recibimos el JSON desde el frontend
    data = request.get_json()
    idea = data.get('idea')
    
    if not idea:
        return jsonify({"error": "Falta la idea de negocio"}), 400

    print(f"Procesando idea: {idea}") # Para que veas en consola que está vivo

    # Llamadas (Puedes optimizarlas con threading después, por ahora secuencial está bien)
    prompt_negocio = "Eres un consultor. Dame un plan de negocio en 3 viñetas para: "
    prompt_marketing = "Eres un publicista. Escribe 2 posts cortos de Instagram para: "
    prompt_finanzas = "Eres financiero. Dime los 3 gastos esenciales iniciales para: "

    negocio = llamar_ia(prompt_negocio, idea)
    marketing = llamar_ia(prompt_marketing, idea)
    finanzas = llamar_ia(prompt_finanzas, idea)

    # Devolvemos el "Contrato JSON" al frontend
    return jsonify({
        "negocio": negocio,
        "marketing": marketing,
        "finanzas": finanzas
    })
    


if __name__ == '__main__':
    # debug=True reinicia el servidor automáticamente si haces cambios
    app.run(debug=True, port=5000)