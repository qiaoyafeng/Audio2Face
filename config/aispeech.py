import codecs
import json

from config.base import CONF_FOLDER_PATH


class AiSpeechConfig:
    """
    AiSpeechConfig
    """

    def __init__(self, filename: str = "aispeech.json"):
        self.filename = filename
        self.config_file = CONF_FOLDER_PATH / self.filename

    def config_dict(self):
        with codecs.open(self.config_file, "r", "utf-8-sig") as fconfig:
            return json.load(fconfig)


if __name__ == '__main__':
    ai = AiSpeechConfig()
    print(f"ai: {ai}")

    conf = ai.config_dict()
    print(f"config type:{type(conf)} config: {conf}")


