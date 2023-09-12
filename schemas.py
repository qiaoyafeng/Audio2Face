from datetime import datetime
from pydantic import BaseModel


class VideoTask(BaseModel):
    """
    响应模型：
    并且设置orm_mode与之兼容
    """

    uuid: str
    info: str
    background_url: str
    video_url: str
    create_time: str
    update_time: str

    class Config:
        orm_mode = True


class VideoTaskCreateRequest(BaseModel):
    info: str
    speaker_id: int = 0
    gender: int = 0
    background_url: str


class VideoTaskCreateResponse(BaseModel):
    uuid: str
    info: str
    background_url: str
    video_url: str
    create_time: datetime
    update_time: datetime


class VideoTaskUpdateRequest(BaseModel):
    uuid: str
    video_url: str
