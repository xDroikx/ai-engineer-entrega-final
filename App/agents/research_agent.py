import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, ToolMessage
from App.rag import buscar_en_base_de_conocimiento

load_dotenv()

RESEARCHER_PROMPT = """Eres el Agente Investigador especializado en recuperación de información corporativa (RAG).
Tu objetivo es buscar información precisa y oficial en la base de conocimiento utilizando la herramienta 'buscar_en_base_de_conocimiento'.
Si encuentras información en la base de conocimiento, responde de forma clara citando las normativas o datos encontrados.
Si la información no existe en la base de conocimiento, indícalo expresamente."""

def research_node(state):
    messages = state.get("messages", [])
    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("GROQ_API_KEY")
    model_name = os.getenv("OPENAI_MODEL_NAME") or "llama-3.1-8b-instant"
    
    tools = [buscar_en_base_de_conocimiento]
    tools_dict = {t.name: t for t in tools}
    
    llm = ChatGroq(
        model=model_name,
        groq_api_key=api_key,
        temperature=0
    ).bind_tools(tools)
    
    prompt_messages = [SystemMessage(content=RESEARCHER_PROMPT)] + messages
    response = llm.invoke(prompt_messages)
    
    if response.tool_calls:
        tool_messages = []
        for call in response.tool_calls:
            tool_func = tools_dict.get(call["name"])
            if tool_func:
                tool_output = tool_func.invoke(call["args"])
                tool_messages.append(
                    ToolMessage(
                        content=str(tool_output),
                        tool_call_id=call["id"],
                        name=call["name"]
                    )
                )
        
        final_prompt = prompt_messages + [response] + tool_messages
        response = llm.invoke(final_prompt)

    return {
        "messages": [response],
        "sender": "researcher"
    }

research_agent = research_node
researcher_node = research_node