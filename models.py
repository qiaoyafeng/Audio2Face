from pydantic import BaseModel


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


class VideoTaskItem(BaseModel):
    info: str
    speaker_id: int = 0
    gender: int = 0
    background_url: str
