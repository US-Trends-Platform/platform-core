from fastapi import FastAPI

from app.core.config import settings
from app.routers import metrics, observations

app = FastAPI(
    title="US Trends Platform API",
    version="0.1.0",
    description="Evidence-first historical data observatory — internal API layer (plan §33).",
)

app.include_router(metrics.router, prefix=settings.api_v1_prefix)
app.include_router(observations.router, prefix=settings.api_v1_prefix)


@app.get("/health")
def health():
    return {"status": "ok", "env": settings.env}
