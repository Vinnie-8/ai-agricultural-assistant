from functools import lru_cache

from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import create_react_agent

from app.config import settings
from app.prompts.system_prompt import SYSTEM_PROMPT
from app.tools.knowledge_base_tool import search_knowledge_base
from app.tools.weather_tool import get_weather_forecast

# NOTE: InMemorySaver keeps conversation history only for the lifetime of
# the running process. This is fine for local development. For production,
# swap in a persistent checkpointer (e.g. a Postgres-backed one) so chat
# history survives restarts and works across multiple worker processes.
_checkpointer = InMemorySaver()


@lru_cache(maxsize=1)
def get_agent():
    llm = ChatOpenAI(
    model=settings.OPENAI_MODEL,
    api_key=settings.OPENAI_API_KEY,
    temperature=0.3,

    )

    return create_react_agent(
        model=llm,
        tools=[search_knowledge_base,get_weather_forecast],
        prompt=SYSTEM_PROMPT,
        checkpointer=_checkpointer,
    )


def run_chat(message: str, session_id: str, location: str | None = None, diagnosis_context: str | None = None) -> str:
    """
    Send a farmer's message to the agent and return its reply.

    Args:
        message: The farmer's chat message.
        session_id: A stable identifier for this conversation (e.g. the
            backend's chat_history session/thread id), used so the agent
            remembers prior turns in this conversation.
        diagnosis_context: Optional short string describing the current
            diagnosis (e.g. "Crop: Maize, Disease: Common Rust,
            Confidence: 0.97"), injected so the agent can ground its
            advice in the specific diagnosis without the frontend having
            to repeat it in every message.
    """
    agent = get_agent()

    user_content = message
    if diagnosis_context:
        user_content = f"[Diagnosis context: {diagnosis_context}]\n\n{message}"
    if location:
        user_content = f"[Farmer location/IP: {location}]\n\n{user_content}"


    config = {"configurable": {"thread_id": session_id}}

    result = agent.invoke(
        {"messages": [{"role": "user", "content": user_content}]},
        config=config,
    )

    final_message = result["messages"][-1]
    return final_message.content
