"""LangGraph pipeline definition."""
from langgraph.graph import StateGraph, END
from src.models import PipelineState
from src.agents.preprocessor import normalize_lead
from src.agents.embedder import embed_lead
from src.agents.retriever import retrieve_similar_leads
from src.agents.scorer import score_lead
from src.agents.validator import validate_and_finalize


MAX_RETRIES = 2


def should_retry(state: PipelineState) -> str:
    """Decide whether to retry scoring or end."""
    if state.error and state.retry_count < MAX_RETRIES:
        return "retry"
    return "end"


def build_pipeline() -> StateGraph:
    graph = StateGraph(PipelineState)

    graph.add_node("preprocess", normalize_lead)
    graph.add_node("embed", embed_lead)
    graph.add_node("retrieve", retrieve_similar_leads)
    graph.add_node("score", score_lead)
    graph.add_node("validate", validate_and_finalize)

    graph.set_entry_point("preprocess")
    graph.add_edge("preprocess", "embed")
    graph.add_edge("embed", "retrieve")
    graph.add_edge("retrieve", "score")
    graph.add_edge("score", "validate")

    graph.add_conditional_edges(
        "validate",
        should_retry,
        {"retry": "score", "end": END},
    )

    return graph.compile()


pipeline = build_pipeline()
