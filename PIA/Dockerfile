# Utiliza una imagen base oficial de Python  
FROM python:3.9-slim  
  
# Establece el directorio de trabajo en la imagen de Docker  
WORKDIR /app  
  
# Copia los archivos de requisitos en el directorio de trabajo  
COPY requirements.txt .  
  
# Instala las dependencias necesarias  
RUN pip install --no-cache-dir -r requirements.txt  
  
# Copia el resto de los archivos de la aplicación en el directorio de trabajo  
COPY . .  
  
# Expone el puerto en el que se ejecutará la aplicación Streamlit  
EXPOSE 8501  
  
# Comando para ejecutar la aplicación Streamlit  
CMD ["streamlit", "run", "app.py"]  