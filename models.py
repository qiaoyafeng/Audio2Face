import datetime

from pydantic import BaseModel

from sqlalchemy import Boolean, Column, Integer, String, TEXT, DateTime, func, TIMESTAMP
from database import Base


class VideoTask(Base):
    __tablename__ = "video_task"
    uuid = Column(String(100), primary_key=True, unique=True, index=True)
    info = Column(TEXT)
    background_url = Column(String(500))
    video_url = Column(String(500), default="")
    create_time = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )
    update_time = Column(TIMESTAMP(timezone=True), default=None, onupdate=func.now())


class ChatInput:
    """
    ChatInput
    """

    def __init__(self, in_type: int, text: dict, asr: dict):
        self.in_type = in_type
        self.text = {}
        self.asr = {}


class ChatOutput:
    """
    ChatOutput
    """

    def __init__(self, answer: dict, tts: dict, face: dict, motion: dict):
        self.answer = {}
        self.tts = {}
        self.face = {}
        self.motion = {}


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(32), unique=True, index=True)
    hashed_password = Column(String(32))
    is_active = Column(Boolean, default=True)
