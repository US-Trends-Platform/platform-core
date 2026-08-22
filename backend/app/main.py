from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers import gdp, unemployment

app = FastAPI(
    title="US Trends Platform API",
    version="0.1.0",
    description="Evidence-first historical data observatory - internal API layer.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(gdp.router, prefix=settings.api_v1_prefix)
app.include_router(unemployment.router, prefix=settings.api_v1_prefix)


@app.get("/health")
def health():
    return {"status": "ok", "env": settings.env}
