#print("🔧 Cargando módulo de conexión a la base de datos...")
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
        print(f"Error al conectar a la base de datos: {e}")
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
        conn.close()
        return True
    
    except Exception as e:
        print(f"Error al actualizar el proyecto en la b ase de datos: {e}")
        if conn:
            conn.rollback()
            
            # Intentar registrar el error en la tabla para que el usuario sepa qué pasó
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE proyectos SET estado = 'error', error_message = %s WHERE id = %s",
                    (str(e), proyecto_id)
                )
                conn.commit()
                cursor.close()
            except Exception as error_db:
                print(f"Error al registrar el mensaje en la base de datos: {error_db}")
            finally:
                conn.close()
        return False
    
if __name__ == "__main__":
    conn = get_db_connection()
    if conn:
        print("🚀 ¡Conexión a la base de datos exitosa!")
        conn.close()
    else:
        print("❌ No se pudo conectar a la base de datos.")