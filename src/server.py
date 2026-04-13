"""FastAPI webhook server — receives lead from n8n, returns score."""
import time
from fastapi import FastAPI, HTTPException, Header
from src.models import LeadInput, ScoreResponse, PipelineState
from src.pipeline import pipeline
from src.config import get_settings

app = FastAPI(
    title="Agentic Lead Scoring Engine",
    description="RAG-backed lead intelligence scoring for B2B revenue teams",
    version="1.0.0",
)


@app.get("/health")
def health():
    return {"status": "ok", "service": "agentic-lead-scoring"}


@app.post("/score", response_model=ScoreResponse)
def score_lead(
    lead: LeadInput,
    x_api_secret: str = Header(default=""),
):
    settings = get_settings()
    if settings.api_secret and x_api_secret != settings.api_secret:
        raise HTTPException(status_code=401, detail="Invalid API secret")

    start = time.time()

    state = PipelineState(lead=lead)
    result = pipeline.invoke(state)

    if result.error:
        raise HTTPException(status_code=500, detail=f"Scoring failed: {result.error}")

    elapsed_ms = round((time.time() - start) * 1000)

    return ScoreResponse(
        lead_id=lead.lead_id,
        score=result.final_score,
        tier=result.tier,
        confidence=result.confidence or 0.5,
        reasoning=result.reasoning or "Score based on firmographic signals.",
        recommended_sequence=result.recommended_sequence,
        suggested_angle=result.suggested_angle or "Value-based introduction",
        rules_score=result.rules_score or 0,
        ai_score=result.ai_score or 0,
        retrieved_context_count=len(result.retrieved_leads),
        processing_time_ms=elapsed_ms,
    )


if __name__ == "__main__":
    import uvicorn
    s = get_settings()
    uvicorn.run(app, host=s.server_host, port=s.server_port)
