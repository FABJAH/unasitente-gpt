import os
from dotenv import load_dotenv
from openai import AzureOpenAI

# 1. Cargar variables del .env
load_dotenv()

# 2. Debug: imprimimos lo que realmente leyó
print("🔍 Endpoint    :", os.getenv("AZURE_OPENAI_ENDPOINT"))
print("🔑 API Key ok  :", os.getenv("AZURE_OPENAI_KEY") is not None)
print("🚀 Deployment :", os.getenv("AZURE_OPENAI_DEPLOYMENT"))
print("📦 API Version:", os.getenv("AZURE_OPENAI_VERSION"))

# 3. Crear el cliente AzureOpenAI
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    api_version=os.getenv("AZURE_OPENAI_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
)

# 4. Petición de prueba
response = client.chat.completions.create(
    model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
    messages=[
        {"role": "system", "content": "Eres un asistente útil y claro."},
        {"role": "user",   "content": "¿Cuál es la capital de Marruecos?"}
    ],
    max_tokens=200
)

# 5. Mostrar la respuesta
print("📢 Respuesta:", response.choices[0].message.content)
