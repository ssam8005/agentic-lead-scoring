"""Pinecone RAG retrieval agent."""
from pinecone import Pinecone
from src.models import PipelineState, HistoricalLead
from src.config import get_settings


def retrieve_similar_leads(state: PipelineState) -> PipelineState:
    """Query Pinecone for historically similar leads with their outcomes."""
    settings = get_settings()
    pc = Pinecone(api_key=settings.pinecone_api_key)
    index = pc.Index(settings.pinecone_index_name)

    results = index.query(
        vector=state.embedding,
        top_k=settings.pinecone_top_k,
        include_metadata=True,
    )

    retrieved = []
    for match in results.matches:
        meta = match.metadata
        retrieved.append(HistoricalLead(
            lead_id=meta.get("lead_id", "unknown"),
            industry=meta.get("industry", "Unknown"),
            company_size=int(meta.get("company_size", 0)),
            title=meta.get("title", "Unknown"),
            outcome=meta.get("outcome", "ghosted"),
            days_to_close=meta.get("days_to_close"),
            deal_value=meta.get("deal_value"),
            close_signals=meta.get("close_signals", []),
            objections=meta.get("objections", []),
            similarity_score=round(match.score, 3),
        ))

    state.retrieved_leads = retrieved

    # Build context text for LLM
    context_lines = ["Historical leads similar to this one:"]
    for i, lead in enumerate(retrieved, 1):
        context_lines.append(
            f"{i}. {lead.title} at {lead.company_size}-person {lead.industry} company. "
            f"Outcome: {lead.outcome}. "
            f"Days to close: {lead.days_to_close or 'N/A'}. "
            f"Close signals: {', '.join(lead.close_signals) or 'none'}. "
            f"Objections: {', '.join(lead.objections) or 'none'}. "
            f"Similarity: {lead.similarity_score:.2f}."
        )
    state.context_text = "\n".join(context_lines)
    return state
