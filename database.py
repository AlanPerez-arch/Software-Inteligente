import os
import json
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

def get_db_connection():
    try:
        connection = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            port=os.getenv('DB_PORT')
        )
        return connection
    except Exception as e:
        print(f"❌ Error al conectar a la base de datos: {e}")
        return None

def actualizar_datos_proyecto(proyecto_id, plan_negocio, kit_marketing, datos_financieros):
    """ 
    Actualizar un proyecto existente con los datos generados por el modelo de IA.
    """
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Query para actualizar los campos JSONB y cambiar el estado a completado
        query = """
            UPDATE proyectos
            SET plan_negocio = %s, 
                kit_marketing = %s, 
                datos_financieros = %s,
                estado = 'completado'
            WHERE id = %s
        """
        # Convertimos los diccionarios de Python a cadenas JSON para guardarlos en JSONB
        cursor.execute(query, (
            json.dumps(plan_negocio), 
            json.dumps(kit_marketing), 
            json.dumps(datos_financieros), 
            proyecto_id
        ))
        
        conn.commit()
        cursor.close()
        return True
    
    except Exception as e:
        print(f"⚠️ Error al actualizar el proyecto: {e}")
        if conn:
            conn.rollback() # Cancelamos la transacción fallida
            
            # Abrimos una nueva transacción limpia para registrar el error
            try:
                with conn.cursor() as error_cursor:
                    error_cursor.execute(
                        "UPDATE proyectos SET estado = 'error', error_message = %s WHERE id = %s",
                        (str(e), proyecto_id)
                    )
                    conn.commit()
            except Exception as error_db:
                print(f"❌ Error crítico al registrar el mensaje de error en la BD: {error_db}")
        return False
        
    finally:
        if conn:
            conn.close() # Nos aseguramos de cerrar la conexión pase lo que pase


def guardar_proyecto_con_respuestas(session_id, idea_negocio, contexto_local, usuario_id, plan_negocio, kit_marketing, datos_financieros, estado='completado'):
    conn = get_db_connection()
    if not conn:
        return None

    try:
        cursor = conn.cursor()
        query = """
            INSERT INTO proyectos (
                session_id,
                idea_negocio,
                contexto_local,
                estado,
                usuario_id,
                plan_negocio,
                kit_marketing,
                datos_financieros
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
        """
        cursor.execute(query, (
            session_id,
            idea_negocio,
            contexto_local,
            estado,
            usuario_id,
            json.dumps(plan_negocio),
            json.dumps(kit_marketing),
            json.dumps(datos_financieros)
        ))
        proyecto_id = cursor.fetchone()[0]
        conn.commit()
        return proyecto_id

    except Exception as e:
        print(f"❌ Error al guardar el proyecto con respuestas: {e}")
        if conn:
            conn.rollback()
        return None

    finally:
        if conn:
            conn.close()


def obtener_proyectos_por_usuario(usuario_id):
    conn = get_db_connection()
    if not conn:
        return []

    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        query = """
            SELECT id, session_id, idea_negocio, contexto_local, estado,
                   plan_negocio, kit_marketing, datos_financieros
            FROM proyectos
            WHERE usuario_id = %s
            ORDER BY id DESC;
        """
        cursor.execute(query, (usuario_id,))
        proyectos = cursor.fetchall()
        return proyectos

    except Exception as e:
        print(f"❌ Error al obtener proyectos del usuario: {e}")
        return []

    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    conn = get_db_connection()
    if conn:
        print("🚀 ¡Conexión a la base de datos exitosa usando el archivo .env!")
        conn.close()
    else:
        print("❌ No se pudo conectar. Revisa los valores en tu archivo .env")