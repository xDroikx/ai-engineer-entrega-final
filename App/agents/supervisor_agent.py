import os
from typing import Literal
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, AIMessage

load_dotenv()

class RouteResponse(BaseModel):
    next: Literal["Investigador", "Analista", "FINALIZAR"] = Field(
        ...,
        description="Próximo agente a ejecutar: 'Investigador', 'Analista' o 'FINALIZAR' cuando la consulta ya fue investigada y analizada."
    )

SUPERVISOR_PROMPT = """Eres el Supervisor de un sistema multi-agente de producción.
Tu función es coordinar el flujo de forma ordenada:
1. Si la consulta acaba de llegar y no hay datos del Investigador en el historial, delega en 'Investigador'.
2. Si el Investigador ya consultó la base de datos o aportó normativas corporativas, delega en 'Analista'.
3. Si el Analista ya intervino o ya existe una respuesta analítica completa a la consulta, tu OBLIGACIÓN es responder 'FINALIZAR' para proceder a la aprobación final.
No vuelvas a llamar al Investigador si ya hay una respuesta en el historial.
"""

def supervisor_node(state):
    messages = state.get("messages", [])
    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("GROQ_API_KEY")
    model_name = os.getenv("OPENAI_MODEL_NAME") or "llama-3.1-8b-instant"

    # Freno determinista contra recursión infinita
    ai_messages = [m for m in messages if isinstance(m, AIMessage) or getattr(m, "type", "") == "ai"]
    
    # Si ya hay 2 o más respuestas de agentes, cerramos el ciclo hacia FINALIZAR
    if len(ai_messages) >= 2:
        return {"next": "FINALIZAR"}

    # Si ya respondió el Investigador, delegamos en el Analista
    if len(ai_messages) == 1:
        first_content = getattr(ai_messages, "content", "") or ""
        if len(first_content) > 15:
            return {"next": "Analista"}

    llm = ChatGroq(
        model=model_name,
        groq_api_key=api_key,
        temperature=0
    )

    prompt_messages = [SystemMessage(content=SUPERVISOR_PROMPT)] + messages
    
    try:
        structured_llm = llm.with_structured_output(RouteResponse)
        decision = structured_llm.invoke(prompt_messages)
        next_step = decision.next
    except Exception:
        response = llm.invoke(prompt_messages)
        content = str(response.content).lower()
        if "analista" in content:
            next_step = "Analista"
        elif "investigador" in content and len(ai_messages) == 0:
            next_step = "Investigador"
        else:
            next_step = "FINALIZAR"

    # Normalización exacta compatible con route_next de graph.py
    if str(next_step).lower() == "investigador" and len(ai_messages) == 0:
        final_route = "Investigador"
    elif str(next_step).lower() == "analista" and len(ai_messages) <= 1:
        final_route = "Analista"
    else:
        final_route = "FINALIZAR"

    return {"next": final_route}

# Alias de compatibilidad
supervisor_agent = supervisor_node