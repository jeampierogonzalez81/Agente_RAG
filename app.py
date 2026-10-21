"""Interfaz Streamlit del asistente RAG basado en documentos PDF."""

import streamlit as st

from rag import cargar_indice, crear_cadena_rag, consultar_rag

st.set_page_config(
    page_title="Asistente Inteligente RAG",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS aislado de la estructura funcional del input: no se cambian
# position, pointer-events, z-index ni los contenedores internos.
st.markdown(
    """
<style>
:root {
    --rag-bg: #151E2E;
    --rag-navy: #14243A;
    --rag-blue: #244A72;
    --rag-text: #EAF2FC;
    --rag-border: #416B9D;
}

.stApp, [data-testid="stAppViewContainer"] {
    background-color: var(--rag-bg);
    color: var(--rag-text);
}

/* Encabezado */
.rag-header {
    background: linear-gradient(120deg, #14243A, #244A72);
    border: 1px solid #36577B;
    border-radius: 18px;
    padding: 28px 32px;
    margin-bottom: 22px;
}
.rag-title {
    color: #FFFFFF;
    font-size: clamp(1.5rem, 3vw, 2rem);
    font-weight: 750;
    margin: 0 0 8px;
}
.rag-subtitle {
    color: #D2E1F3;
    font-size: 1rem;
    margin: 0;
}

/* Barra lateral con contraste */
[data-testid="stSidebar"] {
    background: linear-gradient(160deg, #304D6D 0%, #263F5C 55%, #1D314B 100%);
    border-right: 1px solid #52718E;
}
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] label {
    color: #F3F7FF !important;
}
[data-testid="stSidebar"] [data-testid="stAlert"] {
    background: #355574;
    border: 1px solid #6689A9;
    border-radius: 12px;
}
[data-testid="stSidebar"] [data-testid="stAlert"] p {
    color: #FFFFFF !important;
}

/* Mensajes */
[data-testid="stChatMessage"] {
    background: #1D304A;
    border: 1px solid #34516F;
    border-radius: 16px;
    padding: 14px;
    margin-bottom: 10px;
}


/* Preguntas y respuestas legibles */
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"],
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] p,
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] li,
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] strong,
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] h1,
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] h2,
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] h3 {
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
    opacity: 1 !important;
    font-size: 18px !important;
    line-height: 1.65 !important;
}
[data-testid="stChatMessage"] a {
    color: #93C5FD !important;
    -webkit-text-fill-color: #93C5FD !important;
}
/* Mensajes de espera y carga */
[data-testid="stSpinner"],
[data-testid="stSpinner"] *,
[data-testid="stStatusWidget"],
[data-testid="stStatusWidget"] * {
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
    opacity: 1 !important;
}
[data-testid="stSpinner"] {
    background: #263F5C !important;
    border-radius: 10px;
    padding: 8px 12px;
}

/* Entrada de preguntas: fondo claro uniforme y letras grandes.
   No cambiamos los contenedores ni la funcionalidad de Streamlit. */
[data-testid="stChatInput"] {
    background: #F8FAFC !important;
    border: 2px solid #8BB3DB !important;
    border-radius: 20px !important;
    box-shadow: 0 4px 16px rgba(0, 0, 0, .16) !important;
}
[data-testid="stChatInput"]:focus-within {
    border-color: #3B82F6 !important;
}
/* Texto introducido: oscuro y de 19px para contrastar con el fondo claro. */
[data-testid="stChatInput"] textarea,
[data-testid="stChatInput"] [contenteditable="true"],
[data-testid="stChatInput"] [role="textbox"],
[data-testid="stChatInput"] [data-testid="stChatInputTextArea"],
[data-testid="stChatInput"] [contenteditable="true"] p,
[data-testid="stChatInput"] [contenteditable="true"] span,
[data-testid="stChatInput"] [role="textbox"] p {
    background: transparent !important;
    color: #15243B !important;
    -webkit-text-fill-color: #15243B !important;
    caret-color: #15243B !important;
    font-size: 19px !important;
    line-height: 1.5 !important;
    opacity: 1 !important;
}
/* Indicaciones antes de escribir. */
[data-testid="stChatInput"] textarea::placeholder,
[data-testid="stChatInput"] [data-placeholder]::before,
[data-testid="stChatInput"] [data-placeholder]::after,
[data-testid="stChatInput"] .is-editor-empty::before,
[data-testid="stChatInput"] .is-empty::before {
    color: #61748A !important;
    -webkit-text-fill-color: #61748A !important;
    opacity: 1 !important;
}
[data-testid="stChatInput"] button {
    background: #3B82F6 !important;
    border-radius: 50% !important;
    color: #FFFFFF !important;
}
[data-testid="stChatInput"] button svg {
    color: #FFFFFF !important;
    stroke: #FFFFFF !important;
}

/* Centrado del input: sólo se limita el ancho del elemento,
   no el del contenedor fijo de Streamlit. */
[data-testid="stChatInput"] {
    width: 80% !important;
    max-width: 850px !important;
    margin-inline: auto !important;
}
@media (max-width: 700px) {
    [data-testid="stChatInput"] {
        width: 100% !important;
    }
    .rag-header {
        padding: 20px;
    }
}

/* Botones normales */
.stButton > button {
    background: #315A85;
    color: #FFFFFF;
    border: 1px solid #5688BD;
    border-radius: 10px;
}
.stButton > button:hover {
    background: #4173A5;
    color: #FFFFFF;
    border-color: #74B2FF;
}
</style>
""",
    unsafe_allow_html=True,
)


@st.cache_resource(show_spinner=False)
def iniciar_agente():
    """Carga el índice existente y construye la cadena RAG una sola vez."""
    vector_store = cargar_indice()
    return crear_cadena_rag(vector_store)


st.markdown(
    """
<div class="rag-header">
  <div class="rag-title">🤖 Asistente Inteligente RAG</div>
  <p class="rag-subtitle">
    Consulta tus documentos PDF con Gemini, LangChain y FAISS.
  </p>
</div>
""",
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("⚙️ Configuración")
    st.subheader("🧠 Tecnología del agente")
    st.markdown("**Modelo de lenguaje:** Gemini 3.8 Flash")
    st.markdown("**Modelo de embeddings:** Gemini Embedding 001")
    st.markdown("**Base vectorial:** FAISS")
    st.divider()
    st.info(
        "🔒 La reconstrucción del índice está reservada al administrador "
        "porque puede consumir cuota de la API de Gemini."
    )
    if st.button("🗑️ Limpiar conversación", use_container_width=True):
        st.session_state.mensajes = []
        st.rerun()

if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

try:
    with st.spinner("Cargando documentos y preparando el agente..."):
        cadena_rag = iniciar_agente()
except Exception:
    st.error(
        "No fue posible iniciar el agente. Comprueba que el índice FAISS "
        "ya exista y que la configuración de Gemini sea correcta."
    )
    st.stop()

# Indicador visual: se muestra solo si el agente inició sin excepción.
with st.sidebar:
    st.success("🟢 Asistente conectado")

for mensaje in st.session_state.mensajes:
    with st.chat_message(mensaje["rol"]):
        st.markdown(mensaje["contenido"])

# Entrada nativa y funcional de Streamlit. No reemplazar por HTML.
pregunta = st.chat_input("Escribe tu pregunta sobre los documentos...")

if pregunta and pregunta.strip():
    st.session_state.mensajes.append({"rol": "user", "contenido": pregunta})
    with st.chat_message("user"):
        st.markdown(pregunta)

    with st.chat_message("assistant"):
        with st.spinner("Consultando documentos..."):
            try:
                respuesta = consultar_rag(pregunta, cadena_rag)
            except Exception:
                respuesta = None
                st.error(
                    "No se pudo completar la consulta. Revisa la conexión "
                    "y los registros de la aplicación."
                )
            else:
                st.markdown(respuesta)

    if respuesta is not None:
        st.session_state.mensajes.append(
            {"rol": "assistant", "contenido": respuesta}
        )
