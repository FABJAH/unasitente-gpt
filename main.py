import os
import openai
import datetime

# Configurar cliente OpenAI con Azure
openai.api_type = "azure"
openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
openai.api_key = os.getenv("AZURE_OPENAI_KEY")
openai.api_version = os.getenv("AZURE_OPENAI_VERSION")
deployment_id = os.getenv("AZURE_OPENAI_DEPLOYMENT")

# 👉 Función externa simulada
def get_current_time(location: str = "Barcelona") -> str:
    now = datetime.datetime.now()
    return f"La hora actual en {location} es {now.strftime('%H:%M')}"

# 👉 Definición de función para OpenAI
functions = [
    {
        "name": "get_current_time",
        "description": "Obtiene la hora actual en una ciudad",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "La ciudad para obtener la hora",
                }
            },
            "required": ["location"],
        },
    }
]

# 👉 Primer paso: el modelo decide si invoca la función
response = openai.ChatCompletion.create(
    engine=deployment_id,
    messages=[
        {"role": "user", "content": "¿Qué hora es en Barcelona?"}
    ],
    functions=functions,
    function_call="auto",
    max_tokens=100
)

# 👉 Verificamos si el modelo pidió la función
choice = response.choices[0]
if "function_call" in choice.message:
    function_name = choice.message.function_call.name
    arguments = eval(choice.message.function_call.arguments)
    
    print(f"➡️ El modelo llamó a la función: {function_name} con: {arguments}")

    if function_name == "get_current_time":
        result = get_current_time(**arguments)

        # 👉 Enviamos resultado de función al modelo
        final_response = openai.ChatCompletion.create(
            engine=deployment_id,
            messages=[
                {"role": "user", "content": "¿Qué hora es en Barcelona?"},
                choice.message,
                {"role": "function", "name": function_name, "content": result}
            ],
            max_tokens=100
        )

        print("🧠 Respuesta del modelo:")
        print(final_response.choices[0].message.content)
else:
    print("🧠 Respuesta sin usar función:")
    print(choice.message.content)
