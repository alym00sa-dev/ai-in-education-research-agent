"""Configuration schema for the Open Deep Research v2 pipeline."""

import os
from typing import Optional

from pydantic import BaseModel, Field


class Configuration(BaseModel):
    """Runtime configuration for the research pipeline."""

    model: str = Field(
        default="gpt-5.4-mini-2026-03-17",
        description="LLM model to use for all pipeline nodes",
    )
    report_model: str = Field(
        default="",
        description="LLM model for final report generation (Pass 1 + Pass 2). Falls back to model if empty.",
    )
    model_max_tokens: int = Field(
        default=16000,
        description="Max tokens for LLM responses",
    )
    research_iterations: int = Field(
        default=2,
        description="Number of research iterations (min 1, max 4). Each iteration after the first includes a critique cycle.",
        ge=1,
        le=4,
    )
    max_concurrent_researchers: int = Field(
        default=5,
        description="Maximum number of parallel researchers per supervisor dispatch",
    )
    max_sweep_cycles: int = Field(
        default=2,
        description="Maximum number of sweep cycles per researcher before forcing compress",
    )
    tavily_budget: int = Field(
        default=8,
        description="Maximum Tavily API calls across the full run",
    )
    serp_budget: int = Field(
        default=2,
        description="Maximum Google Scholar (SerpAPI) calls across the full run",
    )
    enable_pdf_extraction: bool = Field(
        default=True,
        description="Whether to attempt full-text PDF extraction for filtered papers",
    )
    allow_clarification: bool = Field(
        default=True,
        description="Whether education_discovery may ask the user for clarification",
    )
    max_sources: int = Field(
        default=30,
        description="Maximum sources to include in the final bibliography",
    )
    session_id: str = Field(
        default="",
        description="Frontend job ID — when set, pipeline saves output files to output/final-test/<session_id>/",
    )

    @classmethod
    def from_runnable_config(cls, config=None) -> "Configuration":
        """Build Configuration from a LangGraph RunnableConfig."""
        configurable = config.get("configurable", {}) if config else {}
        field_names = list(cls.model_fields.keys())
        values = {
            k: os.environ.get(k.upper(), configurable.get(k))
            for k in field_names
        }
        return cls(**{k: v for k, v in values.items() if v is not None})
