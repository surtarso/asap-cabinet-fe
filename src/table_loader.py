import os
from .config import (VPX_ROOT_FOLDER, TABLE_IMAGE_PATH, DEFAULT_TABLE_PATH,
                    TABLE_WHEEL_PATH, DEFAULT_WHEEL_PATH, TABLE_BACKGLASS_PATH, DEFAULT_BACKGLASS_PATH,
                    TABLE_DMD_PATH, DEFAULT_DMD_PATH)

'''
This module handles scanning the VPX_ROOT_FOLDER and building a list
of tables with their associated image paths.
'''

def get_image_path(root, subpath, default):
    """
    Returns the full path for an image if it exists; otherwise, returns the default path.
    """
    path = os.path.join(root, subpath)
    return path if os.path.exists(path) else default

def load_table_list():
    """
    Walks through VPX_ROOT_FOLDER, finds .vpx files, and returns a sorted list
    of dictionaries with table information and media paths.
    """
    tables = []
    for root, dirs, files in os.walk(VPX_ROOT_FOLDER):
        for file in files:
            if file.lower().endswith(".vpx"):
                table_name = os.path.splitext(file)[0]
                vpx_path = os.path.join(root, file)
                table_img_path   = get_image_path(root, TABLE_IMAGE_PATH, DEFAULT_TABLE_PATH)
                wheel_img_path   = get_image_path(root, TABLE_WHEEL_PATH, DEFAULT_WHEEL_PATH)
                backglass_img_path = get_image_path(root, TABLE_BACKGLASS_PATH, DEFAULT_BACKGLASS_PATH)
                dmd_img_path     = get_image_path(root, TABLE_DMD_PATH, DEFAULT_DMD_PATH)
                tables.append({
                    "table_name":    table_name,
                    "vpx_file":      vpx_path,
                    "folder":        root,
                    "table_img":     table_img_path,
                    "wheel_img":     wheel_img_path,
                    "backglass_img": backglass_img_path,
                    "dmd_img":       dmd_img_path
                })
    tables.sort(key=lambda x: x["table_name"])
    return tables
