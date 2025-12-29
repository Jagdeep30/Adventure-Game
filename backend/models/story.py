from sqlalchemy import Column, Integer, DateTime, ForeignKey, String, Boolean, JSON, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from db.database import Base


class Story(Base):
    __tablename__ = "story"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    session_id = Column(Integer, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    nodes = relationship("StoryNode", back_populates="story")


class StoryNode(Base):
    __tablename__ = "story_node"

    id = Column(Integer, primary_key=True, index=True)
    story_id = Column(Integer, ForeignKey("story.id"), index=True)
    content = Column(String)
    is_ending = Column(Boolean, default=False)
    is_root = Column(Boolean, default=False)
    is_winning_ending = Column(Boolean, default=False)
    options = Column(JSON, default=list)

    story = relationship("Story", back_populates="nodes")

