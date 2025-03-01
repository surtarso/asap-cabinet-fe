import os
import configparser
'''
This module holds all configuration constants 
and the function to load settings from the INI file.
'''

# Path to the configuration file
CONFIG_FILE             = "~/.asap-cabinet-fe/settings.ini"

# Main paths and commands
VPX_ROOT_FOLDER         = "/home/tarso/Games/vpinball/build/tables/"
EXECUTABLE_CMD          = "/home/tarso/Games/vpinball/build/VPinballX_GL"
EXECUTABLE_SUB_CMD      = "-Play"

# Default images path
DEFAULT_TABLE_PATH      = "img/default_table.png"
DEFAULT_WHEEL_PATH      = "img/default_wheel.png"
DEFAULT_BACKGLASS_PATH  = "img/default_backglass.png"
DEFAULT_DMD_PATH        = "img/default_dmd.gif"

# Per table images paths
TABLE_IMAGE_PATH        = "images/table.png"
TABLE_WHEEL_PATH        = "images/wheel.png"
TABLE_BACKGLASS_PATH    = "images/backglass.png"
TABLE_DMD_PATH          = "images/dmd.gif"

# Main window (playfield) settings
MAIN_MONITOR_INDEX      = 1
MAIN_WINDOW_WIDTH       = 1080
MAIN_WINDOW_HEIGHT      = 1920
WHEEL_IMAGE_SIZE        = 400
WHEEL_IMAGE_MARGIN      = 20
FONT_NAME               = "Arial"
FONT_SIZE               = 32
BG_COLOR                = "#202020"
TEXT_COLOR              = "white"

# Secondary window (backglass) settings
SECONDARY_MONITOR_INDEX = 0
BACKGLASS_WINDOW_WIDTH  = 1024
BACKGLASS_WINDOW_HEIGHT = 1024
BACKGLASS_IMAGE_WIDTH   = 1024
BACKGLASS_IMAGE_HEIGHT  = 768
DMD_WIDTH               = 1024
DMD_HEIGHT              = 256

# Transition settings
FADE_OPACITY            = 0.5   # Lower value gives a darker fade
FADE_DURATION           = 300   # Milliseconds

def load_configuration():
    """
    Loads configuration from the INI file, or creates the file with default settings if missing.
    Updates the module-level variables.
    """
    global VPX_ROOT_FOLDER, EXECUTABLE_CMD, EXECUTABLE_SUB_CMD
    global DEFAULT_TABLE_PATH, DEFAULT_WHEEL_PATH, DEFAULT_BACKGLASS_PATH, DEFAULT_DMD_PATH
    global TABLE_IMAGE_PATH, TABLE_WHEEL_PATH, TABLE_BACKGLASS_PATH, TABLE_DMD_PATH
    global MAIN_MONITOR_INDEX, MAIN_WINDOW_WIDTH, MAIN_WINDOW_HEIGHT
    global SECONDARY_MONITOR_INDEX, BACKGLASS_WINDOW_WIDTH, BACKGLASS_WINDOW_HEIGHT
    global BACKGLASS_IMAGE_WIDTH, BACKGLASS_IMAGE_HEIGHT, DMD_WIDTH, DMD_HEIGHT
    global WHEEL_IMAGE_SIZE, WHEEL_IMAGE_MARGIN, FONT_NAME, FONT_SIZE
    global BG_COLOR, TEXT_COLOR, FADE_DURATION, FADE_OPACITY

    ini_file = os.path.expanduser(CONFIG_FILE)
    config = configparser.ConfigParser()
    directory = os.path.dirname(ini_file)
    if not os.path.exists(directory):
        os.makedirs(directory)

    if os.path.exists(ini_file):
        config.read(ini_file)
    else:
        config['Main Paths'] = {
            "VPX_ROOT_FOLDER":         VPX_ROOT_FOLDER,
            "EXECUTABLE_CMD":          EXECUTABLE_CMD,
            "EXECUTABLE_SUB_CMD":      EXECUTABLE_SUB_CMD,
        }
        config['Default Images'] = {
            "DEFAULT_TABLE_PATH":      DEFAULT_TABLE_PATH,
            "DEFAULT_WHEEL_PATH":      DEFAULT_WHEEL_PATH,
            "DEFAULT_BACKGLASS_PATH":  DEFAULT_BACKGLASS_PATH,
            "DEFAULT_DMD_PATH":        DEFAULT_DMD_PATH,
        }
        config['Custom Images'] = {
            "TABLE_IMAGE_PATH":        TABLE_IMAGE_PATH,
            "TABLE_WHEEL_PATH":        TABLE_WHEEL_PATH,
            "TABLE_BACKGLASS_PATH":    TABLE_BACKGLASS_PATH,
            "TABLE_DMD_PATH":          TABLE_DMD_PATH,
        }
        config['Main Window'] = {
            "MAIN_MONITOR_INDEX":      str(MAIN_MONITOR_INDEX),
            "MAIN_WINDOW_WIDTH":       str(MAIN_WINDOW_WIDTH),
            "MAIN_WINDOW_HEIGHT":      str(MAIN_WINDOW_HEIGHT),
            "WHEEL_IMAGE_SIZE":        str(WHEEL_IMAGE_SIZE),
            "WHEEL_IMAGE_MARGIN":      str(WHEEL_IMAGE_MARGIN),
            "FONT_NAME":               FONT_NAME,
            "FONT_SIZE":               str(FONT_SIZE),
            "BG_COLOR":                BG_COLOR,
            "TEXT_COLOR":              TEXT_COLOR,
        }
        config['Secondary Window'] = {
            "SECONDARY_MONITOR_INDEX": str(SECONDARY_MONITOR_INDEX),
            "BACKGLASS_WINDOW_WIDTH":  str(BACKGLASS_WINDOW_WIDTH),
            "BACKGLASS_WINDOW_HEIGHT": str(BACKGLASS_WINDOW_HEIGHT),
            "BACKGLASS_IMAGE_WIDTH":   str(BACKGLASS_IMAGE_WIDTH),
            "BACKGLASS_IMAGE_HEIGHT":  str(BACKGLASS_IMAGE_HEIGHT),
            "DMD_WIDTH":               str(DMD_WIDTH),
            "DMD_HEIGHT":              str(DMD_HEIGHT),
        }
        config['Transitions'] = {
            "FADE_DURATION":           str(FADE_DURATION),
            "FADE_OPACITY":            str(FADE_OPACITY),
        }

        with open(ini_file, "w") as f:
            config.write(f)

    # Load settings from the appropriate sections
    p = config['Main Paths']
    VPX_ROOT_FOLDER         = p.get("VPX_ROOT_FOLDER", VPX_ROOT_FOLDER)
    EXECUTABLE_CMD          = p.get("EXECUTABLE_CMD", EXECUTABLE_CMD)
    EXECUTABLE_SUB_CMD      = p.get("EXECUTABLE_SUB_CMD", EXECUTABLE_SUB_CMD)

    di = config['Default Images']
    DEFAULT_TABLE_PATH      = di.get("DEFAULT_TABLE_PATH", DEFAULT_TABLE_PATH)
    DEFAULT_WHEEL_PATH      = di.get("DEFAULT_WHEEL_PATH", DEFAULT_WHEEL_PATH)
    DEFAULT_BACKGLASS_PATH  = di.get("DEFAULT_BACKGLASS_PATH", DEFAULT_BACKGLASS_PATH)
    DEFAULT_DMD_PATH        = di.get("DEFAULT_DMD_PATH", DEFAULT_DMD_PATH)

    pt = config['Custom Images']
    TABLE_IMAGE_PATH        = pt.get("TABLE_IMAGE_PATH", TABLE_IMAGE_PATH)
    TABLE_WHEEL_PATH        = pt.get("TABLE_WHEEL_PATH", TABLE_WHEEL_PATH)
    TABLE_BACKGLASS_PATH    = pt.get("TABLE_BACKGLASS_PATH", TABLE_BACKGLASS_PATH)
    TABLE_DMD_PATH          = pt.get("TABLE_DMD_PATH", TABLE_DMD_PATH)

    mw = config['Main Window']
    MAIN_MONITOR_INDEX      = int(mw.get("MAIN_MONITOR_INDEX", MAIN_MONITOR_INDEX))
    MAIN_WINDOW_WIDTH       = int(mw.get("MAIN_WINDOW_WIDTH", MAIN_WINDOW_WIDTH))
    MAIN_WINDOW_HEIGHT      = int(mw.get("MAIN_WINDOW_HEIGHT", MAIN_WINDOW_HEIGHT))
    WHEEL_IMAGE_SIZE        = int(mw.get("WHEEL_IMAGE_SIZE", WHEEL_IMAGE_SIZE))
    WHEEL_IMAGE_MARGIN      = int(mw.get("WHEEL_IMAGE_MARGIN", WHEEL_IMAGE_MARGIN))
    FONT_NAME               = mw.get("FONT_NAME", FONT_NAME)
    FONT_SIZE               = int(mw.get("FONT_SIZE", FONT_SIZE))
    BG_COLOR                = mw.get("BG_COLOR", BG_COLOR)
    TEXT_COLOR              = mw.get("TEXT_COLOR", TEXT_COLOR)

    sw = config['Secondary Window']
    SECONDARY_MONITOR_INDEX = int(sw.get("SECONDARY_MONITOR_INDEX", SECONDARY_MONITOR_INDEX))
    BACKGLASS_WINDOW_WIDTH  = int(sw.get("BACKGLASS_WINDOW_WIDTH", BACKGLASS_WINDOW_WIDTH))
    BACKGLASS_WINDOW_HEIGHT = int(sw.get("BACKGLASS_WINDOW_HEIGHT", BACKGLASS_WINDOW_HEIGHT))
    BACKGLASS_IMAGE_WIDTH   = int(sw.get("BACKGLASS_IMAGE_WIDTH", BACKGLASS_IMAGE_WIDTH))
    BACKGLASS_IMAGE_HEIGHT  = int(sw.get("BACKGLASS_IMAGE_HEIGHT", BACKGLASS_IMAGE_HEIGHT))
    DMD_WIDTH               = int(sw.get("DMD_WIDTH", DMD_WIDTH))
    DMD_HEIGHT              = int(sw.get("DMD_HEIGHT", DMD_HEIGHT))

    t = config['Transitions']
    FADE_DURATION           = int(t.get("FADE_DURATION", FADE_DURATION))
    FADE_OPACITY            = float(t.get("FADE_OPACITY", FADE_OPACITY))

