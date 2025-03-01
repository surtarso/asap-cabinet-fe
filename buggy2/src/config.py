# asap_cabinet_fe/config.py
import os
import configparser

CONFIG_FILE = "~/.asap-cabinet-fe/settings.ini"

# Default configuration values
VPX_ROOT_FOLDER = "/home/tarso/Games/vpinball/build/tables/"
EXECUTABLE_CMD = "/home/tarso/Games/vpinball/build/VPinballX_GL"
EXECUTABLE_SUB_CMD = "-Play"
DEFAULT_TABLE_PATH = "img/default_table.png"
DEFAULT_WHEEL_PATH = "img/default_wheel.png"
DEFAULT_BACKGLASS_PATH = "img/default_backglass.png"
DEFAULT_DMD_PATH = "img/default_dmd.gif"
TABLE_IMAGE_PATH = "images/table.png"
TABLE_WHEEL_PATH = "images/wheel.png"
TABLE_BACKGLASS_PATH = "images/backglass.png"
TABLE_DMD_PATH = "images/dmd.gif"
MAIN_MONITOR_INDEX = 1
MAIN_WINDOW_WIDTH = 1080
MAIN_WINDOW_HEIGHT = 1920
SECONDARY_MONITOR_INDEX = 0
BACKGLASS_WINDOW_WIDTH = 1024
BACKGLASS_WINDOW_HEIGHT = 1024
WHEEL_IMAGE_SIZE = 400
WHEEL_IMAGE_MARGIN = 20
FONT_NAME = "Arial"
FONT_SIZE = 32
BG_COLOR = "#202020"
TEXT_COLOR = "white"
FADE_DURATION = 300
SETTINGS_WIDTH = 600
SETTINGS_HEIGHT = 980
FADE_OPACITY = 0.5
BACKGLASS_IMAGE_WIDTH = 1024
BACKGLASS_IMAGE_HEIGHT = 768
DMD_WIDTH = 1024
DMD_HEIGHT = 256

def load_configuration():
    """Loads configuration settings from an ini file or creates the file with default settings if it does not exist."""
    global VPX_ROOT_FOLDER, EXECUTABLE_CMD, EXECUTABLE_SUB_CMD, TABLE_IMAGE_PATH, TABLE_WHEEL_PATH
    global TABLE_BACKGLASS_PATH, TABLE_DMD_PATH, MAIN_WINDOW_WIDTH, MAIN_WINDOW_HEIGHT
    global BACKGLASS_WINDOW_WIDTH, BACKGLASS_WINDOW_HEIGHT, WHEEL_IMAGE_SIZE, WHEEL_IMAGE_MARGIN
    global FONT_NAME, FONT_SIZE, BG_COLOR, TEXT_COLOR, MAIN_MONITOR_INDEX, SECONDARY_MONITOR_INDEX
    global FADE_DURATION

    ini_file = os.path.expanduser(CONFIG_FILE)
    config = configparser.ConfigParser()

    if not os.path.exists(os.path.dirname(ini_file)):
        os.makedirs(os.path.dirname(ini_file))

    if os.path.exists(ini_file):
        config.read(ini_file)
    else:
        config['Settings'] = {
            "VPX_ROOT_FOLDER": VPX_ROOT_FOLDER,
            "EXECUTABLE_CMD": EXECUTABLE_CMD,
            "EXECUTABLE_SUB_CMD": EXECUTABLE_SUB_CMD,
            "TABLE_IMAGE_PATH": TABLE_IMAGE_PATH,
            "TABLE_WHEEL_PATH": TABLE_WHEEL_PATH,
            "TABLE_BACKGLASS_PATH": TABLE_BACKGLASS_PATH,
            "TABLE_DMD_PATH": TABLE_DMD_PATH,
            "MAIN_MONITOR_INDEX": str(MAIN_MONITOR_INDEX),
            "MAIN_WINDOW_WIDTH": str(MAIN_WINDOW_WIDTH),
            "MAIN_WINDOW_HEIGHT": str(MAIN_WINDOW_HEIGHT),
            "SECONDARY_MONITOR_INDEX": str(SECONDARY_MONITOR_INDEX),
            "BACKGLASS_WINDOW_WIDTH": str(BACKGLASS_WINDOW_WIDTH),
            "BACKGLASS_WINDOW_HEIGHT": str(BACKGLASS_WINDOW_HEIGHT),
            "WHEEL_IMAGE_SIZE": str(WHEEL_IMAGE_SIZE),
            "WHEEL_IMAGE_MARGIN": str(WHEEL_IMAGE_MARGIN),
            "FONT_NAME": FONT_NAME,
            "FONT_SIZE": str(FONT_SIZE),
            "BG_COLOR": BG_COLOR,
            "TEXT_COLOR": TEXT_COLOR,
            "FADE_DURATION": str(FADE_DURATION)
        }
        with open(ini_file, "w") as f:
            config.write(f)
    
    s = config['Settings']
    globals().update({
        "VPX_ROOT_FOLDER": s.get("VPX_ROOT_FOLDER", VPX_ROOT_FOLDER),
        "EXECUTABLE_CMD": s.get("EXECUTABLE_CMD", EXECUTABLE_CMD),
        "EXECUTABLE_SUB_CMD": s.get("EXECUTABLE_SUB_CMD", EXECUTABLE_SUB_CMD),
        "TABLE_IMAGE_PATH": s.get("TABLE_IMAGE_PATH", TABLE_IMAGE_PATH),
        "TABLE_WHEEL_PATH": s.get("TABLE_WHEEL_PATH", TABLE_WHEEL_PATH),
        "TABLE_BACKGLASS_PATH": s.get("TABLE_BACKGLASS_PATH", TABLE_BACKGLASS_PATH),
        "TABLE_DMD_PATH": s.get("TABLE_DMD_PATH", TABLE_DMD_PATH),
        "MAIN_MONITOR_INDEX": int(s.get("MAIN_MONITOR_INDEX", MAIN_MONITOR_INDEX)),
        "MAIN_WINDOW_WIDTH": int(s.get("MAIN_WINDOW_WIDTH", MAIN_WINDOW_WIDTH)),
        "MAIN_WINDOW_HEIGHT": int(s.get("MAIN_WINDOW_HEIGHT", MAIN_WINDOW_HEIGHT)),
        "SECONDARY_MONITOR_INDEX": int(s.get("SECONDARY_MONITOR_INDEX", SECONDARY_MONITOR_INDEX)),
        "BACKGLASS_WINDOW_WIDTH": int(s.get("BACKGLASS_WINDOW_WIDTH", BACKGLASS_WINDOW_WIDTH)),
        "BACKGLASS_WINDOW_HEIGHT": int(s.get("BACKGLASS_WINDOW_HEIGHT", BACKGLASS_WINDOW_HEIGHT)),
        "WHEEL_IMAGE_SIZE": int(s.get("WHEEL_IMAGE_SIZE", WHEEL_IMAGE_SIZE)),
        "WHEEL_IMAGE_MARGIN": int(s.get("WHEEL_IMAGE_MARGIN", WHEEL_IMAGE_MARGIN)),
        "FONT_NAME": s.get("FONT_NAME", FONT_NAME),
        "FONT_SIZE": int(s.get("FONT_SIZE", FONT_SIZE)),
        "BG_COLOR": s.get("BG_COLOR", BG_COLOR),
        "TEXT_COLOR": s.get("TEXT_COLOR", TEXT_COLOR),
        "FADE_DURATION": int(s.get("FADE_DURATION", FADE_DURATION))
    })