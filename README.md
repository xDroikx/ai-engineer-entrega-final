# Sistema Multi-Agente Asíncrono de Producción con LangGraph, Redis y Arize Phoenix

Sistema de inteligencia artificial de grado de producción que implementa una arquitectura **Multi-Agente con Patrón Supervisor**, recuperación contextual (**RAG**) sobre base de datos vectorial, orquestación asíncrona mediante **FastAPI + BackgroundTasks**, persistencia de estado con **Redis Checkpointer** y un punto de control crítico **Human-in-the-Loop (HITL)**, con observabilidad completa instrumentada en **Arize Phoenix**.

---

## Arquitectura del Sistema

El sistema implementa un grafo cíclico dirigido con **LangGraph** coordinado por un agente **Supervisor** que evalúa dinámicamente qué agente especialista debe intervenir según la consulta:

                  +----------------------+
                  ¦   Entrada Usuario    ¦
                  +----------------------+
                             ¦
                             ?
                  +----------------------+
                  ¦      Supervisor      ¦?--------+
                  +----------------------+         ¦
                             ¦                     ¦
            +---------------------------------+    ¦
            ¦                                 ¦    ¦
 +----------------------+          +----------------------+
 ¦  Agente Investigador ¦          ¦   Agente Analista    ¦
 ¦      (RAG Tool)      ¦          ¦ (Cálculo Financiero) ¦
 +----------------------+          +----------------------+
            ¦                                 ¦
            +---------------------------------+
                             ¦ (Requiere confirmación crítica)
                             ¦
                 +-------------------------+
                 ¦    AprobacionHumana     ¦  <-- [HITL: interrupt_before]
                 ¦  (Pausa en RedisSaver)  ¦
                 +-------------------------+
                             ¦ (POST /tasks/{id}/approve)
                             ¦
                 +-------------------------+
                 ¦          FIN            ¦
                 +-------------------------+

### Agentes y Componentes Clave:
1. **Supervisor**: Coordina el razonamiento y delega tareas a los agentes especialistas utilizando modelos LLM de alto rendimiento a través de **OpenRouter** (`openai/gpt-oss-120b`).
2. **Investigador (RAG)**: Recupera contexto normativo y corporativo almacenado en **ChromaDB**.
3. **Analista**: Ejecuta cálculos determinísticos sobre presupuestos, costos y márgenes de negocio.
4. **Human-in-the-Loop (AprobacionHumana)**: Interrupción nativa configurada en el grafo (`interrupt_before=["AprobacionHumana"]`) que pausa la ejecución cuando se detectan acciones críticas o montos elevados, guardando el checkpoint en Redis hasta la confirmación de un operador humano.
5. **Persistencia**: Estado persistido con `MemorySaver` / `RedisSaver`, permitiendo consultar el historial o reanudar tareas entre reinicios del servicio.

---

##  Estructura del Repositorio

```text
+-- App/
¦   +-- __init__.py
¦   +-- main.py            # API FastAPI asíncrona (POST, GET y /approve)
¦   +-- graph.py           # Grafo de agentes en LangGraph con interrupt_before
¦   +-- worker.py          # Gestor de tareas y almacenamiento de estado
¦   +-- observability.py   # Instrumentación de OpenTelemetry y Arize Phoenix
¦   +-- clients.py         # Clientes LLM y embeddings asíncronos
¦   +-- schemas.py         # Validación estructurada con Pydantic
+-- screenshots/           # Evidencias de observabilidad y ciclo HITL
¦   +-- accepted.png
¦   +-- paused_for_aprove.png
¦   +-- resumed.png
¦   +-- completed.png
¦   +-- phoenix_metrics_p95.png
¦   +-- phoenix_trace_detail2.png
+-- requirements.txt       # Dependencias del proyecto
+-- .env.example           # Variables de entorno modelo
+-- README.md              # Documentación técnica del sistema
