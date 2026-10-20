import os 
from dotenv import load_dotenv

from langchain_community.document_loaders import DirectoryLoader
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda


load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
LANGSMITH_TRACING = os.getenv("LANGSMITH_TRACING")
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")

print("⏳ Cargando documentos...")
pdfs = DirectoryLoader('documentos', glob='*.pdf', loader_cls=PyPDFLoader).load()
print(f"✅ {len(pdfs)} documentos cargados.")

print("✂️ Troceando el texto...")
splitter  = RecursiveCharacterTextSplitter(
         chunk_size=700, 
         chunk_overlap=100,
         length_function=len 
)

fragmentos = splitter.split_documents(pdfs)
print(f"✂️ Generados {len(fragmentos)} fragmentos de texto reales.")

print("🧠 Generando embeddings con all-minilm...")
embeddings = OllamaEmbeddings(model="all-minilm")



print("💾 Guardando base de datos en la carpeta 'faiss_db'...")
vector_store = FAISS.from_documents(documents=fragmentos, embedding=embeddings)
print("🚀 ¡Base de datos vectorial creada con éxito!")


vector_store.save_local("faiss_db") 
print("🚀 ¡Base de datos guardada con éxito en disco! Ya puedes cerrar este script.")

prompt = ChatPromptTemplate (
    [("system" , "Responde la pregunta del usuario usando exclusivamente el contexto provisto abajo.\n\nContexto:\n{contexto}"),
     ("human", "{query}")]
)

retriever = vector_store.as_retriever(search_kwargs={"k": 3})
modelo = OllamaLLM(model= "llama3.2:1b")

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

cadena_rag = (
     {
        "contexto": retriever | RunnableLambda(format_docs), 
        "query": RunnablePassthrough()
    }
    | prompt 
    | modelo 
    | StrOutputParser()
)


pregunta = 'como solicitar el seguro de viaje?'
print(f"\n❓ Buscando respuesta para: '{pregunta}'...\n")

respuesta = cadena_rag.invoke(pregunta)
print("🤖 Respuesta del Asistente:")
print(respuesta)