import os

from flask import Flask, render_template, send_from_directory

app = Flask(__name__)

# 设置文件临时保存路径
app.config["TEMP_FOLDER"] = "temp/"


@app.route("/get_file/<file_name>", methods=["GET"])
def get_file(file_name):
    file_path = os.path.isfile(os.path.join(app.config["TEMP_FOLDER"], file_name))
    if file_path:
        return send_from_directory(app.config["TEMP_FOLDER"], file_name)
    else:
        return send_from_directory(app.config["TEMP_FOLDER"], "test.txt")
