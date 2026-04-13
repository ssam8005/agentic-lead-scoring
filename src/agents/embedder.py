"""Embedding agent — converts lead record to vector."""
from openai import OpenAI
from src.models import PipelineState
from src.config import get_settings
import json


def embed_lead(state: PipelineState) -> PipelineState:
    """Generate embedding for the normalized lead record."""
    settings = get_settings()
    client = OpenAI(api_key=settings.openai_api_key)

    # Build text representation for embedding
    lead_text = (
        f"Company: {state.normalized_lead['company']}. "
        f"Industry: {state.normalized_lead['industry']}. "
        f"Title: {state.normalized_lead['title']}. "
        f"Company size: {state.normalized_lead['company_size']} employees. "
        f"Lead source: {state.normalized_lead['lead_source']}. "
        f"Tech stack: {', '.join(state.normalized_lead['tech_stack'])}. "
        f"Funding stage: {state.normalized_lead['funding_stage']}."
    )

    response = client.embeddings.create(
        model=settings.embedding_model,
        input=lead_text,
    )
    state.embedding = response.data[0].embedding
    return state
