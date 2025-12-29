import uuid
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Cookie, Response, BackgroundTasks
from sqlalchemy.orm import Session

from db.database import get_session, SessionLocal
from models.story import Story, StoryNode
from models.job import StoryJob
from schemas.story import (
    CompleteStoryResponse, CompleteStoryNodeResponse, CreateStoryRequest
)
from schemas.job import StoryJobResponse
from core.story_generator import StoryGenerator


router = APIRouter(prefix="/story", tags=["Stories"])

def get_session_id(session_id: Optional[str] = Cookie(None)):
    if not session_id:
        session_id = str(uuid.uuid4())
    return session_id


@router.post("/create", response_model=StoryJobResponse)
def create_story(
    request: CreateStoryRequest,
    background_tasks: BackgroundTasks,
    response: Response,
    session_id: str = Depends(get_session_id),
    db: Session = Depends(get_session)
):
    # set cookie
    response.set_cookie("session_id", session_id, httponly=True)

    job_id = uuid.uuid4()

    story_job = StoryJob(
        job_id = job_id,
        session_id = session_id,
        theme = request.theme,
        status = "pending"
    )

    db.add(story_job)
    db.commit()

    # add background task to generate story
    background_tasks.add_task(generate_story_task, job_id, session_id, request.theme)


    return story_job

def generate_story_task(job_id: uuid.UUID, session_id: str, theme: str):
    db = SessionLocal()

    try:
        job = db.query(StoryJob).filter(StoryJob.job_id == job_id).first()

        try:
            job.status = "processing"
            db.commit()

            story = StoryGenerator.generate_story(db, session_id, theme)

            job.story_id = story.id
            job.status = "completed"
            job.completed_at = datetime.now()
            db.commit()

        except Exception as e:
            job.status = "failed"
            job.completed_at = datetime.now()
            job.error = str(e)
            db.commit()

    finally:
        db.close()


@router.get("/{story_id}/complete", response_model=CompleteStoryResponse)
def get_complete_story(story_id: int, db: Session = Depends(get_session)):
    story = db.query(Story).filter(Story.id == story_id).first()

    if not story:
        raise HTTPException(detail="Story not found", status_code=404)
    
    # parse story
    complete_story = build_complete_story_tree(db, story)

    return complete_story

def build_complete_story_tree(db: Session, story: Story) -> CompleteStoryResponse:
    nodes = db.query(StoryNode).filter(StoryNode.story_id == story.id).all()

    node_dict = {}

    for node in nodes:
        node_response = CompleteStoryNodeResponse(
            content=node.content,
            is_ending=node.is_ending,
            is_winning_ending=node.is_winning_ending,
            options=node.options,
            id=node.id
        )

        node_dict[node.id] = node_response

    root = next((node for node in nodes if node.is_root), None)

    if not root:
        raise HTTPException(status_code=500, detail="Story root not found")
    
    story_response = CompleteStoryResponse(
        id=story.id,
        title=story.title,
        session_id=story.session_id,
        created_at=story.created_at,
        root_node=root,
        all_nodes=node_dict
    )

    return story_response