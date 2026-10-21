
import os
import hashlib
from pathlib import Path

from dotenv import load_dotenv
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_classic.embeddings import CacheBackedEmbeddings
from langchain_classic.storage import LocalFileStore
from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    GoogleGenerativeAIEmbeddings,
)
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DOCUMENTOS_DIR = BASE_DIR / "documentos"
FAISS_DIR = BASE_DIR / "faiss_db_gemini"
CACHE_DIR = BASE_DIR / "cache_embeddings"

MODELO_EMBEDDINGS = "gemini-embedding-001"
MODELO_LLM = "gemini-3.8-flash"


def obtener_api_key():
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("No se encontró GEMINI_API_KEY en el archivo .env.")

    return api_key


def crear_embeddings():
    embeddings_gemini = GoogleGenerativeAIEmbeddings(
        model=MODELO_EMBEDDINGS,
        google_api_key=obtener_api_key()
    )

    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    almacenamiento = LocalFileStore(str(CACHE_DIR))

    embeddings_cache = CacheBackedEmbeddings.from_bytes_store(
        underlying_embeddings=embeddings_gemini,
        document_embedding_cache=almacenamiento,
        key_encoder=lambda texto: hashlib.sha256(
            f"{MODELO_EMBEDDINGS}:{texto}".encode("utf-8")
    ).hexdigest(),
    )

    return embeddings_cache


def reconstruir_indice():
    """Procesa los PDF y guarda un nuevo índice FAISS."""

    print("⏳ Cargando documentos PDF...")

    pdfs = DirectoryLoader(
        str(DOCUMENTOS_DIR),
        glob="*.pdf",
        loader_cls=PyPDFLoader
    ).load()

    if not pdfs:
        raise ValueError("No se encontraron páginas PDF para procesar.")

    print(f"✅ {len(pdfs)} páginas cargadas.")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=700,
        chunk_overlap=100,
        length_function=len
    )

    fragmentos = splitter.split_documents(pdfs)

    print(f"✂️ Generados {len(fragmentos)} fragmentos.")

    embeddings = crear_embeddings()

    vector_store = FAISS.from_documents(
        documents=fragmentos,
        embedding=embeddings
    )

    vector_store.save_local(str(FAISS_DIR))

    print("✅ Base FAISS de Gemini reconstruida y guardada.")

    return vector_store


def cargar_indice():
    """Carga FAISS desde disco o lo crea si no existe."""

    indice = FAISS_DIR / "index.faiss"
    metadatos = FAISS_DIR / "index.pkl"

    if indice.is_file() and metadatos.is_file():
        print("📂 Cargando base FAISS de Gemini existente...")

        return FAISS.load_local(
            str(FAISS_DIR),
            crear_embeddings(),
            allow_dangerous_deserialization=True
        )

    print("⚠️ No existe un índice completo. Creando uno...")
    return reconstruir_indice()


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


def crear_cadena_rag(vector_store):
    """Construye la cadena RAG utilizando Gemini."""

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "Eres un asistente especializado en responder preguntas "
            "utilizando documentos proporcionados por el usuario. "
            "Responde exclusivamente con información respaldada "
            "por el contexto recuperado. "
            "Si el contexto no contiene la respuesta, "
            "indica claramente que no tienes información suficiente. "
            "Responde en español de manera clara y precisa.\n\n"
            "Contexto:\n{contexto}"
        ),
        ("human", "{query}")
    ])

    retriever = vector_store.as_retriever(
        search_kwargs={"k": 3}
    )

    modelo = ChatGoogleGenerativeAI(
        model=MODELO_LLM,
        google_api_key=obtener_api_key(),
        temperature=0
    )

    cadena_rag = (
        {
            "contexto": retriever | RunnableLambda(format_docs),
            "query": RunnablePassthrough()
        }
        | prompt
        | modelo
        | StrOutputParser()
    )

    return cadena_rag


def consultar_rag(pregunta, cadena_rag):
    """Recibe una pregunta y devuelve la respuesta del agente."""

    if not pregunta.strip():
        raise ValueError("La pregunta no puede estar vacía.")

    return cadena_rag.invoke(pregunta)
