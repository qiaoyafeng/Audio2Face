import asyncio
import os
import uuid
from typing import Union

from os.path import abspath, dirname, join
import uvicorn
import websockets
from fastapi import (
    FastAPI,
    File,
    UploadFile,
    Form,
    WebSocket,
    Request,
    Depends,
    HTTPException,
)
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette.templating import Jinja2Templates

import crud, models, schemas
from config.base import (
    VIDEO_FOLDER_PATH,
    TEMP_FOLDER_PATH,
    BACKGROUND_FOLDER_PATH,
    BASE_DOMAIN,
)
from database import SessionLocal, engine
from utils import replace_special_character

models.Base.metadata.create_all(bind=engine)

from ws_server import (
    get_video_task_info,
    create_video_message,
    send_message_to_client,
)

from ws_server import answer_handler

app = FastAPI()

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")
# app.mount("/background", StaticFiles(directory="static/background"), name="background")


templates = Jinja2Templates(directory="templates")


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class TestItem(BaseModel):
    name: str
    price: float
    is_offer: Union[bool, None] = None


@app.post("/login/")
async def login(username: str = Form(), password: str = Form()):
    return {"username": username}


@app.get("/items/{item_id}", include_in_schema=False)
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


@app.put("/items/{item_id}", include_in_schema=False)
def update_item(item_id: int, item: TestItem):
    return {"item_name": item.name, "item_price": item.price, "item_id": item_id}


@app.post("/files", include_in_schema=False)
async def create_file(file: bytes = File()):
    return {"file_size": len(file)}


@app.post("/uploadfile")
async def create_upload_file(
    file: bytes = File(), task_id: str = Form(), db: Session = Depends(get_db)
):
    print(f"create_upload_file: {task_id}")
    video_id = uuid.uuid4().hex
    if task_id:
        video_name = f"{video_id}.mp4"
        video_name_path = join(VIDEO_FOLDER_PATH, video_name)
        video_url = f"/video/{video_name}"
        with open(video_name_path, "wb") as af:
            af.write(file)
        update_task_schema = schemas.VideoTaskUpdateRequest(
            uuid=task_id, video_url=video_url
        )

        crud.update_video_task(db, update_task_schema)
    return {"message": "upload successfully!"}


@app.get("/get_file/{file_name}")
def read_item(file_name: str):
    file_path = os.path.isfile(os.path.join(TEMP_FOLDER_PATH, file_name))
    if file_path:
        return FileResponse(os.path.join(TEMP_FOLDER_PATH, file_name))
    else:
        return join(TEMP_FOLDER_PATH, "tests.txt")


@app.post(
    "/send_video_info",
)
async def send_video_info(
    item: schemas.VideoTaskCreateRequest, db: Session = Depends(get_db)
):
    print(f"enter send_video_info ...{item.info}")
    info = replace_special_character(item.info)
    resp = {
        "code": 2000,
        "message": "操作成功！",
        "errorMsg": "",
    }
    result = {
        "info": info,
    }
    video_task = crud.create_video_task(db, item)
    task_id = video_task.uuid
    info = video_task.info
    background_url = video_task.background_url
    try:
        # 上传完成文本和背景图后， 发送message给Websocket client
        message = create_video_message(info, background_url, task_id)
        await send_message_to_client(message)
    except Exception as e:
        print(f"except - create_video_message,send_message_to_client: {e}")
    result["task_id"] = task_id
    resp["result"] = result
    return resp


@app.get("/", response_class=HTMLResponse)
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


@app.get("/video/task")
def get_video_task(task_id: str, db: Session = Depends(get_db)):
    resp = {
        "code": 2000,
        "message": "操作成功！",
        "errorMsg": "",
    }
    result = {}
    print(f"get_video_task  task_id: {task_id}")
    if task_id:
        task = crud.get_video_task(db, task_id)
        print(f"task: {task}")
        if task and task.video_url:
            video_url = f"{BASE_DOMAIN}{task.video_url}"
            result["video_url"] = video_url
    resp["result"] = result
    print(f"get_video_task resp: {resp}")
    return resp


@app.get("/video/{file_name}")
def get_video(file_name: str):
    print(f"enter get_video ...")
    files = [file for file in os.listdir(VIDEO_FOLDER_PATH)]

    if file_name in files:
        return FileResponse(os.path.join(VIDEO_FOLDER_PATH, file_name))
    else:
        return {"message": "video file not found"}


@app.post("/create_video_task/", response_model=schemas.VideoTaskCreateResponse)
def create_video_task_api(
    task: schemas.VideoTaskCreateRequest, db: Session = Depends(get_db)
):
    return crud.create_video_task(db=db, task=task)


@app.websocket("/")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    while True:
        await answer_handler(websocket)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
