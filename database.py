from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DB_IP = "127.0.0.1"
DB_PORT = "3306"
DB_NAME = "audio2face"
DB_USERNAME = "root"
DB_PASSWORD = "123456"

SQLALCHEMY_DATABASE_URL = (
    f"mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_IP}:{DB_PORT}/{DB_NAME}"
)


# echo=True表示引擎将用repr()函数记录所有语句及其参数列表到日志
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)

# SQLAlchemy中，CRUD是通过会话进行管理的，所以需要先创建会话，
# 每一个SessionLocal实例就是一个数据库session
# flush指发送到数据库语句到数据库，但数据库不一定执行写入磁盘
# commit是指提交事务，将变更保存到数据库文件中
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基本映射类
Base = declarative_base()
