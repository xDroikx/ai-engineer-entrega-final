import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage

load_dotenv()

ANALYST_PROMPT = """Eres el Agente Analista especializado en evaluación cuantitativa, análisis de riesgo y síntesis estratégica.
Tu objetivo es tomar los hallazgos y datos recuperados por el investigador y generar un análisis claro, estructurado y accionable.
- Evalúa si las solicitudes superan umbrales normativos (ejemplo: límites de presupuesto de USD $5.000).
- Si detectas una acción crítica o un monto que excede los límites, indica claramente que se requiere APROBACIÓN HUMANA.
- Sé conciso, profesional y riguroso."""

def analyst_node(state):
    messages = state.get("messages", [])
    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("GROQ_API_KEY")
    model_name = os.getenv("OPENAI_MODEL_NAME") or "llama-3.1-8b-instant"

    llm = ChatGroq(
        model=model_name,
        groq_api_key=api_key,
        temperature=0
    )

    prompt_messages = [SystemMessage(content=ANALYST_PROMPT)] + messages
    response = llm.invoke(prompt_messages)

    return {
        "messages": [response],
        "sender": "analyst"
    }

analyst_agent = analyst_node