import os
from langchain_openai.embeddings import AzureOpenAIEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import CharacterTextSplitter



# Cargar documento local
loader = TextLoader("demo_context.txt")
documents = loader.load()

# Dividir el texto en fragmentos
text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
docs = text_splitter.split_documents(documents)

# Crear índice con Chroma
embedding = AzureOpenAIEmbeddings(
    azure_deployment="gpt4deployment",  # Asegúrate que coincide con tu .env
    openai_api_version="2025-05-01-preview",
    openai_api_key=os.getenv("AZURE_OPENAI_KEY"),
    openai_api_base=os.getenv("AZURE_OPENAI_ENDPOINT"),
)


vectorstore = Chroma.from_documents(docs, embedding)

# Hacer una consulta de ejemplo
query = "¿Quién es el autor del texto?"
results = vectorstore.similarity_search(query)

for i, doc in enumerate(results):
    print(f"\n Fabio creo un asistente y encontro los errores de coneccion  Resultado {i+1}:\n{doc.page_content}")
