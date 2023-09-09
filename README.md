# Audio2Face
Audio2Face

## 启动 Websocket 服务

```

python server.py

```
请求数据：

```json
{
    "type":0, // 0: text; 1: asr
    "text":{"content":"你好！"},
    "asr":{"base64":"UklGRmRGAQBXQVZFZm10IBA......../9CPqI+hP8jv4nAQz/R/s=","format":"wav"}
}
```

响应数据：

```json

{
    "code": 0,
    "msg": "ok",
    "data": {
        "answer": {
            "input": "你好。",
            "output": "您好！我是心心，请问有什么可以帮助到您。"
        },
        "tts": {
            "audio_url": "https://ds-model-tts.tos-cn-beijing.volces.com/temp/169344792907574024.wav"
        },
        "face": {
            "url": "https://ds-vhost-action-dev.oss-cn-beijing.aliyuncs.com/mouth/c9973b68-0969-45f8-a44c-34745b8443c4.json"
        },
        "motion": {
            "url": "https://ds-vhost-action-dev.oss-cn-beijing.aliyuncs.com/169344792907574024.bin"
        }
    }
}

```


## Flask方式启动 下载面部数据和音频文件HTTP服务

```shell
flask run --host=0.0.0.0
```


## FastAPI方式启动HTTP服务

```shell
uvicorn main:app --reload --host=0.0.0.0
```