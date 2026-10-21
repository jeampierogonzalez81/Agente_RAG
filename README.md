Agente RAG con Gemini, LangChain, FAISS y Streamlit
Asistente de consulta de documentos PDF mediante Retrieval-Augmented Generation (RAG). Recupera fragmentos relevantes de los documentos y los utiliza como contexto para generar respuestas con Google Gemini.
Estado del proyecto: versión actual migrada de Ollama local a Gemini. La interfaz es una aplicación Streamlit. El archivo rag_ollama_respaldo.py es un respaldo local y no es necesario para ejecutar esta versión.

Tecnologías
- Python: lenguaje principal.
- Streamlit: interfaz web conversacional.
- LangChain: procesamiento de documentos y cadena RAG.
- Google Gemini: modelo de lenguaje y generación de embeddings mediante la API.
- FAISS: índice vectorial local para recuperar fragmentos.
- PyPDF: lectura de documentos PDF.
- python-dotenv: configuración local mediante variables de entorno.
En la configuración actual se utiliza el modelo de embeddings gemini-embedding-001. El modelo de chat se configura en rag.py; consulta ese archivo para conocer su identificador exacto.
¿Cómo funciona?
1. Se leen los documentos PDF de la carpeta documentos/.
2. El contenido se divide en fragmentos.
3. Gemini genera representaciones vectoriales (embeddings) de esos fragmentos.
4. FAISS almacena el índice localmente.
5. Ante una pregunta, el recuperador selecciona los fragmentos más relevantes.
6. El modelo de Gemini genera una respuesta a partir del contexto recuperado.
7. Streamlit muestra las preguntas, respuestas y el historial de la sesión.
Estructura principal
Agente_RAG/
├── app.py                 # Interfaz Streamlit
├── rag.py                 # Carga del índice y lógica RAG
├── documentos/            # Documentos PDF de consulta
├── requirements.txt       # Dependencias
├── README.md              # Documentación
├── .gitignore
├── .env                   # Clave de API local (no publicar)
├── cache_embeddings/      # Caché local (ignorada)
└── faiss_db_gemini/       # Índice vectorial local (ignorado)
Las carpetas de caché e índice pueden aparecer después de generar los embeddings. No se distribuyen necesariamente con el repositorio.
Instalación local (Ubuntu / Linux)
1. Clonar el proyecto
git clone https://github.com/jeampierogonzalez81/Agente_RAG.git
cd Agente_RAG
2. Crear y activar el entorno virtual
python3 -m venv .venv
source .venv/bin/activate
3. Instalar dependencias
python -m pip install -r requirements.txt
4. Configurar la API de Gemini
Crea un archivo .env en la raíz del proyecto y añade la variable que consume rag.py. Si tu implementación usa GOOGLE_API_KEY, el formato es:
GOOGLE_API_KEY=tu_clave_aqui
Comprueba el nombre exacto de la variable en rag.py antes de ejecutar. Nunca publiques el valor real ni incluyas .env en un commit.
5. Preparar el índice FAISS
Coloca los PDF autorizados en documentos/. Para generar o actualizar el índice local de manera explícita:
python -c "from rag import reconstruir_indice; reconstruir_indice()"
Este proceso puede consumir cuota de la API de Gemini. La primera generación puede tardar según la cantidad de documentos y los límites de la API.
6. Iniciar la interfaz
streamlit run app.py
Abre la dirección local indicada por Streamlit (habitualmente http://localhost:8501).
Funcionalidades de la interfaz
- Consultas en lenguaje natural sobre los PDF cargados.
- Historial de preguntas y respuestas durante la sesión.
- Botón para limpiar la conversación.
- Interfaz oscura con textos de alto contraste.
- Campo de entrada claro con tipografía ampliada.
- Barra lateral con información de tecnologías e indicador visual «Asistente conectado» después de inicializar el agente.
El indicador significa que la inicialización terminó sin excepción; no es una comprobación continua de disponibilidad de Gemini.

Por precaución, la interfaz pública no ofrece un botón para reconstruir el índice. Esa tarea queda reservada a la ejecución manual del administrador.
Seguridad y costos
- .env y los entornos virtuales están excluidos de Git.
- cache_embeddings/, faiss_db/ y faiss_db_gemini/ se mantienen fuera de los nuevos commits.
- Las llamadas de generación de texto y embeddings a Gemini pueden consumir cuota y tener costos, según el plan y el uso.
- Antes de desplegar la aplicación, revisa qué hace cargar_indice() si el índice no existe: no debe reconstruirlo automáticamente sin que lo hayas previsto.
- No subas documentos confidenciales sin autorización.
- El índice local no se recrea automáticamente en otro equipo solo por clonar este repositorio; debes prepararlo o distribuirlo mediante un mecanismo seguro.
Notas sobre la versión anterior
El proyecto comenzó como una práctica con Ollama (llama3.2:1b y all-minilm). La versión documentada aquí utiliza Gemini y una interfaz Streamlit; por tanto, Ollama ya no es un requisito de ejecución de esta versión.
Próximas mejoras posibles
- Manejo más explícito del índice faltante en entornos de despliegue.
- Referencias a las fuentes documentales utilizadas en cada respuesta.
- Control de acceso y límites de consultas para despliegues públicos.
- Pruebas automatizadas de la cadena RAG.