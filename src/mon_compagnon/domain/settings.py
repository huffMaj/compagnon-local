"""
Les réglages de l'application (moteur, génération, agent).
"""
from __future__ import annotations

import os

from pydantic import BaseModel, Field


def _default_threads() -> int:
    return max(1, os.cpu_count() or 4)


class LLMSettings(BaseModel):
    """Réglages du moteur llama-server."""
    instruct_model: str = "Mistral-7B-Instruct-v0.3-Q4_K_M.gguf"
    n_ctx: int = Field(4096, ge=512, le=262144)
    n_threads: int = Field(default_factory=_default_threads, ge=1)
    n_gpu_layers: int = Field(0, ge=-1)
    server_host: str = "127.0.0.1"
    server_port: int | None = None


class GenerationSettings(BaseModel):
    """Réglages de la génération de texte."""
    temperature: float = Field(0.35, ge=0.0, le=2.0)
    max_tokens: int = Field(1024, ge=16, le=8192)


class AgentSettings(BaseModel):
    """Réglages de la boucle agentique."""
    max_tool_iterations: int = Field(10, ge=1, le=50)
    compression_ratio: float = Field(0.70, ge=0.1, le=0.95)


class AppSettings(BaseModel):
    """Tous les réglages réunis."""
    llm: LLMSettings = Field(default_factory=LLMSettings)
    generation: GenerationSettings = Field(default_factory=GenerationSettings)
    agent: AgentSettings = Field(default_factory=AgentSettings)
