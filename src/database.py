import sqlite3
import os

# Esta es la ruta donde se guardará físicamente nuestra base de datos SQL
DB_PATH = "data/playstore.db"

def obtener_conexion():
    """
    Establece una conexión segura con la base de datos SQLite.
    Funciona como abrir una puerta de acceso para guardar o leer datos.
    """
    conn = sqlite3.connect(DB_PATH)
    return conn

def inicializar_base_de_datos():
    """
    Crea las tablas vacías dentro de la base de datos si es que aún no existen.
    Esto estructura nuestro espacio de almacenamiento.
    """

    # Nos aseguramos de que la carpeta 'data' exista por seguridad
    os.makedirs("data", exist_ok=True)
    
    # Abrimos la conexión
    conn = obtener_conexion()
    cursor = conn.cursor() 
    
    # TABLA 1: Aquí guardaremos las aplicaciones limpias y procesadas
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS aplicaciones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        app TEXT,
        category TEXT,
        rating REAL,
        reviews REAL,
        size REAL,
        installs INTEGER,
        type TEXT,
        price REAL,
        content_rating TEXT,
        is_popular INTEGER
    )
    """)
    
    # TABLA 2: Tabla de Auditoría y Control (Exigido en sistemas profesionales)
    # Registrará de forma automática el estado de la carga de datos
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS auditoria_etl (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha_ejecucion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        registros_procesados INTEGER,
        estado TEXT
    )
    """)
    
    # Guardamos los cambios de forma permanente y cerramos la puerta de la conexión
    conn.commit()
    conn.close()
    print("✅ Base de datos 'playstore.db' y tablas de control creadas con éxito.")

# Este bloque permite que si ejecutas este archivo suelto, se cree la base de datos de inmediato
if __name__ == "__main__":
    inicializar_base_de_datos()