import phoenix as px
from phoenix.otel import register
from openinference.instrumentation.langchain import LangChainInstrumentor

def setup_observability():
    """Inicia Arize Phoenix e instrumenta LangChain/LangGraph sin depender de URLs en el .env."""
    # 1. Levanta la app local en el puerto 6006
    px.launch_app(port=6006)

    # 2. Registra el tracer provider directamente en memoria para el proyecto default
    tracer_provider = register(project_name="default")

    # 3. Instrumenta LangChain conectándolo directamente al tracer_provider
    LangChainInstrumentor().instrument(tracer_provider=tracer_provider)

    print("🔭 Phoenix instrumentado exitosamente en http://localhost:6006/")