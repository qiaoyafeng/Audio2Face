import os
import sys
import time
import uuid
from os.path import abspath, dirname, join
import codecs
import json

import asyncio
import websockets

from constants import (
    BS_CONUNT,
    var_bs_index,
    const_bs_index,
    const_bs_value,
    bs_name_index,
)

package_path = "./"

UPLOAD_FOLDER_PATH = join(package_path, "temp/")

BASE_DOMAIN = "http://172.16.35.149:8000"

# *******************************************
# load config file
path_config = join(package_path, "config.json")

try:
    with codecs.open(path_config, "r", "utf-8-sig") as fconfig:
        ServiceConfig = json.load(fconfig)
except Exception as err:
    print("Read file failed,", path_config, ".Error is :", err)
    os.system("pause")
    # exit(1)

# *******************************************
# read parsing config data
productId = ServiceConfig["api_key"]["productId"]
publicKey = ServiceConfig["api_key"]["publicKey"]
secretkey = ServiceConfig["api_key"]["secretKey"]
productIdChat = ServiceConfig["api_key"]["productIdChat"]
SPEAKER = ServiceConfig["api_key"]["speaker"]

BA_URL = ServiceConfig["api_ba"]["url"]
WSURL = ServiceConfig["api_websocket"]["url"] + productId + "&token="
request_body_json = json.dumps(ServiceConfig["api_websocket"]["request_body_first"])

info_print = ServiceConfig["config"]["print"]
ID_SESSION = ServiceConfig["config"]["session"]
FPS = ServiceConfig["config"]["fps"]
SPEED_PLAY = float(1.0 / FPS)

# pbfile_path = join(package_path, 'zsmeif.pb')

CPU_Thread = ServiceConfig["config"]["tensorflow"]["cpu"]
CPU_Frames = ServiceConfig["config"]["tensorflow"]["frames"]

# *******************************************
# *******************************************

# read server and client config data
SERVER_ADDR = (
    ServiceConfig["config"]["server"]["ip"],
    ServiceConfig["config"]["server"]["port"],
)
CLIENT_ADDR = (
    ServiceConfig["config"]["client"]["ip"],
    ServiceConfig["config"]["client"]["port"],
)

# 0-******************** websockets***********
CONNECTIONS = set()

# 1-*******************************************


from lib.aispeech.api_aispeech import AiSpeech
from lib.aispeech.api_websocket import AiSpeechWebSocket

ANSWER_DATA = {
    "code": 0,
    "msg": "ok",
    "data": {
        "answer": {"input": "你好。", "output": "您好！我是心心，请问有什么可以帮助到您。"},
        "tts": {
            "audio_url": "https://ds-model-tts.tos-cn-beijing.volces.com/temp/169344792907574024.wav"
        },
        "face": {
            "url": "https://ds-vhost-action-dev.oss-cn-beijing.aliyuncs.com/mouth/c9973b68-0969-45f8-a44c-34745b8443c4.json"
        },
        "motion": {
            "url": "https://ds-vhost-action-dev.oss-cn-beijing.aliyuncs.com/169344792907574024.bin"
        },
    },
}


class Answer:
    def __init__(self, in_text, out_text):
        self.in_text = in_text
        self.out_text = out_text

    def output_data(self):
        pass


# *******************************************
# *******************************************
import numpy as np

from lib.tensorflow.input_wavdata_output_lpc import c_lpc, get_audio_frames
from lib.tensorflow.input_lpc_output_weight import WeightsAnimation

tflitepath = "./best_model/Audio2Face.tflite"
model_path = "./best_model/Audio2Face"
# load tensorflow pb model file
pb_weights_animation = WeightsAnimation(tflitepath, model_path)
get_weight = pb_weights_animation.get_weight


# *******************************************
# work thread function
# use to deal with audio data to lpc data ,and input lpc data to get weights.
def worker(q_input, q_output, i):
    print("the cpus number is:", i)
    cnt = 0
    while True:
        input_data = q_input.get()
        for output_wav in input_data:
            # audio frame to lpc datas
            output_lpc = c_lpc(output_wav)
            # lpc data to weights
            output_data = get_weight(output_lpc, label_len=len(var_bs_index))
            # 赋值
            weights = np.zeros((output_data.shape[0], BS_CONUNT))
            # print(weights.shape)

            weights[:, var_bs_index] = output_data
            weights[:, const_bs_index] = const_bs_value

            weights1 = np.zeros((output_data.shape[0], BS_CONUNT))
            for i in range(len(bs_name_index)):
                weights1[:, i] = weights[:, bs_name_index[i]]

            q_output.put(weights1)
        print(cnt)
        cnt += 1


# *******************************************
import threading
from queue import Queue

"""
    mutli thread deal with audio to weights

"""


class SoundAnimation:
    def __init__(self, cpus=1, input_nums=30):
        self.process = None
        self.q_output = None
        self.q_input = None
        self.flag_nums = None
        self.cpus = cpus
        self.input_nums = input_nums
        self.init_multiprocessing()
        self.flag_start = False

    def __del__(self):
        if self.flag_start:
            self.stop_multiprocessing()

    # init  threads
    def init_multiprocessing(self):
        self.q_input = [Queue() for i in range(0, self.cpus)]
        self.q_output = [Queue() for i in range(0, self.cpus)]
        self.process = []
        for i in range(0, self.cpus):
            self.process.append(
                threading.Thread(
                    target=worker, args=(self.q_input[i], self.q_output[i], i)
                )
            )

    # start threads
    def start_multiprocessing(self):
        self.flag_start = True
        for i in range(0, self.cpus):
            self.process[i].setDaemon(True)
            self.process[i].start()

    # stop threads
    def stop_multiprocessing(self):
        for i in range(0, self.cpus):
            self.process[i].terminate()

    # input audio frame data
    def input_frames_data(self, input_data):
        input_data_nums = [
            input_data[i : i + self.input_nums]
            for i in range(0, len(input_data), self.input_nums)
        ]
        self.flag_nums = len(input_data_nums)
        for i in range(0, self.cpus):
            self.q_input[i].put(input_data_nums[i :: self.cpus])

    def yield_output_data(self):
        num = 0
        flag_end = True
        while flag_end:
            for i in range(0, self.cpus):
                if num == self.flag_nums:
                    flag_end = False
                    break
                data_output = self.q_output[i].get()
                for data in data_output:
                    yield data
                num += 1


def get_audio_animation():
    audio_animations = []
    for weight in sound_animation.yield_output_data():
        audio_animations.append(weight)
        # print(f"weight: {weight}")
    return audio_animations


def get_answer_data(recv_dict):
    answer_data = {}
    audio_name = "test.wav"
    face_name = "test.txt"
    audio_url = f"{BASE_DOMAIN}/get_file/{audio_name}"
    face_url = f"{BASE_DOMAIN}/get_file/{face_name}"
    text = recv_dict["text"]["content"]
    dm_tts = aispeech.dm_tts(url=BA_URL, text=text, speaker=SPEAKER)
    if dm_tts.status_code == 200:
        b_wav_data = dm_tts.content
        if b_wav_data:
            voice = np.frombuffer(b_wav_data[44:], dtype=np.int16)
            # audio data to frames
            input_data = get_audio_frames(voice)
            # input audio data to get weights data
            sound_animation.input_frames_data(input_data)
            audio_animation = get_audio_animation()
            # print(f"audio_animation: {audio_animation}")

            audio_name = f"{uuid.uuid4().hex}.wav"
            audio_path = join(UPLOAD_FOLDER_PATH, audio_name)

            with open(audio_path, "wb") as af:
                af.write(b_wav_data)
            audio_url = f"{BASE_DOMAIN}/get_file/{audio_name}"

            face_name = f"{uuid.uuid4().hex}.txt"
            face_path = join(UPLOAD_FOLDER_PATH, face_name)
            np.savetxt(face_path, audio_animation, fmt="%.19e", delimiter=",")
            face_url = f"{BASE_DOMAIN}/get_file/{face_name}"

    answer_data["answer"] = {"input": text, "output": "您好！我是心心，请问有什么可以帮助到您。"}
    answer_data["tts"] = {"audio_url": audio_url}
    answer_data["face"] = {"url": face_url}
    answer_data["motion"] = {"url": ""}
    answer_data["background"] = {"url": ""}
    return answer_data


async def answer_handler(websocket):
    print("Enter answer_handler ...")
    recv_str = await websocket.recv()
    print(f"recv_str: {recv_str}")
    recv_dict = json.loads(recv_str)
    print(f"<<< {recv_dict}")
    recv_type = recv_dict["type"]
    print(f"recv_type:{recv_type}")
    # recv_type：0 text; 1 asr
    answer_data = get_answer_data(recv_dict)
    print(f"answer_data:{answer_data}")
    resp_body = {"code": 0, "msg": "ok", "data": answer_data}

    resp_body = json.dumps(resp_body)
    await websocket.send(resp_body)
    print(f">>> {resp_body}")


async def asr_handler(websocket):
    asr = await websocket.recv()
    asr = json.loads(asr)
    print(f"<<< {asr}")
    request_body = f"asr_request_body: {ANSWER_DATA}!"
    await websocket.send(request_body)
    print(f">>> {request_body}")


async def text_handler(websocket):
    text = await websocket.recv()
    text = json.loads(text)
    print(f"<<< {text}")
    request_body = f"text_request_body: {ANSWER_DATA}!"
    await websocket.send(request_body)
    print(f">>> {request_body}")


def send_message_to_client(message):
    """
    发送消息给所有客户端
    :param message:
    :return:
    """
    print(f"send  {message} to {CONNECTIONS}")
    websockets.broadcast(CONNECTIONS, message)


def create_video_message(text: str, background_name: str):
    """
    根据用户上传的文本内容和背景图片生成对应的消息

    """
    print(f"create_video_message: {text}---{background_name}")
    answer_data = {}

    audio_name = "39ca506ed50043a7a42db1a52b1c3c20.wav"
    face_name = "dafc1e4e81334ce8862bdc6f4724c497.txt"

    audio_url = f"{BASE_DOMAIN}/get_file/{audio_name}"
    face_url = f"{BASE_DOMAIN}/get_file/{face_name}"
    background_url = f"{BASE_DOMAIN}/background/{background_name}"

    answer_data["answer"] = {"input": "notification", "output": text}
    answer_data["tts"] = {"audio_url": audio_url}
    answer_data["face"] = {"url": face_url}
    answer_data["motion"] = {"url": ""}
    answer_data["background"] = {"url": background_url}
    message = {"code": 0, "msg": "ok", "data": answer_data}

    message = json.dumps(message)

    return message


def get_video_task_info(task_id: str):
    """
    获取视频任务信息
    """
    print(f"get_video_task_info:{task_id}")

    video_task_file_path = "./video_task.log"
    task_info = {}

    with open(video_task_file_path, "r",encoding="utf-8") as tasks:
        for task in tasks.readlines():
            task_line = task.split("|")
            if task_line and task_line[0] == task_id:
                task_info["task_id"] = task_id
                task_info["text"] = task_line[1]
                task_info["background_name"] = task_line[2]
                task_info["is_created"] = task_line[3]
    return task_info


def create_video_task(task_id: str):
    """
    创建生成视频任务
    """
    print(f"create_video_task ....")

    task_info = get_video_task_info(task_id)
    if task_info:
        message = create_video_message(task_info["text"], task_info["background_name"])
        send_message_to_client(message)


async def handler(websocket):
    CONNECTIONS.add(websocket)
    print(f"CONNECTIONS ADD: {websocket}")
    async for message in websocket:
        if websocket.path == "/asr":
            await asr_handler(websocket)
        elif websocket.path == "/text":
            await text_handler(websocket)
        else:
            await answer_handler(websocket)
        print(f"message: {message}")

    try:
        await websocket.wait_closed()
    finally:
        CONNECTIONS.remove(websocket)
        print(f"CONNECTIONS REMOVE: {websocket}")


async def main():
    async with websockets.serve(handler, SERVER_ADDR[0], SERVER_ADDR[1]):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    print("Enter main....")
    aispeech = AiSpeech(productId, publicKey, secretkey, productIdChat=productIdChat)
    aispeech.update_token()
    sound_animation = SoundAnimation(CPU_Thread, CPU_Frames)
    sound_animation.start_multiprocessing()
    print("aispeech and sound_animation ok ...")
    asyncio.run(main())
