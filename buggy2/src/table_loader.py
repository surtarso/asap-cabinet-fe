# asap_cabinet_fe/table_loader.py
import os
from src.config import *

def get_image_path(root, subpath, default):
    path = os.path.join(root, subpath)
    return path if os.path.exists(path) else default

def load_table_list():
    tables = []
    for root, dirs, files in os.walk(VPX_ROOT_FOLDER):
        for file in files:
            if file.lower().endswith(".vpx"):
                table_name = os.path.splitext(file)[0]
                vpx_path = os.path.join(root, file)
                tables.append({
                    "table_name": table_name,
                    "vpx_file": vpx_path,
                    "folder": root,
                    "table_img": get_image_path(root, TABLE_IMAGE_PATH, DEFAULT_TABLE_PATH),
                    "wheel_img": get_image_path(root, TABLE_WHEEL_PATH, DEFAULT_WHEEL_PATH),
                    "backglass_img": get_image_path(root, TABLE_BACKGLASS_PATH, DEFAULT_BACKGLASS_PATH),
                    "dmd_img": get_image_path(root, TABLE_DMD_PATH, DEFAULT_DMD_PATH)
                })
    tables.sort(key=lambda x: x["table_name"])
    return tables