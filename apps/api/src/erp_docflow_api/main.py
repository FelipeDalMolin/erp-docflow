"""FastAPI application for the ERP DocFlow bootstrap."""

from typing import Literal

from fastapi import FastAPI, status
from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Deterministic response returned by the API healthcheck."""

    status: Literal["ok"]
    service: Literal["erp-docflow-api"]


app = FastAPI(
    title="ERP DocFlow API",
    version="0.1.0",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)


@app.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Check API health",
)
def health() -> HealthResponse:
    """Report that the API process is ready to serve requests."""

    return HealthResponse(status="ok", service="erp-docflow-api")
