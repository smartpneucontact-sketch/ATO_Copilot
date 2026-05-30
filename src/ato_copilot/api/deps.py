from __future__ import annotations

from dataclasses import dataclass

from ato_copilot.agents import ATORequestAgent
from ato_copilot.config import Settings, get_settings
from ato_copilot.llm import LLMClient
from ato_copilot.observability import Tracer
from ato_copilot.rag.ingest import build_retriever
from ato_copilot.rag.retriever import Retriever
from ato_copilot.tools import build_ato_tools


@dataclass
class AppState:
    settings: Settings
    retriever: Retriever
    tracer: Tracer
    ato_agent: ATORequestAgent


def build_app_state() -> AppState:
    settings = get_settings()
    retriever = build_retriever()
    llm = LLMClient(api_key=settings.anthropic_api_key, model=settings.model, use_mock=settings.use_mock_llm)
    tracer = Tracer(settings.traces_dir)
    ato_agent = ATORequestAgent(
        llm=llm, tools=build_ato_tools(retriever), tracer=tracer, max_steps=settings.max_agent_steps,
    )
    return AppState(settings=settings, retriever=retriever, tracer=tracer, ato_agent=ato_agent)
