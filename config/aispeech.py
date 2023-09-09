import json


class AiSpeechConfig:
    """
    AiSpeechConfig
    """

    def __init__(self, filename: str = "aispeech.json"):
        self.filename = filename

    def config_dict(self):
        return json.load(self.filename)

