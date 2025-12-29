from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import Settings, get_settings
from routers.job import router as job_router
from routers.story import router as story_router
from db.database import create_tables

create_tables()


app = FastAPI(
    title="Personality Test",
    description="",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

settings: Settings = get_settings()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]    
)

@app.get("/health")
def health_check():
    return "Status health"

app.include_router(job_router, prefix=settings.API_PREFIX)
app.include_router(story_router, prefix=settings.API_PREFIX)

arr = ["adf", "fasdf"]