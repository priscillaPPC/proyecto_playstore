import pandas as pd
import logging
from pydantic import BaseModel, Field, field_validator
from database import obtener_conexion, inicializar_base_de_datos

# 1. BITÁCORA DE CONTROL 
# En lugar de usar print(), un sistema profesional escribe en un archivo de texto para auditoría
logging.basicConfig(
    filename="docs/proceso_etl.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)

# 2. REGLAS DE VALIDACIÓN
class AplicacionEsquema(BaseModel):
    app: str
    category: str
    rating: float = Field(ge=1.0, le=5.0) # Obligatorio: Rating entre 1.0 y 5.0
    reviews: float
    size: float = Field(gt=0.0)           # Obligatorio: Tamaño mayor que 0 MB
    installs: int
    type: str
    price: float
    content_rating: str
    is_popular: int

    @field_validator('type')
    def validar_tipo(cls, value):
        # Si el tipo no es Free o Paid, levantará un error por seguridad
        if value not in ['Free', 'Paid']:
            raise ValueError("El tipo debe ser 'Free' o 'Paid'")
        return value

# 3. EL PIPELINE AUTOMÁTICO
def ejecutar_pipeline_etl():
    logging.info("Iniciando el proceso ETL...")
    print(" Iniciando la tubería ETL automatizada...")
    
    try:
        # Nos aseguramos de que las tablas de la base de datos existan
        inicializar_base_de_datos()
        
        # --- [ E: EXTRAER ] ---
        csv_path = "data/googleplaystore_limpio.csv"
        df = pd.read_csv(csv_path)
        logging.info(f"CSV cargado con éxito. Total registros iniciales: {len(df)}")
        
        # --- [ T: TRANSFORMAR ] ---
        # Replicamos la regla de negocio de tu trabajo anterior: Popular si tiene >= 100,000 descargas
        df['Is_Popular'] = (df['Installs'] >= 100000).astype(int)
        
        # Seleccionamos las columnas que nos interesan para el almacenamiento SQL
        columnas = ['App', 'Category', 'Rating', 'Reviews', 'Size', 'Installs', 'Type', 'Price', 'Content Rating', 'Is_Popular']
        df_filtrado = df[columnas].dropna() # Quitamos filas vacías
        
        registros_validos = []
        conteo_errores = 0
        
        # Pasamos cada fila por el "filtro de calidad" de Pydantic
        for index, row in df_filtrado.iterrows():
            try:
                datos_fila = {
                    "app": str(row['App']),
                    "category": str(row['Category']),
                    "rating": float(row['Rating']),
                    "reviews": float(row['Reviews']),
                    "size": float(row['Size']),
                    "installs": int(row['Installs']),
                    "type": str(row['Type']),
                    "price": float(row['Price']),
                    "content_rating": str(row['Content Rating']),
                    "is_popular": int(row['Is_Popular'])
                }
                # Si pasa las reglas, se agrega a la lista limpia
                app_validada = AplicacionEsquema(**datos_fila)
                registros_validos.append(app_validada.model_dump())
            except Exception as e:
                conteo_errores += 1
                # Si falla, se anota calladamente en el archivo log para no romper el programa
                logging.warning(f"Fila {index} rechazada: {e}")
        
        print(f" Validación completada. Filas exitosas: {len(registros_validos)} | Errores detectados: {conteo_errores}")
        
        # --- [ L: CARGAR ] ---
        if len(registros_validos) > 0:
            df_final = pd.DataFrame(registros_validos)
            conn = obtener_conexion()
            
            # Guardamos el DataFrame limpio en la tabla 'aplicaciones' de la base de datos SQL
            df_final.to_sql('aplicaciones', conn, if_exists='append', index=False)
            
            # Guardamos un registro en la tabla de auditoría para saber que todo salió bien
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO auditoria_etl (registros_procesados, estado) VALUES (?, ?)",
                (len(registros_validos), "EXITOSO")
            )
            conn.commit()
            conn.close()
            
            logging.info("Proceso ETL finalizado correctamente. Datos guardados en SQL.")
            print("Datos validados y cargados en tu base de datos SQL.")
            
    except Exception as e:
        error_msg = f"Error crítico en el pipeline: {str(e)}"
        logging.error(error_msg)
        print(f"{error_msg}")

if __name__ == "__main__":
    ejecutar_pipeline_etl()