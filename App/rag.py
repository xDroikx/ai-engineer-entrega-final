import os
from langchain_chroma import Chroma
from langchain_core.tools import tool
from langchain_core.embeddings import FakeEmbeddings

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
CHROMA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "chroma_db")

_vectorstore = None

def get_or_create_vectorstore():
    global _vectorstore
    if _vectorstore is not None:
        return _vectorstore

    # Usamos embeddings deterministas locales que no requieren API externa
    embeddings = FakeEmbeddings(size=384)

    # Si ya existe la base local persistente, la cargamos
    if os.path.exists(CHROMA_DIR) and len(os.listdir(CHROMA_DIR)) > 0:
        try:
            _vectorstore = Chroma(
                collection_name="knowledge_base",
                embedding_function=embeddings,
                persist_directory=CHROMA_DIR
            )
            return _vectorstore
        except Exception:
            pass

    # Si no existe, indexamos los archivos en data/
    docs = []
    if os.path.exists(DATA_DIR):
        for fname in os.listdir(DATA_DIR):
            if fname.endswith(".txt") or fname.endswith(".md"):
                fpath = os.path.join(DATA_DIR, fname)
                with open(fpath, "r", encoding="utf-8") as f:
                    docs.append(f.read())

    if not docs:
        docs = ["Base de conocimiento corporativa de prueba."]

    _vectorstore = Chroma.from_texts(
        texts=docs,
        embedding=embeddings,
        collection_name="knowledge_base",
        persist_directory=CHROMA_DIR
    )
    return _vectorstore

@tool
def buscar_en_base_de_conocimiento(query: str) -> str:
    """Busca información oficial en los documentos internos y normativas de la empresa."""
    try:
        vs = get_or_create_vectorstore()
        results = vs.similarity_search(query, k=2)
        if not results:
            return "No se encontró información relevante en los documentos internos."
        return "\n\n".join([doc.page_content for doc in results])
    except Exception as e:
        return f"Error al consultar la base de conocimiento: {str(e)}"