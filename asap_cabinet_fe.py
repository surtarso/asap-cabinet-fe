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
        - Table image: table.png (or DEFAULT_TABLE_IMAGE if missing)
        - Backglass image: backglass.png (or DEFAULT_BACKGLASS_IMAGE if missing)
        - Wheel image: wheel.png (or DEFAULT_WHEEL_IMAGE if missing)
        - DMD animation: dmd.gif (or DEFAULT_DMD_VIDEO if missing)
    - Main Window (1080x1920): Displays table image full screen with wheel overlay
    - Secondary Window (1280x1024): Displays backglass image and DMD
    - Uses left/right arrow/shift keys for infinite scrolling between tables
    - All images update with fade animation
    - Press Enter to launch table
    - Settings button to configure for your setup
    - Search button by query (jump to letter soon!)

Dependencies: python3, python3-pyqt5, python3-pyqt5.qtmultimedia

Tarso Galvão - Feb/2025
"""

import os
import sys
import subprocess
import configparser

from PyQt5.QtCore import (
    Qt, QPropertyAnimation, QEasingCurve, QSize, QTimer
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

# ### Configuration Defaults

CONFIG_FILE = os.path.expanduser("~/.asap-cabinet-fe/settings.ini")

# **Default Media Paths**
DEFAULT_TABLE_IMAGE = "img/default_table.png"
DEFAULT_WHEEL_IMAGE = "img/default_wheel.png"
DEFAULT_BACKGLASS_IMAGE = "img/default_backglass.png"
DEFAULT_DMD_VIDEO = "img/default_dmd.gif"

# **UI Elements**
HINT_ARROW_SIZE = 48
HINT_ARROW_COLOR = "white"
HINT_ARROW_BG_COLOR = "#202020"
TOP_ICONS_SIZE = 24
SETTINGS_WIDTH = 500
SETTINGS_HEIGHT = 700

# **Sounds**
SND_TABLE_CHANGE = "snd/table_change.wav"
SND_TABLE_LOAD = "snd/table_load.wav"

# **Settings (Editable via Dialog)**
VPX_ROOT_FOLDER = os.path.expanduser("~/Games/vpinball/build/tables/")
VPX_EXECUTABLE = os.path.expanduser("~/Games/vpinball/build/VPinballX_GL")
EXECUTABLE_SUB_CMD = "-Play"

CUSTOM_TABLE_IMAGE = "images/table.png"
CUSTOM_WHEEL_IMAGE = "images/wheel.png"
CUSTOM_BACKGLASS_IMAGE = "images/backglass.png"
CUSTOM_MARQUEE_IMAGE = "images/marquee.png"
CUSTOM_TABLE_VIDEO = "video/table.gif"
CUSTOM_BACKGLASS_VIDEO = "video/backglass.gif"
CUSTOM_DMD_VIDEO = "video/dmd.gif"

# **Main Window Settings**
MAIN_MONITOR_INDEX = 1
MAIN_WINDOW_WIDTH = 1080
MAIN_WINDOW_HEIGHT = 1920
WHEEL_IMAGE_SIZE = 250
WHEEL_IMAGE_MARGIN = 24
FONT_NAME = "Arial"
FONT_SIZE = 22
BG_COLOR = "#202020"
TEXT_COLOR = "white"

# **Secondary Window Settings**
SECONDARY_MONITOR_INDEX = 0
BACKGLASS_WINDOW_WIDTH = 1024
BACKGLASS_WINDOW_HEIGHT = 1024
BACKGLASS_IMAGE_WIDTH = 1024
BACKGLASS_IMAGE_HEIGHT = 768
DMD_WIDTH = 1024
DMD_HEIGHT = 256

# **Transition Settings**
FADE_DURATION = 300
FADE_OPACITY = 0.5

# ### Configuration Loader

def load_configuration():
    """Load settings from INI file or create one with defaults if it doesn't exist."""
    global VPX_ROOT_FOLDER, VPX_EXECUTABLE, EXECUTABLE_SUB_CMD
    global CUSTOM_TABLE_IMAGE, CUSTOM_WHEEL_IMAGE, CUSTOM_BACKGLASS_IMAGE, CUSTOM_MARQUEE_IMAGE
    global CUSTOM_TABLE_VIDEO, CUSTOM_BACKGLASS_VIDEO, CUSTOM_DMD_VIDEO
    global MAIN_MONITOR_INDEX, MAIN_WINDOW_WIDTH, MAIN_WINDOW_HEIGHT
    global SECONDARY_MONITOR_INDEX, BACKGLASS_WINDOW_WIDTH, BACKGLASS_WINDOW_HEIGHT
    global BACKGLASS_IMAGE_WIDTH, BACKGLASS_IMAGE_HEIGHT, DMD_WIDTH, DMD_HEIGHT
    global WHEEL_IMAGE_SIZE, WHEEL_IMAGE_MARGIN, FONT_NAME, FONT_SIZE
    global BG_COLOR, TEXT_COLOR, FADE_DURATION, FADE_OPACITY

    ini_file = os.path.expanduser(CONFIG_FILE)
    config = configparser.ConfigParser()

    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(ini_file), exist_ok=True)

    if os.path.exists(ini_file):
        config.read(ini_file)
    else:
        # Create default configuration
        config['Main Paths'] = {
            "VPX_ROOT_FOLDER": VPX_ROOT_FOLDER,
            "VPX_EXECUTABLE": VPX_EXECUTABLE,
            "EXECUTABLE_SUB_CMD": EXECUTABLE_SUB_CMD,
        }
        config['Custom Media'] = {
            "CUSTOM_TABLE_IMAGE": CUSTOM_TABLE_IMAGE,
            "CUSTOM_WHEEL_IMAGE": CUSTOM_WHEEL_IMAGE,
            "CUSTOM_BACKGLASS_IMAGE": CUSTOM_BACKGLASS_IMAGE,
            "CUSTOM_MARQUEE_IMAGE": CUSTOM_MARQUEE_IMAGE,
            "CUSTOM_TABLE_VIDEO": CUSTOM_TABLE_VIDEO,
            "CUSTOM_BACKGLASS_VIDEO": CUSTOM_BACKGLASS_VIDEO,
            "CUSTOM_DMD_VIDEO": CUSTOM_DMD_VIDEO,
        }
        config['Main Window'] = {
            "MAIN_MONITOR_INDEX": str(MAIN_MONITOR_INDEX),
            "MAIN_WINDOW_WIDTH": str(MAIN_WINDOW_WIDTH),
            "MAIN_WINDOW_HEIGHT": str(MAIN_WINDOW_HEIGHT),
            "WHEEL_IMAGE_SIZE": str(WHEEL_IMAGE_SIZE),
            "WHEEL_IMAGE_MARGIN": str(WHEEL_IMAGE_MARGIN),
            "FONT_NAME": FONT_NAME,
            "FONT_SIZE": str(FONT_SIZE),
            "BG_COLOR": BG_COLOR,
            "TEXT_COLOR": TEXT_COLOR,
        }
        config['Secondary Window'] = {
            "SECONDARY_MONITOR_INDEX": str(SECONDARY_MONITOR_INDEX),
            "BACKGLASS_WINDOW_WIDTH": str(BACKGLASS_WINDOW_WIDTH),
            "BACKGLASS_WINDOW_HEIGHT": str(BACKGLASS_WINDOW_HEIGHT),
            "BACKGLASS_IMAGE_WIDTH": str(BACKGLASS_IMAGE_WIDTH),
            "BACKGLASS_IMAGE_HEIGHT": str(BACKGLASS_IMAGE_HEIGHT),
            "DMD_WIDTH": str(DMD_WIDTH),
            "DMD_HEIGHT": str(DMD_HEIGHT),
        }
        config['Transition Settings'] = {
            "FADE_DURATION": str(FADE_DURATION),
            "FADE_OPACITY": str(FADE_OPACITY),
        }
        with open(ini_file, "w") as f:
            config.write(f)

    # Load values with defaults as fallback
    p = config['Main Paths']
    VPX_ROOT_FOLDER = p.get("VPX_ROOT_FOLDER", VPX_ROOT_FOLDER)
    VPX_EXECUTABLE = p.get("VPX_EXECUTABLE", VPX_EXECUTABLE)
    EXECUTABLE_SUB_CMD = p.get("EXECUTABLE_SUB_CMD", EXECUTABLE_SUB_CMD)

    ci = config['Custom Media']
    CUSTOM_TABLE_IMAGE = ci.get("CUSTOM_TABLE_IMAGE", CUSTOM_TABLE_IMAGE)
    CUSTOM_WHEEL_IMAGE = ci.get("CUSTOM_WHEEL_IMAGE", CUSTOM_WHEEL_IMAGE)
    CUSTOM_BACKGLASS_IMAGE = ci.get("CUSTOM_BACKGLASS_IMAGE", CUSTOM_BACKGLASS_IMAGE)
    CUSTOM_MARQUEE_IMAGE = ci.get("CUSTOM_MARQUEE_IMAGE", CUSTOM_MARQUEE_IMAGE)
    CUSTOM_TABLE_VIDEO = ci.get("CUSTOM_TABLE_VIDEO", CUSTOM_TABLE_VIDEO)
    CUSTOM_BACKGLASS_VIDEO = ci.get("CUSTOM_BACKGLASS_VIDEO", CUSTOM_BACKGLASS_VIDEO)
    CUSTOM_DMD_VIDEO = ci.get("CUSTOM_DMD_VIDEO", CUSTOM_DMD_VIDEO)

    mw = config['Main Window']
    MAIN_MONITOR_INDEX = int(mw.get("MAIN_MONITOR_INDEX", MAIN_MONITOR_INDEX))
    MAIN_WINDOW_WIDTH = int(mw.get("MAIN_WINDOW_WIDTH", MAIN_WINDOW_WIDTH))
    MAIN_WINDOW_HEIGHT = int(mw.get("MAIN_WINDOW_HEIGHT", MAIN_WINDOW_HEIGHT))
    WHEEL_IMAGE_SIZE = int(mw.get("WHEEL_IMAGE_SIZE", WHEEL_IMAGE_SIZE))
    WHEEL_IMAGE_MARGIN = int(mw.get("WHEEL_IMAGE_MARGIN", WHEEL_IMAGE_MARGIN))
    FONT_NAME = mw.get("FONT_NAME", FONT_NAME)
    FONT_SIZE = int(mw.get("FONT_SIZE", FONT_SIZE))
    BG_COLOR = mw.get("BG_COLOR", BG_COLOR)
    TEXT_COLOR = mw.get("TEXT_COLOR", TEXT_COLOR)

    sw = config['Secondary Window']
    SECONDARY_MONITOR_INDEX = int(sw.get("SECONDARY_MONITOR_INDEX", SECONDARY_MONITOR_INDEX))
    BACKGLASS_WINDOW_WIDTH = int(sw.get("BACKGLASS_WINDOW_WIDTH", BACKGLASS_WINDOW_WIDTH))
    BACKGLASS_WINDOW_HEIGHT = int(sw.get("BACKGLASS_WINDOW_HEIGHT", BACKGLASS_WINDOW_HEIGHT))
    BACKGLASS_IMAGE_WIDTH = int(sw.get("BACKGLASS_IMAGE_WIDTH", BACKGLASS_IMAGE_WIDTH))
    BACKGLASS_IMAGE_HEIGHT = int(sw.get("BACKGLASS_IMAGE_HEIGHT", BACKGLASS_IMAGE_HEIGHT))
    DMD_WIDTH = int(sw.get("DMD_WIDTH", DMD_WIDTH))
    DMD_HEIGHT = int(sw.get("DMD_HEIGHT", DMD_HEIGHT))

    t = config['Transition Settings']
    FADE_DURATION = int(t.get("FADE_DURATION", FADE_DURATION))
    FADE_OPACITY = float(t.get("FADE_OPACITY", FADE_OPACITY))

# Load configuration at startup
load_configuration()

# ### Settings Dialog

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(SETTINGS_WIDTH, SETTINGS_HEIGHT)
        self.setWindowTitle(f"[Settings] {CONFIG_FILE.replace(os.path.expanduser('~'), '~')}")

        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        form_widget = QWidget()
        self.layout = QFormLayout(form_widget)

        # Initialize input fields
        self.vpxRootEdit = QLineEdit(VPX_ROOT_FOLDER)
        self.execCmdEdit = QLineEdit(VPX_EXECUTABLE)
        self.execSubCmdEdit = QLineEdit(EXECUTABLE_SUB_CMD)
        self.tableImageEdit = QLineEdit(CUSTOM_TABLE_IMAGE)
        self.wheelImageEdit = QLineEdit(CUSTOM_WHEEL_IMAGE)
        self.backglassImageEdit = QLineEdit(CUSTOM_BACKGLASS_IMAGE)
        self.marqueeImageEdit = QLineEdit(CUSTOM_MARQUEE_IMAGE)
        self.videoTableEdit = QLineEdit(CUSTOM_TABLE_VIDEO)
        self.videoBackglassEdit = QLineEdit(CUSTOM_BACKGLASS_VIDEO)
        self.dmdTableEdit = QLineEdit(CUSTOM_DMD_VIDEO)
        self.mainMonitor = QLineEdit(str(MAIN_MONITOR_INDEX))
        self.windowWidthEdit = QLineEdit(str(MAIN_WINDOW_WIDTH))
        self.windowHeightEdit = QLineEdit(str(MAIN_WINDOW_HEIGHT))
        self.secondaryMonitor = QLineEdit(str(SECONDARY_MONITOR_INDEX))
        self.backglassWidthEdit = QLineEdit(str(BACKGLASS_WINDOW_WIDTH))
        self.backglassHeightEdit = QLineEdit(str(BACKGLASS_WINDOW_HEIGHT))
        self.backglassImageWidthEdit = QLineEdit(str(BACKGLASS_IMAGE_WIDTH))
        self.backglassImageHeightEdit = QLineEdit(str(BACKGLASS_IMAGE_HEIGHT))
        self.dmdWidthEdit = QLineEdit(str(DMD_WIDTH))
        self.dmdHeightEdit = QLineEdit(str(DMD_HEIGHT))
        self.wheelSizeEdit = QLineEdit(str(WHEEL_IMAGE_SIZE))
        self.wheelMarginEdit = QLineEdit(str(WHEEL_IMAGE_MARGIN))
        self.fontNameEdit = QLineEdit(FONT_NAME)
        self.fontSizeEdit = QLineEdit(str(FONT_SIZE))
        self.bgColorEdit = QLineEdit(BG_COLOR)
        self.textColorEdit = QLineEdit(TEXT_COLOR)
        self.fadeDurationEdit = QLineEdit(str(FADE_DURATION))
        self.fadeOpacityEdit = QLineEdit(str(FADE_OPACITY))

        # Add fields to layout
        self.add_section_title("Main Paths")
        self.layout.addRow("Tables Folder:", self.vpxRootEdit)
        self.layout.addRow("VPX Executable:", self.execCmdEdit)
        self.layout.addRow("VPX Argument:", self.execSubCmdEdit)

        self.add_section_title("Custom Media")
        self.layout.addRow("Playfield Images Path:", self.tableImageEdit)
        self.layout.addRow("Wheel Images Path:", self.wheelImageEdit)
        self.layout.addRow("Backglass Images Path:", self.backglassImageEdit)
        self.layout.addRow("Marquee Images Path:", self.marqueeImageEdit)
        self.layout.addRow("Playfield GIFs Path:", self.videoTableEdit)
        self.layout.addRow("Backglass GIFs Path:", self.videoBackglassEdit)
        self.layout.addRow("DMD GIFs Path:", self.dmdTableEdit)

        self.add_section_title("Main Window")
        self.layout.addRow("Playfield Monitor:", self.mainMonitor)
        self.layout.addRow("Playfield Width:", self.windowWidthEdit)
        self.layout.addRow("Playfield Height:", self.windowHeightEdit)
        self.layout.addRow("Wheel Size:", self.wheelSizeEdit)
        self.layout.addRow("Wheel Margin:", self.wheelMarginEdit)
        self.layout.addRow("Font Name:", self.fontNameEdit)
        self.layout.addRow("Font Size:", self.fontSizeEdit)
        self.layout.addRow("Background Color:", self.bgColorEdit)
        self.layout.addRow("Text Color:", self.textColorEdit)

        self.add_section_title("Secondary Window")
        self.layout.addRow("Backglass Monitor:", self.secondaryMonitor)
        self.layout.addRow("Backglass Width:", self.backglassWidthEdit)
        self.layout.addRow("Backglass Height:", self.backglassHeightEdit)
        self.layout.addRow("Backglass Image Width:", self.backglassImageWidthEdit)
        self.layout.addRow("Backglass Image Height:", self.backglassImageHeightEdit)
        self.layout.addRow("DMD Width:", self.dmdWidthEdit)
        self.layout.addRow("DMD Height:", self.dmdHeightEdit)

        self.add_section_title("Transition Settings")
        self.layout.addRow("Transition Duration:", self.fadeDurationEdit)
        self.layout.addRow("Fade Opacity:", self.fadeOpacityEdit)

        # Add buttons
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.layout.addRow(self.buttonBox)

        ok_button = self.buttonBox.button(QDialogButtonBox.Ok)
        cancel_button = self.buttonBox.button(QDialogButtonBox.Cancel)
        ok_button.setText("")
        cancel_button.setText("")
        square_size = 40
        ok_button.setFixedSize(square_size, square_size)
        cancel_button.setFixedSize(square_size, square_size)
        ok_button.setIconSize(QSize(square_size, square_size))
        cancel_button.setIconSize(QSize(square_size, square_size))

        scroll_area.setWidget(form_widget)
        dialog_layout = QVBoxLayout(self)
        dialog_layout.addWidget(scroll_area)

    def getValues(self):
        """Return current settings values."""
        return {
            "VPX_ROOT_FOLDER": self.vpxRootEdit.text(),
            "VPX_EXECUTABLE": self.execCmdEdit.text(),
            "EXECUTABLE_SUB_CMD": self.execSubCmdEdit.text(),
            "CUSTOM_TABLE_IMAGE": self.tableImageEdit.text(),
            "CUSTOM_WHEEL_IMAGE": self.wheelImageEdit.text(),
            "CUSTOM_BACKGLASS_IMAGE": self.backglassImageEdit.text(),
            "CUSTOM_MARQUEE_IMAGE": self.marqueeImageEdit.text(),
            "CUSTOM_TABLE_VIDEO": self.videoTableEdit.text(),
            "CUSTOM_BACKGLASS_VIDEO": self.videoBackglassEdit.text(),
            "CUSTOM_DMD_VIDEO": self.dmdTableEdit.text(),
            "MAIN_MONITOR_INDEX": self.mainMonitor.text(),
            "MAIN_WINDOW_WIDTH": self.windowWidthEdit.text(),
            "MAIN_WINDOW_HEIGHT": self.windowHeightEdit.text(),
            "SECONDARY_MONITOR_INDEX": self.secondaryMonitor.text(),
            "BACKGLASS_WINDOW_WIDTH": self.backglassWidthEdit.text(),
            "BACKGLASS_WINDOW_HEIGHT": self.backglassHeightEdit.text(),
            "BACKGLASS_IMAGE_WIDTH": self.backglassImageWidthEdit.text(),
            "BACKGLASS_IMAGE_HEIGHT": self.backglassImageHeightEdit.text(),
            "DMD_WIDTH": self.dmdWidthEdit.text(),
            "DMD_HEIGHT": self.dmdHeightEdit.text(),
            "WHEEL_IMAGE_SIZE": self.wheelSizeEdit.text(),
            "WHEEL_IMAGE_MARGIN": self.wheelMarginEdit.text(),
            "FONT_NAME": self.fontNameEdit.text(),
            "FONT_SIZE": self.fontSizeEdit.text(),
            "BG_COLOR": self.bgColorEdit.text(),
            "TEXT_COLOR": self.textColorEdit.text(),
            "FADE_DURATION": self.fadeDurationEdit.text(),
            "FADE_OPACITY": self.fadeOpacityEdit.text()
        }

    def add_section_title(self, title):
        """Add a styled section title."""
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 14px; padding: 5px;")
        self.layout.addWidget(title_label)

    def accept(self):
        """Validate settings before accepting."""
        values = self.getValues()
        errors = self.validate_settings(values)
        if errors:
            QMessageBox.critical(self, "Validation Error", "\n".join(errors))
        else:
            super().accept()

    def validate_settings(self, values):
        """Validate critical settings."""
        errors = []
        root_folder = values["VPX_ROOT_FOLDER"]
        if not os.path.isdir(root_folder):
            errors.append(f"VPX_ROOT_FOLDER '{root_folder}' is not a valid directory.")
        else:
            has_vpx = any(file.lower().endswith(".vpx") for root, _, files in os.walk(root_folder) for file in files)
            if not has_vpx:
                errors.append(f"No .vpx files found in VPX_ROOT_FOLDER '{root_folder}'.")
        executable = values["VPX_EXECUTABLE"]
        if not os.path.isfile(executable):
            errors.append(f"VPX_EXECUTABLE '{executable}' is not a valid file.")
        elif not os.access(executable, os.X_OK):
            errors.append(f"VPX_EXECUTABLE '{executable}' is not executable.")
        return errors

# ### Table Data Loader

def get_image_path(root, preferred_media_path, fallback_media_path, default_media_path):
    """Return the first existing media path or default."""
    preferred_path = os.path.join(root, preferred_media_path)
    if os.path.exists(preferred_path):
        return preferred_path
    fallback_path = os.path.join(root, fallback_media_path)
    if os.path.exists(fallback_path):
        return fallback_path
    return default_media_path

def load_table_list():
    """Load and sort table data from VPX_ROOT_FOLDER."""
    tables = []
    for root, _, files in os.walk(VPX_ROOT_FOLDER):
        for file in files:
            if file.lower().endswith(".vpx"):
                table_name = os.path.splitext(file)[0]
                vpx_path = os.path.join(root, file)
                tables.append({
                    "table_name": table_name,
                    "vpx_file": vpx_path,
                    "folder": root,
                    "table_img": get_image_path(root, CUSTOM_TABLE_VIDEO, CUSTOM_TABLE_IMAGE, DEFAULT_TABLE_IMAGE),
                    "wheel_img": get_image_path(root, CUSTOM_WHEEL_IMAGE, CUSTOM_WHEEL_IMAGE, DEFAULT_WHEEL_IMAGE),
                    "backglass_img": get_image_path(root, CUSTOM_BACKGLASS_VIDEO, CUSTOM_BACKGLASS_IMAGE, DEFAULT_BACKGLASS_IMAGE),
                    "dmd_img": get_image_path(root, CUSTOM_DMD_VIDEO, CUSTOM_MARQUEE_IMAGE, DEFAULT_DMD_VIDEO)
                })
    tables.sort(key=lambda x: x["table_name"])
    return tables

# ### Secondary Window

class SecondaryWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Secondary Display (Backglass)")
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setFixedSize(BACKGLASS_WINDOW_WIDTH, BACKGLASS_WINDOW_HEIGHT)
        self.setStyleSheet("background-color: black;")

        self.label = QLabel(self)
        self.label.setGeometry(0, 0, BACKGLASS_IMAGE_WIDTH, BACKGLASS_IMAGE_HEIGHT)
        self.label.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        self.backglass_effect = QGraphicsOpacityEffect(self.label)
        self.label.setGraphicsEffect(self.backglass_effect)
        self.backglass_effect.setOpacity(1.0)

        self.dmd_label = QLabel(self)
        self.dmd_label.setGeometry(0, BACKGLASS_IMAGE_HEIGHT, DMD_WIDTH, DMD_HEIGHT)
        self.dmd_label.setStyleSheet("background-color: black;")
        self.dmd_label.setAlignment(Qt.AlignCenter)

    def update_image(self, image_path, table_folder):
        """Update backglass and DMD media."""
        if image_path.lower().endswith('.gif') and os.path.exists(image_path):
            self.backglass_movie = QMovie(image_path)
            self.backglass_movie.setCacheMode(QMovie.CacheAll)
            self.backglass_movie.start()
            frame_size = self.backglass_movie.currentPixmap().size()
            self.backglass_movie.stop()
            width, height = frame_size.width(), frame_size.height()
            if width > 0 and height > 0:
                aspect_ratio = width / height
                new_width = min(BACKGLASS_IMAGE_WIDTH, int(BACKGLASS_IMAGE_HEIGHT * aspect_ratio))
                new_height = min(BACKGLASS_IMAGE_HEIGHT, int(BACKGLASS_IMAGE_WIDTH / aspect_ratio))
                if new_width > BACKGLASS_IMAGE_WIDTH:
                    new_width = BACKGLASS_IMAGE_WIDTH
                    new_height = int(BACKGLASS_IMAGE_WIDTH / aspect_ratio)
                if new_height > BACKGLASS_IMAGE_HEIGHT:
                    new_height = BACKGLASS_IMAGE_HEIGHT
                    new_width = int(BACKGLASS_IMAGE_HEIGHT * aspect_ratio)
                self.label.setGeometry(
                    (BACKGLASS_IMAGE_WIDTH - new_width) // 2,
                    (BACKGLASS_IMAGE_HEIGHT - new_height) // 2,
                    new_width, new_height
                )
                self.backglass_movie.setScaledSize(QSize(new_width, new_height))
            self.label.setMovie(self.backglass_movie)
            self.backglass_movie.start()
        else:
            pixmap = QPixmap(image_path)
            if pixmap.isNull():
                pixmap = QPixmap(BACKGLASS_IMAGE_WIDTH, BACKGLASS_IMAGE_HEIGHT).fill(Qt.black)
            else:
                pixmap = pixmap.scaled(BACKGLASS_IMAGE_WIDTH, BACKGLASS_IMAGE_HEIGHT,
                                       Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.label.setPixmap(pixmap)
            self.backglass_effect.setOpacity(1.0)

        dmd_path = os.path.join(table_folder, CUSTOM_DMD_VIDEO) if os.path.exists(os.path.join(table_folder, CUSTOM_DMD_VIDEO)) else \
                   os.path.join(table_folder, CUSTOM_MARQUEE_IMAGE) if os.path.exists(os.path.join(table_folder, CUSTOM_MARQUEE_IMAGE)) else \
                   DEFAULT_DMD_VIDEO

        if dmd_path.lower().endswith('.gif'):
            self.dmd_movie = QMovie(dmd_path)
            self.dmd_movie.setCacheMode(QMovie.CacheAll)
            self.dmd_movie.start()
            frame_size = self.dmd_movie.currentPixmap().size()
            self.dmd_movie.stop()
            width, height = frame_size.width(), frame_size.height()
            if width > 0 and height > 0:
                aspect_ratio = width / height
                new_width = min(DMD_WIDTH, int(DMD_HEIGHT * aspect_ratio))
                new_height = min(DMD_HEIGHT, int(DMD_WIDTH / aspect_ratio))
                if new_width > DMD_WIDTH:
                    new_width = DMD_WIDTH
                    new_height = int(DMD_WIDTH / aspect_ratio)
                if new_height > DMD_HEIGHT:
                    new_height = DMD_HEIGHT
                    new_width = int(DMD_HEIGHT * aspect_ratio)
                self.dmd_movie.setScaledSize(QSize(new_width, new_height))
                self.dmd_label.setGeometry(
                    (DMD_WIDTH - new_width) // 2,
                    BACKGLASS_IMAGE_HEIGHT + (DMD_HEIGHT - new_height) // 2,
                    new_width, new_height
                )
            self.dmd_label.setMovie(self.dmd_movie)
            self.dmd_movie.start()
        else:
            dmd_pixmap = QPixmap(dmd_path)
            if dmd_pixmap.isNull():
                dmd_pixmap = QPixmap(DMD_WIDTH, DMD_HEIGHT).fill(Qt.black)
            else:
                dmd_pixmap = dmd_pixmap.scaled(DMD_WIDTH, DMD_HEIGHT,
                                               Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.dmd_label.setPixmap(dmd_pixmap)

# ### Search Dialog

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

# ### Main Window

class SingleTableViewer(QMainWindow):
    def __init__(self, secondary_window=None):
        super().__init__()
        self.setWindowTitle("Primary Display (Table Viewer)")
        self.setFixedSize(MAIN_WINDOW_WIDTH, MAIN_WINDOW_HEIGHT)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.secondary = secondary_window

        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(BG_COLOR))
        self.setPalette(palette)

        self.table_list = load_table_list()
        self.current_index = 0

        central = QWidget(self)
        self.setCentralWidget(central)
        central.setFocusPolicy(Qt.StrongFocus)
        central.setStyleSheet(f"background-color: {BG_COLOR};")
        self.setFocus()

        # **Table Image**
        self.table_label = QLabel(central)
        self.table_label.setGeometry(0, 0, MAIN_WINDOW_WIDTH, MAIN_WINDOW_HEIGHT)
        self.table_label.setScaledContents(True)
        self.table_effect = QGraphicsOpacityEffect(self.table_label)
        self.table_label.setGraphicsEffect(self.table_effect)

        # **Table Name**
        self.table_name_label = QLabel(central)
        self.table_name_label.setGeometry(10, MAIN_WINDOW_HEIGHT - 30, MAIN_WINDOW_WIDTH - 20, 30)
        self.table_name_label.setStyleSheet(f"color: {TEXT_COLOR}; font-size: {FONT_SIZE}px; background-color: {BG_COLOR};")
        self.table_name_label.setAlignment(Qt.AlignCenter)
        self._set_table_name()

        # **Settings Button**
        self.settingsButton = QPushButton("⚙", central)
        self.settingsButton.setFixedSize(40, 40)
        self.settingsButton.move(MAIN_WINDOW_WIDTH - 50, 10)
        self.settingsButton.setFocusPolicy(Qt.NoFocus)
        self.settingsButton.clicked.connect(self.openSettings)
        self.settingsButton.setStyleSheet(f"font-size: {TOP_ICONS_SIZE}px; border: none; background: transparent;")
        self.settingsButton.raise_()

        # **Search Button**
        self.searchButton = QPushButton("🔍", central)
        self.searchButton.setFixedSize(40, 40)
        self.searchButton.move(10, 15)
        self.searchButton.setFocusPolicy(Qt.NoFocus)
        self.searchButton.clicked.connect(self.openSearch)
        self.searchButton.setStyleSheet(f"font-size: {TOP_ICONS_SIZE}px; border: none; background: transparent;")
        self.searchButton.raise_()

        # **Wheel Image**
        wheel_x = MAIN_WINDOW_WIDTH - WHEEL_IMAGE_SIZE - WHEEL_IMAGE_MARGIN
        wheel_y = MAIN_WINDOW_HEIGHT - WHEEL_IMAGE_SIZE - WHEEL_IMAGE_MARGIN
        self.wheel_label = QLabel(central)
        self.wheel_label.setGeometry(wheel_x, wheel_y, WHEEL_IMAGE_SIZE, WHEEL_IMAGE_SIZE)
        self.wheel_label.setScaledContents(True)
        self.wheel_label.setStyleSheet("background-color: transparent;")
        self.wheel_effect = QGraphicsOpacityEffect(self.wheel_label)
        self.wheel_label.setGraphicsEffect(self.wheel_effect)

        # **Hint Arrows**
        self.left_arrow = QLabel("←", central)
        self.right_arrow = QLabel("→", central)
        arrow_style = f"padding-bottom: 5px; color: {HINT_ARROW_COLOR}; font-size: {HINT_ARROW_SIZE}px; background-color: {HINT_ARROW_BG_COLOR};"
        self.left_arrow.setStyleSheet(arrow_style)
        self.right_arrow.setStyleSheet(arrow_style)
        self.left_arrow.setAlignment(Qt.AlignCenter)
        self.right_arrow.setAlignment(Qt.AlignCenter)
        arrow_y = (2 * MAIN_WINDOW_HEIGHT) // 3 - 25
        self.left_arrow.setGeometry(10, arrow_y, 50, 50)
        self.right_arrow.setGeometry(MAIN_WINDOW_WIDTH - 60, arrow_y, 50, 50)
        self.left_arrow_effect = QGraphicsOpacityEffect(self.left_arrow)
        self.right_arrow_effect = QGraphicsOpacityEffect(self.right_arrow)
        self.left_arrow.setGraphicsEffect(self.left_arrow_effect)
        self.right_arrow.setGraphicsEffect(self.right_arrow_effect)
        for anim in [QPropertyAnimation(self.left_arrow_effect, b"opacity"), QPropertyAnimation(self.right_arrow_effect, b"opacity")]:
            anim.setDuration(1000)
            anim.setStartValue(1.0)
            anim.setKeyValueAt(0.5, 0.5)
            anim.setEndValue(1.0)
            anim.setEasingCurve(QEasingCurve.InOutQuad)
            anim.setLoopCount(-1)
            anim.start()

        # **Sounds**
        self.table_change_sound = QSound(SND_TABLE_CHANGE) if os.path.exists(SND_TABLE_CHANGE) else None
        self.table_load_sound = QSound(SND_TABLE_LOAD) if os.path.exists(SND_TABLE_LOAD) else None

        # **Initial Display**
        self.update_images()

        # **Validate Configuration at Startup**
        if not self.table_list or not os.path.isfile(VPX_EXECUTABLE) or not os.access(VPX_EXECUTABLE, os.X_OK):
            if self.openSettings() == QDialog.Rejected:
                sys.exit(1)

    def openSearch(self):
        """Open search dialog and update table if found."""
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

    def _set_table_name(self):
        """Set the current table name."""
        if self.table_list:
            table_name = os.path.splitext(os.path.basename(self.table_list[self.current_index]["vpx_file"]))[0]
            self.table_name_label.setText(table_name)
            self.table_name_label.setFont(QFont(FONT_NAME, FONT_SIZE))
            self._update_table_name_label_geometry()

    def _update_table_name_label_geometry(self):
        """Adjust table name label size and position."""
        font_metrics = QFontMetrics(self.table_name_label.font())
        text_width = font_metrics.horizontalAdvance(self.table_name_label.text())
        label_height = font_metrics.height()
        padding = 10
        self.table_name_label.setGeometry(
            10, MAIN_WINDOW_HEIGHT - label_height - 20,
            text_width + 2 * padding, label_height + 2 * padding
        )

    def update_images(self):
        """Update all images with fade animation."""
        if not self.table_list:
            return
        table = self.table_list[self.current_index]
        playing_gif = False

        if table["table_img"].lower().endswith('.gif') and os.path.exists(table["table_img"]):
            self.table_movie = QMovie(table["table_img"])
            self.table_movie.setCacheMode(QMovie.CacheAll)
            self.table_movie.start()
            frame_size = self.table_movie.currentPixmap().size()
            self.table_movie.stop()
            if frame_size.width() > 0 and frame_size.height() > 0:
                aspect_ratio = frame_size.width() / frame_size.height()
                new_width = min(MAIN_WINDOW_WIDTH, int(MAIN_WINDOW_HEIGHT * aspect_ratio))
                new_height = min(MAIN_WINDOW_HEIGHT, int(MAIN_WINDOW_WIDTH / aspect_ratio))
                if new_width > MAIN_WINDOW_WIDTH:
                    new_width = MAIN_WINDOW_WIDTH
                    new_height = int(MAIN_WINDOW_WIDTH / aspect_ratio)
                if new_height > MAIN_WINDOW_HEIGHT:
                    new_height = MAIN_WINDOW_HEIGHT
                    new_width = int(MAIN_WINDOW_HEIGHT * aspect_ratio)
                self.table_movie.setScaledSize(QSize(new_width, new_height))
                self.table_label.setGeometry(
                    (MAIN_WINDOW_WIDTH - new_width) // 2,
                    (MAIN_WINDOW_HEIGHT - new_height) // 2,
                    new_width, new_height
                )
            self.table_label.setMovie(self.table_movie)
            self.table_movie.start()
            playing_gif = True
        else:
            table_pixmap = QPixmap(table["table_img"])
            if table_pixmap.isNull():
                table_pixmap = QPixmap(MAIN_WINDOW_WIDTH, MAIN_WINDOW_HEIGHT).fill(Qt.black)
            table_scaled = table_pixmap.scaled(MAIN_WINDOW_WIDTH, MAIN_WINDOW_HEIGHT,
                                               Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            self.table_label.setPixmap(table_scaled)

        wheel_pixmap = QPixmap(table["wheel_img"])
        if wheel_pixmap.isNull():
            wheel_pixmap = QPixmap(WHEEL_IMAGE_SIZE, WHEEL_IMAGE_SIZE).fill(Qt.transparent)
        wheel_scaled = wheel_pixmap.scaled(WHEEL_IMAGE_SIZE, WHEEL_IMAGE_SIZE,
                                           Qt.KeepAspectRatio, Qt.SmoothTransformation)

        self.table_name_label.setText(os.path.splitext(os.path.basename(table["vpx_file"]))[0])
        self.table_name_label.setStyleSheet(f"color: {TEXT_COLOR}; background-color: {BG_COLOR};")
        self._update_table_name_label_geometry()

        # **Fade Out**
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

        if self.secondary:
            self.fade_out_backglass = QPropertyAnimation(self.secondary.backglass_effect, b"opacity")
            self.fade_out_backglass.setDuration(FADE_DURATION // 2)
            self.fade_out_backglass.setStartValue(1.0)
            self.fade_out_backglass.setEndValue(FADE_OPACITY)
            self.fade_out_backglass.setEasingCurve(QEasingCurve.InQuad)

        self.fade_out_table.finished.connect(lambda: self._set_new_images(
            None if playing_gif else table_scaled, wheel_scaled, table["backglass_img"], table["folder"]
        ))

        self.fade_out_table.start()
        self.fade_out_wheel.start()
        if self.secondary and hasattr(self, 'fade_out_backglass'):
            self.fade_out_backglass.start()

    def _set_new_images(self, table_pixmap, wheel_pixmap, backglass_path, table_folder):
        """Set new images and fade in."""
        if table_pixmap:
            self.table_label.setPixmap(table_pixmap)
        self.wheel_label.setPixmap(wheel_pixmap)
        if self.secondary:
            self.secondary.update_image(backglass_path, table_folder)

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

    def launch_table(self):
        """Launch the selected table."""
        if not self.table_list:
            return
        table = self.table_list[self.current_index]
        command = [VPX_EXECUTABLE, EXECUTABLE_SUB_CMD, table["vpx_file"]]
        if self.table_load_sound:
            self.table_load_sound.play()
        try:
            subprocess.Popen(command).wait()
        except Exception as e:
            print(f"Error launching {table['vpx_file']}: {e}")

    def openSettings(self):
        """Open settings dialog and apply changes if accepted."""
        dialog = SettingsDialog(self)
        result = dialog.exec_()
        if result == QDialog.Accepted:
            values = dialog.getValues()
            config = configparser.ConfigParser()
            config['Main Paths'] = {
                "VPX_ROOT_FOLDER": values["VPX_ROOT_FOLDER"],
                "VPX_EXECUTABLE": values["VPX_EXECUTABLE"],
                "EXECUTABLE_SUB_CMD": values["EXECUTABLE_SUB_CMD"],
            }
            config['Custom Media'] = {
                "CUSTOM_TABLE_IMAGE": values["CUSTOM_TABLE_IMAGE"],
                "CUSTOM_WHEEL_IMAGE": values["CUSTOM_WHEEL_IMAGE"],
                "CUSTOM_BACKGLASS_IMAGE": values["CUSTOM_BACKGLASS_IMAGE"],
                "CUSTOM_MARQUEE_IMAGE": values["CUSTOM_MARQUEE_IMAGE"],
                "CUSTOM_TABLE_VIDEO": values["CUSTOM_TABLE_VIDEO"],
                "CUSTOM_BACKGLASS_VIDEO": values["CUSTOM_BACKGLASS_VIDEO"],
                "CUSTOM_DMD_VIDEO": values["CUSTOM_DMD_VIDEO"],
            }
            config['Main Window'] = {
                "MAIN_MONITOR_INDEX": values["MAIN_MONITOR_INDEX"],
                "MAIN_WINDOW_WIDTH": values["MAIN_WINDOW_WIDTH"],
                "MAIN_WINDOW_HEIGHT": values["MAIN_WINDOW_HEIGHT"],
                "WHEEL_IMAGE_SIZE": values["WHEEL_IMAGE_SIZE"],
                "WHEEL_IMAGE_MARGIN": values["WHEEL_IMAGE_MARGIN"],
                "FONT_NAME": values["FONT_NAME"],
                "FONT_SIZE": values["FONT_SIZE"],
                "BG_COLOR": values["BG_COLOR"],
                "TEXT_COLOR": values["TEXT_COLOR"],
            }
            config['Secondary Window'] = {
                "SECONDARY_MONITOR_INDEX": values["SECONDARY_MONITOR_INDEX"],
                "BACKGLASS_WINDOW_WIDTH": values["BACKGLASS_WINDOW_WIDTH"],
                "BACKGLASS_WINDOW_HEIGHT": values["BACKGLASS_WINDOW_HEIGHT"],
                "BACKGLASS_IMAGE_WIDTH": values["BACKGLASS_IMAGE_WIDTH"],
                "BACKGLASS_IMAGE_HEIGHT": values["BACKGLASS_IMAGE_HEIGHT"],
                "DMD_WIDTH": values["DMD_WIDTH"],
                "DMD_HEIGHT": values["DMD_HEIGHT"],
            }
            config['Transition Settings'] = {
                "FADE_DURATION": values["FADE_DURATION"],
                "FADE_OPACITY": values["FADE_OPACITY"],
            }
            ini_file = os.path.expanduser(CONFIG_FILE)
            os.makedirs(os.path.dirname(ini_file), exist_ok=True)
            with open(ini_file, "w") as f:
                config.write(f)
            load_configuration()
            self.apply_settings()
            self.table_list = load_table_list()
            if not self.table_list:
                QMessageBox.critical(self, "Error", "No tables found after updating settings.")
                sys.exit(1)
            if self.current_index >= len(self.table_list):
                self.current_index = 0
            self.update_images()
        self.setFocus()
        return result

    def apply_settings(self):
        """Apply settings to UI elements."""
        self.setFixedSize(MAIN_WINDOW_WIDTH, MAIN_WINDOW_HEIGHT)
        self.table_label.setGeometry(0, 0, MAIN_WINDOW_WIDTH, MAIN_WINDOW_HEIGHT)
        self.table_name_label.setFont(QFont(FONT_NAME, FONT_SIZE))
        self.table_name_label.setStyleSheet(f"color: {TEXT_COLOR}; background-color: {BG_COLOR};")
        self.settingsButton.move(MAIN_WINDOW_WIDTH - 50, 10)
        wheel_x = MAIN_WINDOW_WIDTH - WHEEL_IMAGE_SIZE - WHEEL_IMAGE_MARGIN
        wheel_y = MAIN_WINDOW_HEIGHT - WHEEL_IMAGE_SIZE - WHEEL_IMAGE_MARGIN
        self.wheel_label.setGeometry(wheel_x, wheel_y, WHEEL_IMAGE_SIZE, WHEEL_IMAGE_SIZE)
        self._set_table_name()
        if self.secondary:
            self.secondary.setFixedSize(BACKGLASS_WINDOW_WIDTH, BACKGLASS_WINDOW_HEIGHT)
            self.secondary.label.setGeometry(0, 0, BACKGLASS_IMAGE_WIDTH, BACKGLASS_IMAGE_HEIGHT)
            self.secondary.dmd_label.setGeometry(0, BACKGLASS_IMAGE_HEIGHT, DMD_WIDTH, DMD_HEIGHT)

    def keyPressEvent(self, event):
        """Handle navigation and table launch."""
        if event.key() == Qt.Key_Left and self.table_list:
            self.current_index = (self.current_index - 1) % len(self.table_list)
            self.update_images()
            if self.table_change_sound:
                self.table_change_sound.play()
        elif event.key() == Qt.Key_Right and self.table_list:
            self.current_index = (self.current_index + 1) % len(self.table_list)
            self.update_images()
            if self.table_change_sound:
                self.table_change_sound.play()
        elif event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.launch_table()
        elif event.key() == Qt.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)

    def closeEvent(self, event):
        if self.secondary:
            self.secondary.close()
        event.accept()

# ### Main Entry Point

if __name__ == "__main__":
    if os.environ.get("XDG_SESSION_TYPE", "unknown").lower() == "wayland":
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
        viewer.setGeometry(main_geom.x(), main_geom.y(), MAIN_WINDOW_WIDTH, MAIN_WINDOW_HEIGHT)
    if len(screens) > SECONDARY_MONITOR_INDEX:
        secondary_screen = screens[SECONDARY_MONITOR_INDEX]
        sec_geom = secondary_screen.geometry()
        secondary_window.windowHandle().setScreen(secondary_screen)
        secondary_window.setGeometry(sec_geom.x(), sec_geom.y(), BACKGLASS_WINDOW_WIDTH, BACKGLASS_WINDOW_HEIGHT)

    is_ci = any(os.environ.get(var) == "true" for var in ["CI", "GITHUB_ACTIONS", "TRAVIS", "CIRCLECI"])
    if is_ci:
        print("Running in CI, will exit in 5 seconds")
        QTimer.singleShot(5000, app.quit)

    sys.exit(app.exec_())