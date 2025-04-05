import os  
import requests  
import json  
import uuid  
from dotenv import load_dotenv  
import streamlit as st  
from azure.cosmos import CosmosClient, PartitionKey, exceptions  
  
# Cargar las variables de entorno desde el archivo .env y configurar las claves de API de Azure OpenAI y la conexión a Cosmos DB.  
load_dotenv()  
endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')  
subscription_key = os.getenv('AZURE_OPENAI_SUBSCRIPTION_KEY')  
if not endpoint or not subscription_key:  
    raise ValueError("Las variables de entorno no se han cargado correctamente.")  
cosmos_endpoint = os.getenv('COSMOS_DB_ENDPOINT')  
cosmos_key = os.getenv('COSMOS_DB_KEY')  
cosmos_database_name = os.getenv('COSMOS_DB_DATABASE_NAME')  
cosmos_container_name = os.getenv('COSMOS_DB_CONTAINER_NAME')  
client = CosmosClient(cosmos_endpoint, cosmos_key)  
database = client.create_database_if_not_exists(id=cosmos_database_name)  
container = database.create_container_if_not_exists(  
    id=cosmos_container_name,  
    partition_key=PartitionKey(path="/id"),  
    offer_throughput=400  
)  
  
def clasificar_comentario(comentario, endpoint, subscription_key):  
    """  
    Esta función clasifica un comentario en categorías específicas utilizando la API de Azure OpenAI.  
    Construye un prompt claro, envía una solicitud POST a la API y procesa la respuesta para obtener la clasificación del comentario.  
    """  
    prompt = (  
        "Tu tarea es clasificar comentarios basándote únicamente en el contenido mencionado en el texto del comentario. "  
        "Deberás asignar el comentario a uno de los siguientes tópicos específicos: 'cocina', 'servicio', 'baños', 'comida', 'otros'. "  
        "Es crucial que tu respuesta se limite solo al nombre del tópico correspondiente sin incluir opiniones, observaciones adicionales "  
        "o cualquier otro tipo de elaboración. A continuación se te proporcionará un comentario, y tu deber es identificar claramente el tópico relevante "  
        "basado en el contenido del mismo. No asumas información que no esté explícitamente mencionada en el comentario.\n\n"  
        f"Comentario: {comentario}\nTópico:"  
    )  
    url = f"{endpoint}"  
    headers = {"Content-Type": "application/json", "api-key": subscription_key}  
    payload = {"messages": [{"role": "system", "content": "Eres un asistente útil."}, {"role": "user", "content": prompt}], "max_tokens": 10, "n": 1, "stop": None}  
    response = requests.post(url, headers=headers, json=payload)  
    if response.status_code == 200:  
        response_data = response.json()  
        topico = response_data['choices'][0]['message']['content'].strip()  
        return topico  
    else:  
        raise Exception(f"Error en la solicitud a la API: {response.status_code} - {response.text}")  
  
def calificar_comentario(comentario, endpoint, subscription_key):  
    """  
    Esta función evalúa un comentario en una escala de 1 a 5 estrellas utilizando emojis, mediante la API de Azure OpenAI.  
    Envía un prompt detallado a la API y procesa la respuesta para obtener la calificación en forma de emojis de estrellas.  
    """  
    prompt = (  
        "¡Necesitamos tu ayuda para evaluar este comentario! Por favor, lee detenidamente el siguiente comentario "  
        "y califícalo con estrellas del 1 al 5 basado en su utilidad, claridad y relevancia. Utiliza solo los emojis "  
        "de estrellas para tu respuesta. No incluyas ningún otro símbolo, número o texto adicional. Copia y pega "  
        "las estrellas correspondientes del siguiente conjunto: ⭐, ⭐⭐, ⭐⭐⭐, ⭐⭐⭐⭐, ⭐⭐⭐⭐⭐. No modifiques el formato ni "  
        "alteres los emojis. Tu participación es esencial para mantener la integridad y precisión de nuestras evaluaciones. "  
        "Gracias por tu colaboración.\n\n"  
        f"Comentario: {comentario}\n"  
        "Estrellas:"  
    )  
    url = f"{endpoint}"  
    headers = {"Content-Type": "application/json", "api-key": subscription_key}  
    payload = {"messages": [{"role": "system", "content": "Eres un asistente útil."}, {"role": "user", "content": prompt}], "max_tokens": 10, "n": 1, "stop": None}  
    response = requests.post(url, headers=headers, json=payload)  
    if response.status_code == 200:  
        response_data = response.json()  
        estrellas = response_data['choices'][0]['message']['content'].strip()  
        return estrellas  
    else:  
        raise Exception(f"Error en la solicitud a la API: {response.status_code} - {response.text}")  
  
def guardar_comentario_en_cosmos(comentario, topico, estrellas):  
    """  
    Esta función guarda un comentario junto con su clasificación y calificación en Cosmos DB.  
    Crea un documento único para cada comentario y lo almacena en la base de datos.  
    """  
    comentario_documento = {"id": str(uuid.uuid4()), "comentario": comentario, "topico": topico, "estrellas": estrellas}  
    container.create_item(body=comentario_documento)  
  
# Crear la interfaz de usuario de Streamlit para permitir la entrada de comentarios y mostrar los resultados de clasificación y calificación.  
st.title("Clasificación y Calificación de Comentarios")  
comentario = st.text_area("Introduce tu comentario:")  
if st.button("Enviar"):  
    if comentario:  
        try:  
            topico = clasificar_comentario(comentario, endpoint, subscription_key)  
            estrellas = calificar_comentario(comentario, endpoint, subscription_key)  
            st.write(f"Comentario: {comentario}")  
            st.write(f"Tópico: {topico}")  
            st.write(f"Estrellas: {estrellas}")  
            guardar_comentario_en_cosmos(comentario, topico, estrellas)  
            st.success("Comentario guardado en Cosmos DB.")  
        except Exception as e:  
            st.error(f"Error: {e}")  
    else:  
        st.warning("Por favor, introduce un comentario.")  