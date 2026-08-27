"""
NLP API router — POST /api/v1/nlp/analyze

Accepts text, runs the NLP pipeline, and returns structured results.
Raw user text is never logged or stored.
"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.schemas.nlp import NLPAnalyzeRequest, NLPAnalyzeResponse
from app.nlp.service import run_nlp_pipeline
from app.core.exceptions import AIException
from app.core.logging import logger

router = APIRouter()


@router.post(
    "/nlp/analyze",
    response_model=NLPAnalyzeResponse,
    summary="Analyze text with the NLP pipeline",
    description=(
        "Accepts a text payload and runs it through the Aurevia NLP pipeline. "
        "Returns language detection, preprocessing metrics, tokenization, "
        "NLP model indicators, and embedding metadata. "
        "In DEMO_MODE all steps complete without external AI services."
    ),
    responses={
        200: {"description": "NLP analysis complete"},
        422: {"description": "Validation error — empty/missing/oversized text"},
        500: {"description": "Internal pipeline error"},
    },
)
async def nlp_analyze(request: NLPAnalyzeRequest) -> NLPAnalyzeResponse:
    """
    POST /api/v1/nlp/analyze

    Run the full NLP analysis pipeline on the submitted text.
    """
    logger.info("NLP analyze endpoint called")
    result = run_nlp_pipeline(request.text)
    return result
