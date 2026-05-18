from flask import Flask, jsonify, request
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

# 📝 Ruta para registrar un nuevo proyecto e iniciar el flujo
@app.route('/proyectos', methods=['POST'])
def crear_proyecto():
    # 1. Recibir los datos enviados en formato JSON desde el frontend
    datos = request.get_json()
    
    # Validar que los campos obligatorios existan
    if not datos or 'session_id' not in datos or 'idea_negocio' not in datos:
        return jsonify({
            "status": "error",
            "message": "Faltan campos obligatorios: 'session_id' y 'idea_negocio'."
        }), 400
        
    session_id = datos['session_id']
    idea_negocio = datos['idea_negocio']
    contexto_local = datos.get('contexto_local', '')
        
    # 2. Conexión a la base de datos e insertar (¡AHORA SÍ INDENTADO!)
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            
            # Query de inserción de datos iniciales del usuario
            query = """
                INSERT INTO proyectos (session_id, idea_negocio, contexto_local, estado) 
                VALUES (%s, %s, %s, 'pendiente')
                RETURNING id;
            """
            cursor.execute(query, (session_id, idea_negocio, contexto_local))
            
            # Obtenemos el ID generado automáticamente por el SERIAL
            nuevo_id = cursor.fetchone()[0]
            
            # Guardamos los cambios de forma definitiva (COMMIT)
            conn.commit()
            
            cursor.close()
            conn.close()

            return jsonify({
                "status": "success",
                "message": "✅ Proyecto creado exitosamente!",
                "proyecto_id": nuevo_id
            }), 201

        except Exception as e:
            if conn:
                conn.rollback()  # Revertir cualquier cambio en caso de error
            return jsonify({
                "status": "error",
                "message": f"Error al insertar en la base de datos: {str(e)}"
            }), 500
    else:
        return jsonify({
            "status": "error",
            "error": "❌ No se pudo conectar a la base de datos."
        }), 500

if __name__ == '__main__':
    app.run(debug=True)