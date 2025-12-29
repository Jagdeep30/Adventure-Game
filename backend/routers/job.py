from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from schemas.job import StoryJobResponse
from db.database import get_session
from models.job import StoryJob

router = APIRouter(prefix="/job", tags=["Jobs"])


@router.get("/{job_id}", response_model=StoryJobResponse)
def get_job_status(job_id: UUID, db: Session = Depends(get_session)):
    job = db.query(StoryJob).filter(StoryJob.job_id == job_id).first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return job