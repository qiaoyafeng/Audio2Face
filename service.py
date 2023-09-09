from config.aispeech import AiSpeechConfig
from lib.aispeech.api_aispeech import AiSpeech
from models import ChatInput, ChatOutput



class AiSpeechService:
    """
         AiSpeechService
    """

    def get_config(self):
        aispeech_config = AiSpeechConfig().config_dict()
        self.aispeech_config = aispeech_config
        return aispeech_config

    def get_aispeech(self):
        productId, publicKey, secretkey, productIdChat = self.aispeech_config["api_key"]["productId"],self.aispeech_config["api_key"]["publicKey"],

        aispeech = AiSpeech(productId, publicKey, secretkey, productIdChat=productIdChat)
        return aispeech


class ChatService:
    """
         ChatService
    """

    def __init__(self, chat_input: ChatInput, chat_output: ChatOutput):
        self.chat_input = chat_input
        self.chat_output = chat_output

    def get_input(self):
        """

        :return: dict
        """
        input_dict = {}

        # types:  0 text, 1 audio
        if self.chat_input.in_type:
            # audio type input
            audio = self.asr["base64"]
            format = self.asr["format"]
            print(f"format: {format}")

        else:
            # text type input
            text = self.text["content"]
            print(f"text: {text}")
        return input_dict

    def get_output(self):
        """

        :return: dict
        """

        output_dict = {}
        chat_input = self.chat_input

        if chat_input.in_type:
            pass
        else:
            text = self.chat_input.text["content"]
            url = ""

            speaker = ""
            aispeech = AiSpeechService().get_aispeech()

            dm_tts = aispeech.dm_tts(url=url, text=text, speaker=speaker)

        return output_dict



