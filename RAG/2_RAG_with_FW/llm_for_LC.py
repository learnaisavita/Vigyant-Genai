"""LangChain LLM access
 LangChain,  needs a chat-model OBJECT (a Runnable) so it can sit
in a 'prompt | model | parser' pipeline. So this module exposes a single factory,
get_chat_model(), selected from the same .env as the rest of the course.

Configure in a .env at the project root (copy .env.example):

    PROVIDER=groq            # gemini | groq | ollama   (default: groq)
    MODEL_NAME=                # optional; blank uses the per-provider default
    GEMINI_API_KEY=...         # only if PROVIDER=gemini
    GROQ_API_KEY=...           # only if PROVIDER=groq

Install the matching LangChain integration for your provider:

    pip install langchain langchain-ollama          # PROVIDER=ollama (default)
    pip install langchain langchain-groq            # PROVIDER=groq
    pip install langchain langchain-google-genai    # PROVIDER=gemini
"""

from __future__ import annotations
import logging
import os

log = logging.getLogger("course.llm")
log.addHandler(logging.NullHandler())

# Load .env so PROVIDER / MODEL_NAME / API keys appear in os.environ.
try:
    from dotenv import load_dotenv, find_dotenv
    load_dotenv(find_dotenv())
except Exception:
    pass

DEFAULT_MODEL = {
    
    "gemini": "gemini-3.5-flash-lite",
    "groq": "openai/gpt-oss-20b",
    "ollama": "llama3.2",
}

PROVIDER = os.getenv("PROVIDER", "groq").lower()
MODEL_NAME = os.getenv("MODEL_NAME") or DEFAULT_MODEL.get(PROVIDER, "openai/gpt-oss-20b")

# Map our PROVIDER names to LangChain's init_chat_model provider ids.
_PROVIDER_TO_LC = {"ollama": "ollama", "groq": "groq", "gemini": "google_genai"}


def get_chat_model(provider=None, model=None, temperature=0.2):
    """Return a LangChain chat model (a Runnable) for use in LCEL chains.

    Uses LangChain's init_chat_model so one call returns the right one
    (ChatOllama / ChatGroq / ChatGoogleGenerativeAI) for the configured provider.
    """
    from langchain.chat_models import init_chat_model
    provider = (provider or PROVIDER).lower()
    if model is None:
        model = MODEL_NAME if provider == PROVIDER else DEFAULT_MODEL[provider]
    return init_chat_model(model, model_provider=_PROVIDER_TO_LC[provider], temperature=temperature)
