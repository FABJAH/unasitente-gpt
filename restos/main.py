from dotenv import load_dotenv
load_dotenv() 

from azure.storage.blob import BlobServiceClient
import os
import datetime
import openai
import json

# ——— Configuración de Azure Blob Storage ———
AZ_STORAGE_ACCOUNT = os.getenv("AZURE_STORAGE_ACCOUNT")
AZ_STORAGE_KEY     = os.getenv("AZURE_STORAGE_KEY")
AZ_BLOB_URL        = f"https://{AZ_STORAGE_ACCOUNT}.blob.core.windows.net"

blob_service = BlobServiceClient(
    account_url=AZ_BLOB_URL,
    credential=AZ_STORAGE_KEY
)
container_client = blob_service.get_container_client("articles")


def upload_json_folder():
    """
    Sube todos los .json de data/articles al contenedor 'articles'.
    """
    folder = os.path.join(os.path.dirname(__file__), "data", "articles")
    for fname in os.listdir(folder):
        if not fname.lower().endswith(".json"):
            continue
        path = os.path.join(folder, fname)
        with open(path, "rb") as f:
            container_client.upload_blob(
                name=fname,
                data=f,
                overwrite=True
            )
        print(f"✅ Uploaded {fname}")


# ——— Configuración de Azure OpenAI ———
openai.api_type    = "azure"
openai.api_base    = os.getenv("AZURE_OPENAI_ENDPOINT")
openai.api_key     = os.getenv("AZURE_OPENAI_KEY")
openai.api_version = os.getenv("AZURE_OPENAI_VERSION")
deployment_id      = os.getenv("AZURE_OPENAI_DEPLOYMENT")

# Función auxiliar que el modelo puede invocar
def get_current_time(location: str = "Barcelona") -> str:
    now = datetime.datetime.now()
    return f"La hora actual en {location} es {now.strftime('%H:%M')}"

# Definición de la función para OpenAI
functions = [
    {
        "name": "get_current_time",
        "description": "Obtiene la hora actual en una ciudad",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "La ciudad para obtener la hora"
                }
            },
            "required": ["location"]
        }
    }
]


def main():
    # 1) Subir JSON al contenedor
    print("Subiendo JSONs a Blob Storage…")
    upload_json_folder()

    # 2) Invocar a OpenAI con posibilidad de llamada a función
    print("\nConsultando hora actual con Azure OpenAI…")
    resp = openai.ChatCompletion.create(
        engine=deployment_id,
        messages=[{"role": "user", "content": "¿Qué hora es en Barcelona?"}],
        functions=functions,
        function_call="auto",
        max_tokens=100
    )

    choice = resp.choices[0].message
    if choice.get("function_call"):
        # El modelo solicitó get_current_time
        fname = choice.function_call.name
        args_str = choice.function_call.arguments
        params   = json.loads(args_str)

        print(f"➡️ Función llamada: {fname} con {params}")
        result = get_current_time(**params)

        # Enviamos el resultado de vuelta al modelo
        final = openai.ChatCompletion.create(
            engine=deployment_id,
            messages=[
                {"role": "user",    "content": "¿Qué hora es en Barcelona?"},
                {"role": "assistant", "content": choice.content or "", "function_call": choice.function_call},
                {"role": "function",  "name": fname, "content": result}
            ],
            max_tokens=100
        )
        print("🧠 Respuesta final del modelo:")
        print(final.choices[0].message.content)
    else:
        # El modelo respondió directamente sin llamar a la función
        print("🧠 Respuesta directa del modelo:")
        print(choice.content)


if __name__ == "__main__":
    main()
