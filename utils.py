import os


def replace_special_character(raw_str):
    update_str = (
        raw_str.replace("\n", "。").replace("\r", "").replace("【", "，").replace("】", "，")
    )
    return update_str
