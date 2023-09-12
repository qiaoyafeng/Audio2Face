import datetime

import uuid
from sqlalchemy.orm import Session
import models
import schemas


# 通过task_id查询视频任务
def get_video_task(db: Session, task_id: str):
    return db.query(models.VideoTask).filter(models.VideoTask.uuid == task_id).first()


# 新建视频任务
def create_video_task(db: Session, task: schemas.VideoTaskCreateRequest):
    now = datetime.datetime.now()
    task_uuid = f"{uuid.uuid4().hex}"
    db_task = models.VideoTask(
        uuid=task_uuid,
        info=task.info,
        background_url=task.background_url,
        create_time=now,
        update_time=now,
    )
    db.add(db_task)
    db.commit()  # 提交保存到数据库中
    db.refresh(db_task)  # 刷新
    return db_task


# 更新生成视频任务
def update_video_task(db: Session, task: schemas.VideoTaskUpdateRequest):
    now = datetime.datetime.now()
    db_task = (
        db.query(models.VideoTask).filter(models.VideoTask.uuid == task.uuid).first()
    )
    if db_task and task.video_url:
        db_task.video_url = task.video_url
        db_task.update_time = now
    db.commit()  # 提交保存到数据库中
    db.refresh(db_task)  # 刷新
    return db_task
