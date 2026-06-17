# Paso 1: Usar una versión oficial y liviana de Python como base
FROM python:3.11-slim

# Paso 2: Crear una carpeta interna dentro del contenedor para nuestro proyecto
WORKDIR /app

# Paso 3: Copiar la lista de librerías al contenedor
COPY requirements.txt .

# Paso 4: Instalar las librerías dentro del contenedor de forma aislada
RUN pip install --no-cache-dir -r requirements.txt

# Paso 5: Copiar todo el código de nuestras carpetas locales hacia el contenedor
COPY . .

# Paso 6: Ejecutar el pipeline ETL para que la base de datos SQL se cree automáticamente adentro
RUN python src/etl.py

# Paso 7: Indicar que el contenedor usará el puerto 8050
EXPOSE 8050

# Paso 8: Comando para que al encender el contenedor se abra el Dashboard directamente
CMD ["python", "src/app.py"]