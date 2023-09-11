import asyncio
import os
import uuid
from typing import Union

from os.path import abspath, dirname, join
import uvicorn
import websockets
from fastapi import FastAPI, File, UploadFile, Form, WebSocket, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from pydantic import BaseModel
from starlette.templating import Jinja2Templates

from ws_server import (
    create_video_task,
    handler,
    SERVER_ADDR,
    main,
    update_video_task_info,
)
from ws_server import answer_handler

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
# app.mount("/background", StaticFiles(directory="static/background"), name="background")

root_path = "./"

BACKGROUND_FOLDER_PATH = join(root_path, "static/background")
VIDEO_FOLDER_PATH = join(root_path, "static/video")

TEMP_FOLDER_PATH = join(root_path, "temp")

BASE_DOMAIN = "http://172.16.35.149:8000"

templates = Jinja2Templates(directory="templates")


class Item(BaseModel):
    name: str
    price: float
    is_offer: Union[bool, None] = None


@app.get("/")
def hello():
    return {"info": "好心情，有你才有好心情"}


@app.post("/login/")
async def login(username: str = Form(), password: str = Form()):
    return {"username": username}


@app.get("/items/{item_id}", include_in_schema=False)
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


@app.put("/items/{item_id}", include_in_schema=False)
def update_item(item_id: int, item: Item):
    return {"item_name": item.name, "item_price": item.price, "item_id": item_id}


@app.post("/files", include_in_schema=False)
async def create_file(file: bytes = File()):
    return {"file_size": len(file)}


@app.post("/uploadfile")
async def create_upload_file(file: bytes = File(), task_id: str = Form()):
    print(f"create_upload_file: {task_id}")
    video_id = uuid.uuid4().hex
    if task_id:
        video_name = f"{video_id}.mp4"
        video_name_path = join(VIDEO_FOLDER_PATH, video_name)
        with open(video_name_path, "wb") as af:
            af.write(file)
        update_video_task_info(task_id, video_id)

    return {"message": "upload successfully!"}


@app.get("/get_file/{file_name}")
def read_item(file_name: str):
    file_path = os.path.isfile(os.path.join(TEMP_FOLDER_PATH, file_name))
    if file_path:
        return FileResponse(os.path.join(TEMP_FOLDER_PATH, file_name))
    else:
        return join(TEMP_FOLDER_PATH, "test.txt")


@app.post("/send_video_info", response_class=HTMLResponse)
async def send_video_info(
    request: Request, info: str = Form(), file: UploadFile = File()
):
    print(f"enter send_video_info ...", info)
    info = info.replace("\n", "").replace("\r", "").replace("|", "")
    result = {"info": info, "message": "send successfully!"}
    task_id = f"{uuid.uuid4().hex}"
    background_name = f"{uuid.uuid4().hex}.jpg"
    background_name_path = join(BACKGROUND_FOLDER_PATH, background_name)
    contents = await file.read()

    with open(background_name_path, "wb") as af:
        af.write(contents)

    video_task_file_path = "./video_task.log"
    is_created = 0
    with open(video_task_file_path, "a", encoding="utf-8") as log:
        log_info = f"{task_id}|{info}|{background_name}|{is_created}\n"
        log.write(log_info)

    # 上传完成文本和背景图后， 创建视频任务，
    await create_video_task(task_id)
    result["task_id"] = task_id
    return RedirectResponse("/video/list", 302)


@app.get("/send_video_info", response_class=HTMLResponse)
async def send_video_info(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/background/list")
def get_background_list():
    background_list = []
    files = [file for file in os.listdir(BACKGROUND_FOLDER_PATH)]
    # 遍历文件列表，输出文件名
    for file in files:
        url = f"{BASE_DOMAIN}/background/{file}"
        file_dict = {"url": url}
        background_list.append(file_dict)
    return {"background_list": background_list}


@app.get("/background/{file_name}")
def get_background(file_name: str):
    files = [file for file in os.listdir(BACKGROUND_FOLDER_PATH)]
    if file_name in files:
        return FileResponse(os.path.join(BACKGROUND_FOLDER_PATH, file_name))
    else:
        return {"message": "background file not found"}


@app.get("/video/list")
def get_video_list(request: Request):
    video_url_list = []

    video_files = [file for file in os.listdir(VIDEO_FOLDER_PATH)]
    video_files.sort(key=lambda x: os.path.getmtime(os.path.join(VIDEO_FOLDER_PATH, x)))

    # last_videos = video_files[-3:]  # 显示最新三个视频
    last_videos = video_files[-1:]  # 改为显示最新一个视频
    last_videos.sort(reverse=True)
    for last_video in last_videos:
        video_url = f"{BASE_DOMAIN}/video/{last_video}"
        video_url_list.append(video_url)

    return templates.TemplateResponse(
        "video_list.html", {"request": request, "video_url_list": video_url_list}
    )


@app.get("/video/last", response_class=HTMLResponse)
def get_last_video(request: Request):
    print(f"enter get_last_video ...")
    files = [file for file in os.listdir(VIDEO_FOLDER_PATH)]
    print(f"files: {files}")
    files.sort(key=lambda x: os.path.getmtime(os.path.join(VIDEO_FOLDER_PATH, x)))
    video_url = f"{BASE_DOMAIN}/video/{files[-1]}"
    return templates.TemplateResponse(
        "video_info.html", {"request": request, "video_url": video_url}
    )


@app.get("/video/{file_name}")
def get_video(file_name: str):
    print(f"enter get_video ...")
    files = [file for file in os.listdir(VIDEO_FOLDER_PATH)]

    if file_name in files:
        return FileResponse(os.path.join(VIDEO_FOLDER_PATH, file_name))
    else:
        return {"message": "background file not found"}


@app.get("/video/task/{task_id}")
def get_video_task(task_id: str):
    print(f"get_video_task: {task_id}")


@app.websocket("/")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    while True:
        await answer_handler(websocket)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
