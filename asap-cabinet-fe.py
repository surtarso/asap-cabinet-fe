#!/usr/bin/env python3
"""
                ------------ASAP-CABINET-FE------------
               "As Simple As Possible Cabinet Front-End"
                ---------------------------------------
                  A Dual-screen VPX Python Front-End
                ---------------------------------------
    Features:
    - Scans VPX_ROOT_FOLDER recursively for .vpx files.
    - For each table, uses:
        - Table image: table.png (or DEFAULT_TABLE_PATH if missing)
        - Backglass image: backglass.png (or DEFAULT_BACKGLASS_PATH if missing)
        - Wheel image: wheel.png (or DEFAULT_WHEEL_PATH if missing)
        - DMD animation: dmd.gif (of DEFAULT_DMD_PATH if missing)
    - Main Window (1080x1920): Displays table image full screen with wheel overlay
    - Secondary Window (1280x1024): Displays backglass image and DMD
    - Uses left/right arrow keys for infinite scrolling between tables
    - All images update with fade animation
    - Press Enter to launch table
    - Settings button to configure for your setup
    - Search button by querry
    * Use the screenshot_art.sh tool to get table media

Dependencies: python3, python3-pyqt5, python3-pyqt5.qtmultimedia

Tarso Galvão - feb/2025
"""

import os
import sys
import subprocess
import configparser

from PyQt5.QtCore import (
    Qt, QPropertyAnimation, QEasingCurve, QSize
)
from PyQt5.QtGui import (
    QPixmap, QPalette, QColor, QGuiApplication, QFont, QFontMetrics, QMovie
)
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QWidget, QGraphicsOpacityEffect,
    QVBoxLayout, QScrollArea, QDialog, QFormLayout, QLineEdit,
    QDialogButtonBox, QPushButton, QMessageBox
)

from PyQt5.QtMultimedia import QSound

# ------------- Configuration --------------
# ------------------------------------------
##          Default values:
# ------------------------------------------
CONFIG_FILE             = "~/.asap-cabinet-fe/settings.ini"
# LAUNCHER_LOGFILE        = "~/.asap-cabinet-fe/launcher.log"
# ERROR_LOGFILE           = "~/.asap-cabinet-fe/errors.log"

# Default images path
DEFAULT_TABLE_PATH      = "img/default_table.png"
DEFAULT_WHEEL_PATH      = "img/default_wheel.png"
DEFAULT_BACKGLASS_PATH  = "img/default_backglass.png"
DEFAULT_DMD_PATH        = "img/default_dmd.gif"

# Hint side-arrows 
HINT_ARROW_SIZE         = 48
HINT_ARROW_COLOR        = "white"
HINT_ARROW_BG_COLOR     = "#202020"

# Search and Settings icons
TOP_ICONS_SIZE          = 24

# Settings panel (portrait)
SETTINGS_WIDTH          = 500
SETTINGS_HEIGHT         = 700

# Sounds
SND_TABLE_CHANGE        = "snd/table_change.wav"
# ------------------------------------------
##     Included in settins dialog:
# ------------------------------------------
VPX_ROOT_FOLDER         = "~/Games/vpinball/build/tables/"
EXECUTABLE_CMD          = "~/Games/vpinball/build/VPinballX_GL"
EXECUTABLE_SUB_CMD      = "-Play"

# Per table images path (/tables/<table_dir>/)
TABLE_IMAGE_PATH        = "images/table.png"
TABLE_WHEEL_PATH        = "images/wheel.png"
TABLE_BACKGLASS_PATH    = "images/backglass.png"
TABLE_MARQUEE_PATH      = "images/marquee.png"

# Per table videos path (/tables/<table_dir>/)
VIDEO_TABLE_PATH        = "video/table.gif"
VIDEO_BACKGLASS_PATH    = "video/backglass.gif"
VIDEO_DMD_PATH          = "video/dmd.gif"

## Main window (vertical)
MAIN_MONITOR_INDEX      = 1
MAIN_WINDOW_WIDTH       = 1080
MAIN_WINDOW_HEIGHT      = 1920
WHEEL_IMAGE_SIZE        = 250
WHEEL_IMAGE_MARGIN      = 24
FONT_NAME               = "Arial"
FONT_SIZE               = 22
BG_COLOR                = "#202020"
TEXT_COLOR              = "white"

## Secondary window (backglass)
SECONDARY_MONITOR_INDEX = 0
BACKGLASS_WINDOW_WIDTH  = 1024
BACKGLASS_WINDOW_HEIGHT = 1024
BACKGLASS_IMAGE_WIDTH   = 1024
BACKGLASS_IMAGE_HEIGHT  = 768
DMD_WIDTH               = 1024
DMD_HEIGHT              = 256

# Transition settings
FADE_DURATION           = 300
FADE_OPACITY            = 0.5

# ---------------- Configuration Loader ----------------
def load_configuration():
    """Loads configuration settings from an ini file or creates the file with default settings if it does not exist."""
    
    global VPX_ROOT_FOLDER, EXECUTABLE_CMD, EXECUTABLE_SUB_CMD
    global TABLE_IMAGE_PATH, TABLE_WHEEL_PATH, TABLE_BACKGLASS_PATH, VIDEO_DMD_PATH
    global MAIN_MONITOR_INDEX, MAIN_WINDOW_WIDTH, MAIN_WINDOW_HEIGHT
    global SECONDARY_MONITOR_INDEX, BACKGLASS_WINDOW_WIDTH, BACKGLASS_WINDOW_HEIGHT
    global BACKGLASS_IMAGE_WIDTH, BACKGLASS_IMAGE_HEIGHT, DMD_WIDTH, DMD_HEIGHT
    global WHEEL_IMAGE_SIZE, WHEEL_IMAGE_MARGIN, FONT_NAME, FONT_SIZE
    global BG_COLOR, TEXT_COLOR, FADE_DURATION, FADE_OPACITY

    ini_file = os.path.expanduser(CONFIG_FILE) 
    config = configparser.ConfigParser()

    # Ensure the directory exists
    directory = os.path.dirname(ini_file)
    if not os.path.exists(directory):
        os.makedirs(directory)

    if os.path.exists(ini_file):
        config.read(ini_file)
    
    # Ensure 'Main Paths' section exists
    if 'Main Paths' not in config:
        config['Main Paths'] = {
            "VPX_ROOT_FOLDER":         VPX_ROOT_FOLDER,
            "EXECUTABLE_CMD":          EXECUTABLE_CMD,
            "EXECUTABLE_SUB_CMD":      EXECUTABLE_SUB_CMD,
        }
        config['Custom Images'] = {
            "TABLE_IMAGE_PATH":        TABLE_IMAGE_PATH,
            "TABLE_WHEEL_PATH":        TABLE_WHEEL_PATH,
            "TABLE_BACKGLASS_PATH":    TABLE_BACKGLASS_PATH,
            "VIDEO_DMD_PATH":          VIDEO_DMD_PATH,
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
    p = config['Main Paths']
    VPX_ROOT_FOLDER         = p.get("VPX_ROOT_FOLDER", VPX_ROOT_FOLDER)
    EXECUTABLE_CMD          = p.get("EXECUTABLE_CMD", EXECUTABLE_CMD)
    EXECUTABLE_SUB_CMD      = p.get("EXECUTABLE_SUB_CMD", EXECUTABLE_SUB_CMD)

    ci = config['Custom Images']
    TABLE_IMAGE_PATH        = ci.get("TABLE_IMAGE_PATH", TABLE_IMAGE_PATH)
    TABLE_WHEEL_PATH        = ci.get("TABLE_WHEEL_PATH", TABLE_WHEEL_PATH)
    TABLE_BACKGLASS_PATH    = ci.get("TABLE_BACKGLASS_PATH", TABLE_BACKGLASS_PATH)
    VIDEO_DMD_PATH          = ci.get("VIDEO_DMD_PATH", VIDEO_DMD_PATH)

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

# Load configuration on startup
load_configuration()

# ---------------- Settings Dialog ----------------
class SettingsDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        # Set the fixed size
        self.setFixedSize(SETTINGS_WIDTH, SETTINGS_HEIGHT)
        
        # Create a scroll area
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        
        # Create a widget to hold the form layout
        form_widget = QWidget()
        self.layout = QFormLayout(form_widget)
        
        # Use ini path on title
        ini_path = CONFIG_FILE.replace(os.path.expanduser("~"), "~")
        self.setWindowTitle(f"[Settings] {ini_path}")

        # Create QLineEdit fields for each setting
        self.vpxRootEdit             = QLineEdit(VPX_ROOT_FOLDER)
        self.execCmdEdit             = QLineEdit(EXECUTABLE_CMD)
        self.execSubCmdEdit          = QLineEdit(EXECUTABLE_SUB_CMD)
        self.tableImageEdit          = QLineEdit(TABLE_IMAGE_PATH)
        self.wheelImageEdit          = QLineEdit(TABLE_WHEEL_PATH)
        self.backglassImageEdit      = QLineEdit(TABLE_BACKGLASS_PATH)
        self.dmdTableEdit            = QLineEdit(VIDEO_DMD_PATH)
        self.mainMonitor             = QLineEdit(str(MAIN_MONITOR_INDEX))
        self.windowWidthEdit         = QLineEdit(str(MAIN_WINDOW_WIDTH))
        self.windowHeightEdit        = QLineEdit(str(MAIN_WINDOW_HEIGHT))
        self.secondaryMonitor        = QLineEdit(str(SECONDARY_MONITOR_INDEX))
        self.backglassWidthEdit      = QLineEdit(str(BACKGLASS_WINDOW_WIDTH))
        self.backglassHeightEdit     = QLineEdit(str(BACKGLASS_WINDOW_HEIGHT))
        self.backglassImageWidthEdit = QLineEdit(str(BACKGLASS_IMAGE_WIDTH))
        self.backglassImageHeightEdit= QLineEdit(str(BACKGLASS_IMAGE_HEIGHT))
        self.dmdWidthEdit            = QLineEdit(str(DMD_WIDTH))
        self.dmdHeightEdit           = QLineEdit(str(DMD_HEIGHT))
        self.wheelSizeEdit           = QLineEdit(str(WHEEL_IMAGE_SIZE))
        self.wheelMarginEdit         = QLineEdit(str(WHEEL_IMAGE_MARGIN))
        self.fontNameEdit            = QLineEdit(FONT_NAME)
        self.fontSizeEdit            = QLineEdit(str(FONT_SIZE))
        self.bgColorEdit             = QLineEdit(BG_COLOR)
        self.textColorEdit           = QLineEdit(TEXT_COLOR)
        self.fadeDurationEdit        = QLineEdit(str(FADE_DURATION))
        self.fadeOpacityEdit         = QLineEdit(str(FADE_OPACITY))
        
        # Add each field to the layout with a descriptive label
        self.add_section_title("Main Paths")
        self.layout.addRow("Tables Folder:",        self.vpxRootEdit)
        self.layout.addRow("VPX Executable:",       self.execCmdEdit)
        self.layout.addRow("VPX Argument:",         self.execSubCmdEdit)
        self.add_section_title("Custom Images")
        self.layout.addRow("Playfield Images Path:",self.tableImageEdit)
        self.layout.addRow("Wheel Images Path:",    self.wheelImageEdit)
        self.layout.addRow("Backglass Images Path:",self.backglassImageEdit)
        self.layout.addRow("DMD GIFs Path:",        self.dmdTableEdit)
        self.add_section_title("Screens Dimensions")
        self.layout.addRow("Playfield Monitor:",    self.mainMonitor)
        self.layout.addRow("Playfield Width:",      self.windowWidthEdit)
        self.layout.addRow("Playfield Height:",     self.windowHeightEdit)
        self.layout.addRow("Backglass Monitor:",    self.secondaryMonitor)
        self.layout.addRow("Backglass Width:",      self.backglassWidthEdit)
        self.layout.addRow("Backglass Height:",     self.backglassHeightEdit)
        self.layout.addRow("Backglass Image Width:",self.backglassImageWidthEdit)
        self.layout.addRow("Backglass Image Height:",self.backglassImageHeightEdit)
        self.layout.addRow("DMD Width:",            self.dmdWidthEdit)
        self.layout.addRow("DMD Height:",           self.dmdHeightEdit)
        self.add_section_title("Table Title Style")
        self.layout.addRow("Wheel Size:",           self.wheelSizeEdit)
        self.layout.addRow("Wheel Margin:",         self.wheelMarginEdit)
        self.layout.addRow("Font Name:",            self.fontNameEdit)
        self.layout.addRow("Font Size:",            self.fontSizeEdit)
        self.layout.addRow("Background Color:",     self.bgColorEdit)
        self.layout.addRow("Text Color:",           self.textColorEdit)
        self.add_section_title("Transition Settings")
        self.layout.addRow("Transition Duration:",  self.fadeDurationEdit)
        self.layout.addRow("Fade Opacity:",         self.fadeOpacityEdit)
        
        # Create a button box with Ok and Cancel buttons
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.layout.addRow(self.buttonBox)

        # Retrieve the standard Ok and Cancel buttons from the button box
        ok_button = self.buttonBox.button(QDialogButtonBox.Ok)
        cancel_button = self.buttonBox.button(QDialogButtonBox.Cancel)

        # Remove the text from both buttons so that only the icon is displayed
        ok_button.setText("")
        cancel_button.setText("")

        # Define a fixed square size for the buttons (adjust as needed)
        square_size = 40

        # Set both buttons to be square by fixing their width and height
        ok_button.setFixedSize(square_size, square_size)
        cancel_button.setFixedSize(square_size, square_size)

        # Adjust the icon size to fill the button area, ensuring a proper icon-only display
        ok_button.setIconSize(ok_button.size())
        cancel_button.setIconSize(cancel_button.size())

        # Set the form widget as the scroll area's widget
        scroll_area.setWidget(form_widget)

        # Create a vertical layout for the dialog and add the scroll area to it
        dialog_layout = QVBoxLayout(self)
        dialog_layout.addWidget(scroll_area)

    def getValues(self):
        """Retrieve the current settings values from the dialog."""
        return {
            "VPX_ROOT_FOLDER":         self.vpxRootEdit.text(),
            "EXECUTABLE_CMD":          self.execCmdEdit.text(),
            "EXECUTABLE_SUB_CMD":      self.execSubCmdEdit.text(),
            "TABLE_IMAGE_PATH":        self.tableImageEdit.text(),
            "TABLE_WHEEL_PATH":        self.wheelImageEdit.text(),
            "TABLE_BACKGLASS_PATH":    self.backglassImageEdit.text(),
            "VIDEO_DMD_PATH":          self.dmdTableEdit.text(),
            "MAIN_MONITOR_INDEX":      self.mainMonitor.text(),
            "MAIN_WINDOW_WIDTH":       self.windowWidthEdit.text(),
            "MAIN_WINDOW_HEIGHT":      self.windowHeightEdit.text(),
            "SECONDARY_MONITOR_INDEX": self.secondaryMonitor.text(),
            "BACKGLASS_WINDOW_WIDTH":  self.backglassWidthEdit.text(),
            "BACKGLASS_WINDOW_HEIGHT": self.backglassHeightEdit.text(),
            "BACKGLASS_IMAGE_WIDTH":   self.backglassImageWidthEdit.text(),
            "BACKGLASS_IMAGE_HEIGHT":  self.backglassImageHeightEdit.text(),
            "DMD_WIDTH":               self.dmdWidthEdit.text(),
            "DMD_HEIGHT":              self.dmdHeightEdit.text(),
            "WHEEL_IMAGE_SIZE":        self.wheelSizeEdit.text(),
            "WHEEL_IMAGE_MARGIN":      self.wheelMarginEdit.text(),
            "FONT_NAME":               self.fontNameEdit.text(),
            "FONT_SIZE":               self.fontSizeEdit.text(),
            "BG_COLOR":                self.bgColorEdit.text(),
            "TEXT_COLOR":              self.textColorEdit.text(),
            "FADE_DURATION":           self.fadeDurationEdit.text(),
            "FADE_OPACITY":            self.fadeOpacityEdit.text()
        }
    
    def add_section_title(self, title):
        """ Adds a section title with a distinct style """
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 14px; padding: 5px;")
        self.layout.addWidget(title_label)

# ---------------- Table Data Loader ----------------
def get_image_path(root, subpath, default):
    """Returns the image path if it exists, otherwise returns the default path."""
    path = os.path.join(root, subpath)
    return path if os.path.exists(path) else default

def load_table_list():
    """Loads and returns a sorted list of dictionaries containing information about .vpx tables found in the VPX_ROOT_FOLDER directory and its subdirectories."""
    # Initialize an empty list to store table information dictionaries
    tables = []
    
    # Walk through the VPX_ROOT_FOLDER directory and its subdirectories
    for root, dirs, files in os.walk(VPX_ROOT_FOLDER):
        # Iterate over each file in the current directory
        for file in files:
            # Check if the file has a .vpx extension (case insensitive)
            if file.lower().endswith(".vpx"):
                # Extract the table name by removing the file extension
                table_name = os.path.splitext(file)[0]
                # Build the full path to the .vpx file
                vpx_path = os.path.join(root, file)

                # Get paths using the helper function
                table_img_path     = get_image_path(root, TABLE_IMAGE_PATH, DEFAULT_TABLE_PATH)
                wheel_img_path     = get_image_path(root, TABLE_WHEEL_PATH, DEFAULT_WHEEL_PATH)
                backglass_img_path = get_image_path(root, TABLE_BACKGLASS_PATH, DEFAULT_BACKGLASS_PATH)
                dmd_img_path       = get_image_path(root, VIDEO_DMD_PATH, DEFAULT_DMD_PATH)

                # Append a dictionary containing all relevant table information to the tables list
                tables.append({
                    "table_name":    table_name,
                    "vpx_file":      vpx_path,
                    "folder":        root,
                    "table_img":     table_img_path,
                    "wheel_img":     wheel_img_path,
                    "backglass_img": backglass_img_path,
                    "dmd_img":       dmd_img_path
                })
    
    # Sort the list of tables alphabetically by the table name
    tables.sort(key=lambda x: x["table_name"])
    
    # Return the sorted list of table dictionaries
    return tables

# ---------------- Secondary Window ----------------
class SecondaryWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Secondary Display (Backglass)")
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setFixedSize(BACKGLASS_WINDOW_WIDTH, BACKGLASS_WINDOW_HEIGHT)  # Full screen size
        self.setStyleSheet("background-color: black;")

        # QLabel for backglass image (aligned to top)
        self.label = QLabel(self)
        self.label.setGeometry(0, 0, BACKGLASS_IMAGE_WIDTH, BACKGLASS_IMAGE_HEIGHT)
        self.label.setAlignment(Qt.AlignHCenter | Qt.AlignTop)

        # Opacity effect for fade animation
        self.backglass_effect = QGraphicsOpacityEffect(self.label)
        self.label.setGraphicsEffect(self.backglass_effect)
        self.backglass_effect.setOpacity(1.0)

        # QLabel for DMD (fills the black bottom part)
        self.dmd_label = QLabel(self)
        self.dmd_label.setGeometry(0, BACKGLASS_IMAGE_HEIGHT, DMD_WIDTH, DMD_HEIGHT)  # Positioned below backglass
        self.dmd_label.setStyleSheet("background-color: black;")  # Ensure black background
        self.dmd_label.setAlignment(Qt.AlignCenter)

    def update_image(self, image_path, table_folder):
        """Update backglass image and DMD GIF, prioritizing table-specific DMD if available."""
        
        # --- Update Backglass Image ---
        if not os.path.exists(image_path):
            image_path = DEFAULT_BACKGLASS_PATH

        pixmap = QPixmap(image_path)
        if pixmap.isNull():
            pixmap = QPixmap(BACKGLASS_IMAGE_WIDTH, BACKGLASS_IMAGE_HEIGHT)
            pixmap.fill(Qt.black)
        else:
            pixmap = pixmap.scaled(BACKGLASS_IMAGE_WIDTH, BACKGLASS_IMAGE_HEIGHT, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        self.label.setPixmap(pixmap)
        self.backglass_effect.setOpacity(1.0)

        # --- Determine DMD GIF Path ---
        table_dmd_path = os.path.join(table_folder, VIDEO_DMD_PATH)  # Table-specific DMD
        dmd_path = table_dmd_path if os.path.exists(table_dmd_path) else DEFAULT_DMD_PATH

        # --- Update DMD GIF ---
        if os.path.exists(dmd_path):
            self.dmd_movie = QMovie(dmd_path)
            self.dmd_movie.setCacheMode(QMovie.CacheAll)

            # Get original GIF size
            self.dmd_movie.start()  # Start to get correct frame size
            frame_size = self.dmd_movie.currentPixmap().size()
            self.dmd_movie.stop()

            # Scale while maintaining aspect ratio
            dmd_width, dmd_height = frame_size.width(), frame_size.height()
            if dmd_width > 0 and dmd_height > 0:
                aspect_ratio = dmd_width / dmd_height
                new_width    = min(DMD_WIDTH, int(DMD_HEIGHT * aspect_ratio))
                new_height   = min(DMD_HEIGHT, int(DMD_WIDTH / aspect_ratio))

                if new_width > DMD_WIDTH:
                    new_width  = DMD_WIDTH
                    new_height = int(DMD_WIDTH / aspect_ratio)
                if new_height > DMD_HEIGHT:
                    new_height = DMD_HEIGHT
                    new_width  = int(DMD_HEIGHT * aspect_ratio)

                self.dmd_movie.setScaledSize(QSize(new_width, new_height))

                # Center the GIF inside the 1024x256 area
                x_offset = (DMD_WIDTH - new_width) // 2
                y_offset = (DMD_HEIGHT - new_height) // 2
                self.dmd_label.setGeometry(x_offset, BACKGLASS_IMAGE_HEIGHT + y_offset, new_width, new_height)

            self.dmd_label.setMovie(self.dmd_movie)
            self.dmd_movie.start()

# ---------------- Search Dialog ----------------
class SearchDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Search Tables")
        self.setFixedSize(400, 100)
        self.layout = QFormLayout(self)
        self.searchEdit = QLineEdit(self)
        self.layout.addRow("Search:", self.searchEdit)
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.layout.addRow(self.buttonBox)

    def getSearchQuery(self):
        return self.searchEdit.text()

# ---------------- Main Window ----------------
class SingleTableViewer(QMainWindow):

    def __init__(self, secondary_window=None):
        """Initializes the primary display window with table viewer and settings button."""
        super().__init__()
        self.setWindowTitle("Primary Display (Table Viewer)")
        self.setFixedSize(MAIN_WINDOW_WIDTH, MAIN_WINDOW_HEIGHT)
        self.setWindowFlags(Qt.FramelessWindowHint)

        self.secondary = secondary_window

        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(BG_COLOR))
        self.setPalette(palette)

        self.table_list = load_table_list()
        if not self.table_list:
            raise Exception("No .vpx files found in the specified folder.")

        self.current_index = 0

        central = QWidget(self)
        self.setCentralWidget(central)
        central.setFocusPolicy(Qt.StrongFocus)
        central.setStyleSheet(f"background-color: {BG_COLOR};")
        central.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setFocus()
        
        ##--- Create TABLE TITLE
        # Create the table label before using it
        self.table_label = QLabel(central)
        self.table_label.setGeometry(0, 0, MAIN_WINDOW_WIDTH, MAIN_WINDOW_HEIGHT)
        self.table_label.setScaledContents(True)
        self.table_label.setStyleSheet("border: none;")
        self.table_effect = QGraphicsOpacityEffect(self.table_label)
        self.table_label.setGraphicsEffect(self.table_effect)
        # Create the table name label after other elements are set up
        self.table_name_label = QLabel(central)
        self.table_name_label.setGeometry(10, MAIN_WINDOW_HEIGHT - 30, MAIN_WINDOW_WIDTH - 20, 30)
        self.table_name_label.setStyleSheet(f"color: {TEXT_COLOR}; font-size: {FONT_SIZE}px; text-align: left; background-color: {BG_COLOR};")
        self.table_name_label.setAlignment(Qt.AlignCenter)
        # Set initial table name after loading images
        self._set_table_name()

        ##--- Add SETTINGS BUTTON
        self.settingsButton = QPushButton("⚙", central)
        self.settingsButton.setFixedSize(40, 40)
        self.settingsButton.move(MAIN_WINDOW_WIDTH - 50, 10)
        self.settingsButton.setFocusPolicy(Qt.NoFocus)
        self.settingsButton.clicked.connect(self.openSettings)
        self.settingsButton.raise_()
        # Apply a stylesheet to remove the border and make the background transparent
        self.settingsButton.setStyleSheet(f"""
            QPushButton {{
            font-size:  {TOP_ICONS_SIZE}px;  /* Increase the font size of the ⚙ icon */
            border:     none;                /* Remove the ⚙ button border */
            background: transparent;         /* Make the background transparent */
            }}
        """)

        ##--- Add SEARCH BUTTON
        self.searchButton = QPushButton("🔍", central)
        self.searchButton.setFixedSize(40, 40)
        self.searchButton.move(10, 15)
        self.searchButton.setFocusPolicy(Qt.NoFocus)
        self.searchButton.clicked.connect(self.openSearch)
        self.searchButton.raise_()
        # Apply a stylesheet to remove the border and make the background transparent
        self.searchButton.setStyleSheet(f"""
            QPushButton {{
            font-size:  {TOP_ICONS_SIZE}px;  /* Increase the font size of the 🔍 icon */
            border:     none;                /* Remove the 🔍 button border */
            background: transparent;         /* Make the background transparent */
            }}
        """)

        ##--- Add WHEEL IMAGE
        wheel_x = MAIN_WINDOW_WIDTH - WHEEL_IMAGE_SIZE - WHEEL_IMAGE_MARGIN
        wheel_y = MAIN_WINDOW_HEIGHT - WHEEL_IMAGE_SIZE - WHEEL_IMAGE_MARGIN
        self.wheel_label = QLabel(central)
        self.wheel_label.setGeometry(wheel_x, wheel_y, WHEEL_IMAGE_SIZE, WHEEL_IMAGE_SIZE)
        self.wheel_label.setScaledContents(True)
        self.wheel_label.setAttribute(Qt.WA_TranslucentBackground)
        self.wheel_label.setStyleSheet("background-color: transparent;")
        self.wheel_effect = QGraphicsOpacityEffect(self.wheel_label)
        self.wheel_label.setGraphicsEffect(self.wheel_effect)

        ##--- Add HINT ARROWS
        self.left_arrow = QLabel("←", central)
        self.right_arrow = QLabel("→", central)
        # Style the arrows
        arrow_style = (
            f"padding-bottom: 5px; "
            f"color:              {HINT_ARROW_COLOR}; "
            f"font-size:          {HINT_ARROW_SIZE}px; "
            f"background-color:   {HINT_ARROW_BG_COLOR};"
        )
        self.left_arrow.setStyleSheet(arrow_style)
        self.right_arrow.setStyleSheet(arrow_style)
        # Center the arrows within their background box
        self.left_arrow.setAlignment(Qt.AlignCenter)
        self.right_arrow.setAlignment(Qt.AlignCenter)
        # Position arrows
        arrow_y = (2 * MAIN_WINDOW_HEIGHT) // 3 - 25  # Middle of the bottom third of the screen
        self.left_arrow.setGeometry(10, arrow_y, 50, 50)
        self.right_arrow.setGeometry(MAIN_WINDOW_WIDTH - 60, arrow_y, 50, 50)
        # Add fade animation to arrows
        self.left_arrow_effect = QGraphicsOpacityEffect(self.left_arrow)
        self.right_arrow_effect = QGraphicsOpacityEffect(self.right_arrow)
        self.left_arrow.setGraphicsEffect(self.left_arrow_effect)
        self.right_arrow.setGraphicsEffect(self.right_arrow_effect)
        self.left_arrow_animation = QPropertyAnimation(self.left_arrow_effect, b"opacity")
        self.right_arrow_animation = QPropertyAnimation(self.right_arrow_effect, b"opacity")

        for animation in [self.left_arrow_animation, self.right_arrow_animation]:
            animation.setDuration(1000)
            animation.setStartValue(1.0)
            animation.setKeyValueAt(0.5, 0.5)
            animation.setEndValue(1.0)
            animation.setEasingCurve(QEasingCurve.InOutQuad)
            animation.setLoopCount(-1)  # Loop indefinitely
            animation.start()

        try:
            self.table_change_sound = QSound(SND_TABLE_CHANGE)
        except Exception as e:
            print(f"Error loading sound: {e}")
            self.table_change_sound = None

        ##--- Initial display
        self.update_images()

    ##-- SEARCH Logic
    def openSearch(self):
        dialog = SearchDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            query = dialog.getSearchQuery().lower()
            for index, table in enumerate(self.table_list):
                if query in table["table_name"].lower():
                    self.current_index = index
                    self.update_images()
                    break
            else:
                QMessageBox.information(self, "Search", "No matching table found.")

    ##--- Add TABLE TITLE
    def _set_table_name(self):
        """Sets the table name."""
        table = self.table_list[self.current_index]
        table_name = os.path.splitext(os.path.basename(table["vpx_file"]))[0]  # Get file name without extension
        self.table_name_label.setText(table_name)
        self.table_name_label.setFont(QFont(FONT_NAME, FONT_SIZE))
        # Ensure the label's size is adjusted to the text
        self.table_name_label.adjustSize()

        # Get the height of the text based on the current font size
        font_metrics = QFontMetrics(self.table_name_label.font())

        # Update label geometry to match the height of the text
        # Here, we calculate the Y position dynamically based on the table index
        label_height = font_metrics.height()  # Get the height of the text
        y_position = MAIN_WINDOW_HEIGHT - label_height - (self.current_index * (label_height))  # Adjust based on index

        # Make sure the table name label is positioned correctly for all tables
        self.table_name_label.setGeometry(10, y_position, MAIN_WINDOW_WIDTH - 20, label_height)

        # Set the style
        self.table_name_label.setStyleSheet(f"color: {TEXT_COLOR}; text-align: left; background-color: {BG_COLOR};")
        self._update_table_name_label_geometry()

    def _update_table_name_label_geometry(self):
        """Update the geometry of the table name label to fit its text and keep it on screen."""
        font_metrics = QFontMetrics(self.table_name_label.font())
        text = self.table_name_label.text()

        try:
            text_width = font_metrics.horizontalAdvance(text)
        except AttributeError:
            text_width = font_metrics.width(text)
        
        label_height = font_metrics.height()
        padding      = 10  # add 10 pixels of padding on all sides
        label_width  = text_width + 2 * padding
        label_height = label_height + 2 * padding
        x_position   = 10  # fixed left margin
        y_position   = MAIN_WINDOW_HEIGHT - label_height - 20  # fixed 20-pixel margin from the bottom
        self.table_name_label.setGeometry(x_position, y_position, label_width, label_height)

    ##--- Change ALL IMAGES (switch table)
    # FADE OUT table transition
    def update_images(self):
        """Update images with fade out animation across all displays."""
        table = self.table_list[self.current_index]

        # Prepare new pixmaps for table and wheel images
        table_pixmap = QPixmap(table["table_img"])
        if table_pixmap.isNull():
            table_pixmap = QPixmap(MAIN_WINDOW_WIDTH, MAIN_WINDOW_HEIGHT)
            table_pixmap.fill(Qt.black)
        table_scaled = table_pixmap.scaled(MAIN_WINDOW_WIDTH, MAIN_WINDOW_HEIGHT,
                                        Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)

        wheel_pixmap = QPixmap(table["wheel_img"])
        if wheel_pixmap.isNull():
            wheel_pixmap = QPixmap(WHEEL_IMAGE_SIZE, WHEEL_IMAGE_SIZE)
            wheel_pixmap.fill(Qt.transparent)
        wheel_scaled = wheel_pixmap.scaled(WHEEL_IMAGE_SIZE, WHEEL_IMAGE_SIZE,
                                        Qt.KeepAspectRatio, Qt.SmoothTransformation)

        # Update the table name label
        table_name = os.path.splitext(os.path.basename(table["vpx_file"]))[0]  # Get file name without extension
        self.table_name_label.setText(table_name)
        self.table_name_label.adjustSize()  # Adjust the label width to fit the name
        self.table_name_label.setStyleSheet(f"color: {TEXT_COLOR}; text-align: left; background-color: {BG_COLOR};")
        self._update_table_name_label_geometry()

        # Fade out all elements
        self.fade_out_table = QPropertyAnimation(self.table_effect, b"opacity")
        self.fade_out_table.setDuration(FADE_DURATION // 2)
        self.fade_out_table.setStartValue(1.0)
        self.fade_out_table.setEndValue(FADE_OPACITY)
        self.fade_out_table.setEasingCurve(QEasingCurve.InQuad)

        self.fade_out_wheel = QPropertyAnimation(self.wheel_effect, b"opacity")
        self.fade_out_wheel.setDuration(FADE_DURATION // 2)
        self.fade_out_wheel.setStartValue(1.0)
        self.fade_out_wheel.setEndValue(FADE_OPACITY)
        self.fade_out_wheel.setEasingCurve(QEasingCurve.InQuad)

        self.fade_out_backglass = QPropertyAnimation(self.secondary.backglass_effect, b"opacity") if self.secondary else None
        if self.fade_out_backglass:
            self.fade_out_backglass.setDuration(FADE_DURATION // 2)
            self.fade_out_backglass.setStartValue(1.0)
            self.fade_out_backglass.setEndValue(FADE_OPACITY)
            self.fade_out_backglass.setEasingCurve(QEasingCurve.InQuad)

        self.fade_out_table.finished.connect(lambda: self._set_new_images(table_scaled, wheel_scaled, table["backglass_img"], table["folder"]))
        self.fade_out_table.start()
        self.fade_out_wheel.start()
        if self.fade_out_backglass:
            self.fade_out_backglass.start()

    # FADE IN table transition
    def _set_new_images(self, table_pixmap, wheel_pixmap, backglass_path, table_folder):
        """Set new images and fade in all displays."""
        self.table_label.setPixmap(table_pixmap)
        self.wheel_label.setPixmap(wheel_pixmap)
        if self.secondary:
            self.secondary.update_image(backglass_path, table_folder)

        # Fade in all elements
        self.fade_in_table = QPropertyAnimation(self.table_effect, b"opacity")
        self.fade_in_table.setDuration(FADE_DURATION // 2)
        self.fade_in_table.setStartValue(FADE_OPACITY)
        self.fade_in_table.setEndValue(1.0)
        self.fade_in_table.setEasingCurve(QEasingCurve.OutQuad)
        self.fade_in_table.start()

        self.fade_in_wheel = QPropertyAnimation(self.wheel_effect, b"opacity")
        self.fade_in_wheel.setDuration(FADE_DURATION // 2)
        self.fade_in_wheel.setStartValue(FADE_OPACITY)
        self.fade_in_wheel.setEndValue(1.0)
        self.fade_in_wheel.setEasingCurve(QEasingCurve.OutQuad)
        self.fade_in_wheel.start()

        if self.secondary:
            self.fade_in_backglass = QPropertyAnimation(self.secondary.backglass_effect, b"opacity")
            self.fade_in_backglass.setDuration(FADE_DURATION // 2)
            self.fade_in_backglass.setStartValue(FADE_OPACITY)
            self.fade_in_backglass.setEndValue(1.0)
            self.fade_in_backglass.setEasingCurve(QEasingCurve.OutQuad)
            self.fade_in_backglass.start()

    ##--- PLAY
    def launch_table(self):
        """Launch the current table."""
        table = self.table_list[self.current_index]
        command = [EXECUTABLE_CMD, EXECUTABLE_SUB_CMD, table["vpx_file"]]
        try:
            # Launch the game and wait for it to finish
            process = subprocess.Popen(command)
            process.wait()
        except Exception as e:
            print(f"Error launching {table['vpx_file']}: {e}")

    ##--- SETTINGS
    def openSettings(self):
        """Opens settings dialog, saves settings if accepted, and updates configuration and UI."""
        dialog = SettingsDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            values = dialog.getValues()
            config = configparser.ConfigParser()

            # Read existing configuration
            ini_file = os.path.expanduser(CONFIG_FILE)
            config.read(ini_file)

            # Update the configuration with new values
            config['Main Paths'] = {
                "VPX_ROOT_FOLDER":         values["VPX_ROOT_FOLDER"],
                "EXECUTABLE_CMD":          values["EXECUTABLE_CMD"],
                "EXECUTABLE_SUB_CMD":      values["EXECUTABLE_SUB_CMD"],
            }
            config['Custom Images'] = {
                "TABLE_IMAGE_PATH":        values["TABLE_IMAGE_PATH"],
                "TABLE_WHEEL_PATH":        values["TABLE_WHEEL_PATH"],
                "TABLE_BACKGLASS_PATH":    values["TABLE_BACKGLASS_PATH"],
                "VIDEO_DMD_PATH":          values["VIDEO_DMD_PATH"],
            }
            config['Main Window'] = {
                "MAIN_MONITOR_INDEX":      values["MAIN_MONITOR_INDEX"],
                "MAIN_WINDOW_WIDTH":       values["MAIN_WINDOW_WIDTH"],
                "MAIN_WINDOW_HEIGHT":      values["MAIN_WINDOW_HEIGHT"],
                "WHEEL_IMAGE_SIZE":        values["WHEEL_IMAGE_SIZE"],
                "WHEEL_IMAGE_MARGIN":      values["WHEEL_IMAGE_MARGIN"],
                "FONT_NAME":               values["FONT_NAME"],
                "FONT_SIZE":               values["FONT_SIZE"],
                "BG_COLOR":                values["BG_COLOR"],
                "TEXT_COLOR":              values["TEXT_COLOR"],
            }
            config['Secondary Window'] = {
                "SECONDARY_MONITOR_INDEX": values["SECONDARY_MONITOR_INDEX"],
                "BACKGLASS_WINDOW_WIDTH":  values["BACKGLASS_WINDOW_WIDTH"],
                "BACKGLASS_WINDOW_HEIGHT": values["BACKGLASS_WINDOW_HEIGHT"],
                "BACKGLASS_IMAGE_WIDTH":   values["BACKGLASS_IMAGE_WIDTH"],
                "BACKGLASS_IMAGE_HEIGHT":  values["BACKGLASS_IMAGE_HEIGHT"],
                "DMD_WIDTH":               values["DMD_WIDTH"],
                "DMD_HEIGHT":              values["DMD_HEIGHT"],
            }
            config['Transitions'] = {
                "FADE_DURATION":           values["FADE_DURATION"],
                "FADE_OPACITY":            values["FADE_OPACITY"],
            }

            # Ensure the directory exists
            directory = os.path.dirname(ini_file)
            if not os.path.exists(directory):
                os.makedirs(directory)

            try:
                with open(ini_file, "w") as f:
                    config.write(f)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save settings: {e}")
                return  # exit the function if error.

            load_configuration()
            self._set_table_name()
            self.apply_settings()
            self.table_list = load_table_list()
            # self.update_images()
        self.setFocus()

    ##--- APPLY SETTINGS
    def apply_settings(self):
        """Apply settings to update the visuals immediately."""
        self.setFixedSize(MAIN_WINDOW_WIDTH, MAIN_WINDOW_HEIGHT)
        self.table_label.setGeometry(0, 0, MAIN_WINDOW_WIDTH, MAIN_WINDOW_HEIGHT)
        self.table_name_label.setFont(QFont(FONT_NAME, FONT_SIZE))
        self.table_name_label.setStyleSheet(f"color: {TEXT_COLOR}; text-align: left; background-color: {BG_COLOR};")
        self.settingsButton.move(MAIN_WINDOW_WIDTH - 50, 10)
        wheel_x = MAIN_WINDOW_WIDTH - WHEEL_IMAGE_SIZE - WHEEL_IMAGE_MARGIN
        wheel_y = MAIN_WINDOW_HEIGHT - WHEEL_IMAGE_SIZE - WHEEL_IMAGE_MARGIN
        self.wheel_label.setGeometry(wheel_x, wheel_y, WHEEL_IMAGE_SIZE, WHEEL_IMAGE_SIZE)
        self.update_images()

        if self.secondary:
            self.secondary.setFixedSize(BACKGLASS_WINDOW_WIDTH, BACKGLASS_WINDOW_HEIGHT)
            self.secondary.label.setGeometry(0, 0, BACKGLASS_IMAGE_WIDTH, BACKGLASS_IMAGE_HEIGHT)
            self.secondary.dmd_label.setGeometry(0, BACKGLASS_IMAGE_HEIGHT, DMD_WIDTH, DMD_HEIGHT)

    # ##--- KEY EVENTS
    def keyPressEvent(self, event):
        """Handle key press events to navigate tables, launch a table, or close the window."""
        if event.key() == Qt.Key_Left:
            self.current_index = (self.current_index - 1) % len(self.table_list)
            self.update_images()  # Update images when switching tables
            if self.table_change_sound:
                self.table_change_sound.play()

        elif event.key() == Qt.Key_Right:
            self.current_index = (self.current_index + 1) % len(self.table_list)
            self.update_images()  # Update images when switching tables
            if self.table_change_sound:
                self.table_change_sound.play()

        elif event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.launch_table()  # Launch the table
        elif event.key() == Qt.Key_Escape:
            self.close()  # Close the window
        else:
            super().keyPressEvent(event)  # Handle other key events

    # def keyPressEvent(self, event):
    #     """Handle key press events to navigate tables, launch a table, or close the window."""
    #     if event.key() == Qt.Key_Left:
    #         self.current_index = (self.current_index - 1) % len(self.table_list)
    #         self.update_images()  # Update images when switching tables
    #     elif event.key() == Qt.Key_Right:
    #         self.current_index = (self.current_index + 1) % len(self.table_list)
    #         self.update_images()  # Update images when switching tables
    #     elif event.key() in (Qt.Key_Return, Qt.Key_Enter):
    #         self.launch_table()  # Launch the table
    #     elif event.key() == Qt.Key_Escape:
    #         self.close()  # Close the window
    #     else:
    #         super().keyPressEvent(event)  # Handle other key events

    ##--- QUIT
    def closeEvent(self, event):
        if self.secondary:
            self.secondary.close()
        event.accept()

# ---------------- Main Entry Point ----------------
if __name__ == "__main__":

    session_type = os.environ.get("XDG_SESSION_TYPE", "unknown")
    if session_type.lower() == "wayland":
        print("Running under Wayland. For precise window positioning, consider launching with QT_QPA_PLATFORM=xcb")

    app = QApplication(sys.argv)

    secondary_window = SecondaryWindow()
    secondary_window.show()

    viewer = SingleTableViewer(secondary_window)
    viewer.show()

    screens = QGuiApplication.screens()
    if len(screens) > MAIN_MONITOR_INDEX:
        main_screen = screens[MAIN_MONITOR_INDEX]
        main_geom = main_screen.geometry()
        viewer.windowHandle().setScreen(main_screen)
        viewer.move(main_geom.topLeft())
        viewer.setGeometry(main_geom.x(), main_geom.y(), MAIN_WINDOW_WIDTH, MAIN_WINDOW_HEIGHT)

    if len(screens) > SECONDARY_MONITOR_INDEX:
        secondary_screen = screens[SECONDARY_MONITOR_INDEX]
        sec_geom = secondary_screen.geometry()
        secondary_window.windowHandle().setScreen(secondary_screen)
        secondary_window.move(sec_geom.topLeft())
        secondary_window.setGeometry(sec_geom.x(), sec_geom.y(), BACKGLASS_WINDOW_WIDTH, BACKGLASS_WINDOW_HEIGHT)

    sys.exit(app.exec_())
