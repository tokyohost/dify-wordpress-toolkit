import json
import re

import unicodedata
from PIL import Image
import os

def clean_string_keep_underscore(text):
    text = re.sub(r'\s+', '-', text)  # 替换空格为短横线 "-"
    text = re.sub(r'[^a-zA-Z0-9_-]', '', text)  # 只保留字母、数字、短横线 "-" 和下划线 "_"
    return text.strip('-')  # 移除开头和结尾的 "-"

def convert_to_webp(input_path, quality=80):
    print("Converting {} to webp".format(input_path))
    """将 PNG 或 JPG 图片转换为 WebP 格式"""
    try:
        #获取inputpath 在文件目录下创建同名的webp文件为 output_path
        output_path = os.path.splitext(input_path)[0] + ".webp"
        with Image.open(input_path) as img:
            img.save(output_path, "WEBP", quality=quality)
        print(f"转换成功: {output_path}")
        return output_path
    except Exception as e:
        print(f"转换失败: {e}")
def encodeStr(text):
    if text is None:
        return None
    return unicodedata.normalize("NFKC", text)
def process_other_parameter(data,tool_parameters):
    other_prarmeters = check_and_cover(tool_parameters)
    if other_prarmeters:
        other_prarmeters.update(data)
        return other_prarmeters
    else:
        return data
def check_and_cover(tool_parameters):
    if "otherParamter" in tool_parameters and tool_parameters["otherParamter"]:
        return cover_other_parameter(tool_parameters["otherParamter"])
    else:
        return None
def cover_other_parameter(strJson):
    if strJson is None:
        return None
    if is_valid_json(strJson):
        #处理额外参数
        other_parameter = json.loads(strJson)

        return other_parameter
    else:
        raise Exception("other_parameter is not a valid json object")
    pass
def is_valid_json(parameter_json):
    try:
        obj = json.loads(parameter_json)
        return isinstance(obj, (dict,))  # 只允许对象 {}
    except json.JSONDecodeError:
        return False
def get_sql_type_regex(sql):
    sql = sql.strip().lower()
    match = re.match(r'^\s*(select|insert|update|delete|create|drop|alter|truncate|merge)\b', sql, re.IGNORECASE)
    return match.group(1).upper() if match else "UNKNOWN"