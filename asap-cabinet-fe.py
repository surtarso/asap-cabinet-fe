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
- Main Window (1080x1920): Displays table image full screen with wheel overlay
- Secondary Window (1280x1024): Displays backglass image
- Uses left/right arrow keys for infinite scrolling between tables
- All images update with fade animation
- Press Enter to launch table, closing both windows until game exits
- Settings button to configure for your setup
- Use the screenshot_art.sh tool to get table media

Dependencies: python3, python3-pyqt5

Tarso Galvão - feb/2025
"""

# TODO:
# - add a default DMD for all tables, animated if possible like a gif
# - configure keys for ease to use on cabinet joystick

import sys, os, subprocess, configparser
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QWidget, QGraphicsOpacityEffect,
                             QDialog, QFormLayout, QLineEdit, QDialogButtonBox, QPushButton, QMessageBox)
from PyQt5.QtGui import QPixmap, QPalette, QColor, QGuiApplication, QFont, QFontMetrics
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve

# ---------------- Configuration ----------------
CONFIG_FILE        = "~/.asap-cabinet-fe/settings.ini"

VPX_ROOT_FOLDER    = "/home/tarso/Games/vpinball/build/tables/"
EXECUTABLE_CMD     = "/home/tarso/Games/vpinball/build/VPinballX_GL"
EXECUTABLE_SUB_CMD = "-Play"

# Images path:
DEFAULT_TABLE_PATH = "default_table.png"
DEFAULT_WHEEL_PATH = "default_wheel.png"
DEFAULT_BACKGLASS_PATH = "default_backglass.png"
DEFAULT_DMD_PATH   = "" # gif? (nyi)

TABLE_IMAGE_PATH   = "images/table.png"
TABLE_WHEEL_PATH   = "images/wheel.png"
TABLE_BACKGLASS_PATH = "images/backglass.png"
TABLE_DMD_PATH     = "images/dmd.png" # screenshot? (nyi)

# Window and image sizes
WINDOW_WIDTH       = 1080
WINDOW_HEIGHT      = 1920
BACKGLASS_WIDTH    = 1024
BACKGLASS_HEIGHT   = 1024
WHEEL_SIZE         = 400 # Square
WHEEL_MARGIN       = 20

# Table titles
FONT_NAME = "Arial"
FONT_SIZE = 32
BG_COLOR = "#202020"
TEXT_COLOR = "white"

# Monitor binding indices
MAIN_MONITOR_INDEX = 1        # Main window (vertical)
SECONDARY_MONITOR_INDEX = 0   # Secondary window (backglass)

# Animation settings
FADE_DURATION = 300  # milliseconds

# ---------------- Configuration Loader ----------------
def load_configuration():
    global VPX_ROOT_FOLDER, EXECUTABLE_CMD, EXECUTABLE_SUB_CMD
    global DEFAULT_TABLE_PATH, DEFAULT_WHEEL_PATH, DEFAULT_BACKGLASS_PATH
    global TABLE_IMAGE_PATH, TABLE_WHEEL_PATH, TABLE_BACKGLASS_PATH
    global WINDOW_WIDTH, WINDOW_HEIGHT, BACKGLASS_WIDTH, BACKGLASS_HEIGHT
    global WHEEL_SIZE, WHEEL_MARGIN, FONT_NAME, FONT_SIZE
    global BG_COLOR, TEXT_COLOR, MAIN_MONITOR_INDEX, SECONDARY_MONITOR_INDEX, FADE_DURATION

    ini_file = os.path.expanduser(CONFIG_FILE) 
    config = configparser.ConfigParser()

    # Ensure the directory exists
    directory = os.path.dirname(ini_file)
    if not os.path.exists(directory):
        os.makedirs(directory)

    if os.path.exists(ini_file):
        config.read(ini_file)
    else:
        config['Settings'] = {
            "VPX_ROOT_FOLDER": VPX_ROOT_FOLDER,
            "EXECUTABLE_CMD": EXECUTABLE_CMD,
            "EXECUTABLE_SUB_CMD": EXECUTABLE_SUB_CMD,
            "DEFAULT_TABLE_PATH": DEFAULT_TABLE_PATH,
            "DEFAULT_WHEEL_PATH": DEFAULT_WHEEL_PATH,
            "DEFAULT_BACKGLASS_PATH": DEFAULT_BACKGLASS_PATH,
            "TABLE_IMAGE_PATH": TABLE_IMAGE_PATH,
            "TABLE_WHEEL_PATH": TABLE_WHEEL_PATH,
            "TABLE_BACKGLASS_PATH": TABLE_BACKGLASS_PATH,
            "WINDOW_WIDTH": str(WINDOW_WIDTH),
            "WINDOW_HEIGHT": str(WINDOW_HEIGHT),
            "BACKGLASS_WIDTH": str(BACKGLASS_WIDTH),
            "BACKGLASS_HEIGHT": str(BACKGLASS_HEIGHT),
            "WHEEL_SIZE": str(WHEEL_SIZE),
            "WHEEL_MARGIN": str(WHEEL_MARGIN),
            "FONT_NAME": FONT_NAME,
            "FONT_SIZE": str(FONT_SIZE),
            "BG_COLOR": BG_COLOR,
            "TEXT_COLOR": TEXT_COLOR,
            "MAIN_MONITOR_INDEX": str(MAIN_MONITOR_INDEX),
            "SECONDARY_MONITOR_INDEX": str(SECONDARY_MONITOR_INDEX),
            "FADE_DURATION": str(FADE_DURATION)
        }
        with open(ini_file, "w") as f:
            config.write(f)
    s = config['Settings']
    VPX_ROOT_FOLDER = s.get("VPX_ROOT_FOLDER", VPX_ROOT_FOLDER)
    EXECUTABLE_CMD = s.get("EXECUTABLE_CMD", EXECUTABLE_CMD)
    EXECUTABLE_SUB_CMD = s.get("EXECUTABLE_SUB_CMD", EXECUTABLE_SUB_CMD)
    DEFAULT_TABLE_PATH = s.get("DEFAULT_TABLE_PATH", DEFAULT_TABLE_PATH)
    DEFAULT_WHEEL_PATH = s.get("DEFAULT_WHEEL_PATH", DEFAULT_WHEEL_PATH)
    DEFAULT_BACKGLASS_PATH = s.get("DEFAULT_BACKGLASS_PATH", DEFAULT_BACKGLASS_PATH)
    TABLE_IMAGE_PATH = s.get("TABLE_IMAGE_PATH", TABLE_IMAGE_PATH)
    TABLE_WHEEL_PATH = s.get("TABLE_WHEEL_PATH", TABLE_WHEEL_PATH)
    TABLE_BACKGLASS_PATH = s.get("TABLE_BACKGLASS_PATH", TABLE_BACKGLASS_PATH)
    WINDOW_WIDTH = int(s.get("WINDOW_WIDTH", WINDOW_WIDTH))
    WINDOW_HEIGHT = int(s.get("WINDOW_HEIGHT", WINDOW_HEIGHT))
    BACKGLASS_WIDTH = int(s.get("BACKGLASS_WIDTH", BACKGLASS_WIDTH))
    BACKGLASS_HEIGHT = int(s.get("BACKGLASS_HEIGHT", BACKGLASS_HEIGHT))
    WHEEL_SIZE = int(s.get("WHEEL_SIZE", WHEEL_SIZE))
    WHEEL_MARGIN = int(s.get("WHEEL_MARGIN", WHEEL_MARGIN))
    FONT_NAME = s.get("FONT_NAME", FONT_NAME)
    FONT_SIZE = int(s.get("FONT_SIZE", FONT_SIZE))
    BG_COLOR = s.get("BG_COLOR", BG_COLOR)
    TEXT_COLOR = s.get("TEXT_COLOR", TEXT_COLOR)
    MAIN_MONITOR_INDEX = int(s.get("MAIN_MONITOR_INDEX", MAIN_MONITOR_INDEX))
    SECONDARY_MONITOR_INDEX = int(s.get("SECONDARY_MONITOR_INDEX", SECONDARY_MONITOR_INDEX))
    FADE_DURATION = int(s.get("FADE_DURATION", FADE_DURATION))

# Load configuration on startup
load_configuration()
        
# ---------------- Settings Dialog ----------------
class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        
        # Set the fixed size of the settings dialog to 700x500
        self.setFixedSize(700, 710)
        
        # Create a form layout for the settings fields
        self.layout = QFormLayout(self)
        
        # Create QLineEdit fields for each setting
        self.vpxRootEdit = QLineEdit(VPX_ROOT_FOLDER)
        self.execCmdEdit = QLineEdit(EXECUTABLE_CMD)
        self.execSubCmdEdit = QLineEdit(EXECUTABLE_SUB_CMD)
        self.tableImageEdit = QLineEdit(TABLE_IMAGE_PATH)
        self.wheelImageEdit = QLineEdit(TABLE_WHEEL_PATH)
        self.backglassImageEdit = QLineEdit(TABLE_BACKGLASS_PATH)
        self.windowWidthEdit = QLineEdit(str(WINDOW_WIDTH))
        self.windowHeightEdit = QLineEdit(str(WINDOW_HEIGHT))
        self.backglassWidthEdit = QLineEdit(str(BACKGLASS_WIDTH))
        self.backglassHeightEdit = QLineEdit(str(BACKGLASS_HEIGHT))
        self.wheelSizeEdit = QLineEdit(str(WHEEL_SIZE))
        self.wheelMarginEdit = QLineEdit(str(WHEEL_MARGIN))
        self.fontNameEdit = QLineEdit(FONT_NAME)
        self.fontSizeEdit = QLineEdit(str(FONT_SIZE))
        self.bgColorEdit = QLineEdit(BG_COLOR)
        self.textColorEdit = QLineEdit(TEXT_COLOR)
        self.fadeDurationEdit = QLineEdit(str(FADE_DURATION))
        
        # Add each field to the layout with a descriptive label
        self.layout.addRow("VPX Root Folder:", self.vpxRootEdit)
        self.layout.addRow("Executable Command:", self.execCmdEdit)
        self.layout.addRow("Executable Sub Cmd:", self.execSubCmdEdit)
        self.layout.addRow("Table Image Path:", self.tableImageEdit)
        self.layout.addRow("Wheel Image Path:", self.wheelImageEdit)
        self.layout.addRow("Backglass Image Path:", self.backglassImageEdit)
        self.layout.addRow("Window Width:", self.windowWidthEdit)
        self.layout.addRow("Window Height:", self.windowHeightEdit)
        self.layout.addRow("Backglass Width:", self.backglassWidthEdit)
        self.layout.addRow("Backglass Height:", self.backglassHeightEdit)
        self.layout.addRow("Wheel Size:", self.wheelSizeEdit)
        self.layout.addRow("Wheel Margin:", self.wheelMarginEdit)
        self.layout.addRow("Font Name:", self.fontNameEdit)
        self.layout.addRow("Font Size:", self.fontSizeEdit)
        self.layout.addRow("Background Color:", self.bgColorEdit)
        self.layout.addRow("Text Color:", self.textColorEdit)
        self.layout.addRow("Fade Duration:", self.fadeDurationEdit)
        
        # Create a button box with Ok and Cancel buttons
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.layout.addRow(self.buttonBox)

        # --- Begin customization for icon-only, square buttons ---
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
        # --- End customization for icon-only, square buttons ---

    def getValues(self):
        """Retrieve the current settings values from the dialog."""
        return {
            "VPX_ROOT_FOLDER": self.vpxRootEdit.text(),
            "EXECUTABLE_CMD": self.execCmdEdit.text(),
            "EXECUTABLE_SUB_CMD": self.execSubCmdEdit.text(),
            "TABLE_IMAGE_PATH": self.tableImageEdit.text(),
            "TABLE_WHEEL_PATH": self.wheelImageEdit.text(),
            "TABLE_BACKGLASS_PATH": self.backglassImageEdit.text(),
            "WINDOW_WIDTH": self.windowWidthEdit.text(),
            "WINDOW_HEIGHT": self.windowHeightEdit.text(),
            "BACKGLASS_WIDTH": self.backglassWidthEdit.text(),
            "BACKGLASS_HEIGHT": self.backglassHeightEdit.text(),
            "WHEEL_SIZE": self.wheelSizeEdit.text(),
            "WHEEL_MARGIN": self.wheelMarginEdit.text(),
            "FONT_NAME": self.fontNameEdit.text(),
            "FONT_SIZE": self.fontSizeEdit.text(),
            "BG_COLOR": self.bgColorEdit.text(),
            "TEXT_COLOR": self.textColorEdit.text(),
            "FADE_DURATION": self.fadeDurationEdit.text()
        }

# ---------------- Table Data Loader ----------------
def load_table_list():
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
                # Construct the expected path for the table image
                table_img_path = os.path.join(root, TABLE_IMAGE_PATH)
                # If the table image doesn't exist at the expected path, use a default image path
                if not os.path.exists(table_img_path):
                    table_img_path = DEFAULT_TABLE_PATH
                # Construct the expected path for the wheel image
                wheel_img_path = os.path.join(root, TABLE_WHEEL_PATH)
                # If the wheel image doesn't exist at the expected path, use a default wheel image path
                if not os.path.exists(wheel_img_path):
                    wheel_img_path = DEFAULT_WHEEL_PATH
                # Construct the expected path for the backglass image
                backglass_img_path = os.path.join(root, TABLE_BACKGLASS_PATH)
                # If the backglass image doesn't exist at the expected path, use a default backglass image path
                if not os.path.exists(backglass_img_path):
                    backglass_img_path = DEFAULT_BACKGLASS_PATH
                # Append a dictionary containing all relevant table information to the tables list
                tables.append({
                    "table_name": table_name,
                    "vpx_file": vpx_path,
                    "folder": root,
                    "table_img": table_img_path,
                    "wheel_img": wheel_img_path,
                    "backglass_img": backglass_img_path
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
        self.setFixedSize(BACKGLASS_WIDTH, BACKGLASS_HEIGHT)
        self.setStyleSheet("background-color: black;")
        
        # Create a QLabel to display the image
        self.label = QLabel(self)
        # Set alignment to top-center so that the image touches the top of the frame
        self.label.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        self.setCentralWidget(self.label)

        # Add an opacity effect for fade animation
        self.backglass_effect = QGraphicsOpacityEffect(self.label)
        self.label.setGraphicsEffect(self.backglass_effect)
        self.backglass_effect.setOpacity(1.0)  # Initial opacity

    def update_image(self, image_path):
        # Use default image if the specified path does not exist
        if not os.path.exists(image_path):
            image_path = DEFAULT_BACKGLASS_PATH
        
        pixmap = QPixmap(image_path)
        if pixmap.isNull():
            # If the image is invalid, create a black pixmap
            pixmap = QPixmap(BACKGLASS_WIDTH, BACKGLASS_HEIGHT)
            pixmap.fill(Qt.black)
        else:
            # Scale the pixmap while preserving aspect ratio
            pixmap = pixmap.scaled(BACKGLASS_WIDTH, BACKGLASS_HEIGHT, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        
        # Set the scaled pixmap on the label
        self.label.setPixmap(pixmap)
        # Reset opacity after setting the image
        self.backglass_effect.setOpacity(1.0)

# ---------------- Main Window ----------------
class SingleTableViewer(QMainWindow):
    def __init__(self, secondary_window=None):
        super().__init__()
        self.setWindowTitle("Primary Display (Table Viewer)")
        self.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)
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
        # central.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setFocus()
        # Create the table label before using it
        self.table_label = QLabel(central)
        self.table_label.setGeometry(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
        self.table_label.setScaledContents(True)
        self.table_label.setStyleSheet("border: none;")
        self.table_effect = QGraphicsOpacityEffect(self.table_label)
        self.table_label.setGraphicsEffect(self.table_effect)

        # Create the table name label after other elements are set up
        self.table_name_label = QLabel(central)
        self.table_name_label.setGeometry(10, WINDOW_HEIGHT - 30, WINDOW_WIDTH - 20, 30)
        self.table_name_label.setStyleSheet(f"color: {TEXT_COLOR}; font-size: {FONT_SIZE}px; text-align: left; background-color: {BG_COLOR};")
        self.table_name_label.setAlignment(Qt.AlignCenter)
        
        # Now that the table label and name label are created, set the font
        self._set_font_from_config()  # Set the font for the table name
        # Set initial table name after loading images
        self._set_initial_table_name()
        # Add a cogwheel settings button in the top-right corner
        self.settingsButton = QPushButton("⚙", central)
        self.settingsButton.setFixedSize(40, 40)
        self.settingsButton.move(WINDOW_WIDTH - 50, 10)
        self.settingsButton.setFocusPolicy(Qt.NoFocus)
        self.settingsButton.clicked.connect(self.openSettings)
        self.settingsButton.raise_()

        # Apply a stylesheet to remove the border and make the background transparent
        self.settingsButton.setStyleSheet("""
            QPushButton {
                font-size: 28px;         /* Increase the font size of the icon */
                border: none;           /* Remove the button border */
                background: transparent; /* Make the background transparent */
            }
        """)

        wheel_x = WINDOW_WIDTH - WHEEL_SIZE - WHEEL_MARGIN
        wheel_y = WINDOW_HEIGHT - WHEEL_SIZE - WHEEL_MARGIN
        self.wheel_label = QLabel(central)
        self.wheel_label.setGeometry(wheel_x, wheel_y, WHEEL_SIZE, WHEEL_SIZE)
        self.wheel_label.setScaledContents(True)
        self.wheel_label.setAttribute(Qt.WA_TranslucentBackground)
        self.wheel_label.setStyleSheet("background-color: transparent;")
        self.wheel_effect = QGraphicsOpacityEffect(self.wheel_label)
        self.wheel_label.setGraphicsEffect(self.wheel_effect)

        # Initial display without animation
        self._update_images_no_animation()

    def _set_font_from_config(self):
        """Set the font for the table name label from config variables."""
        font = QFont(FONT_NAME, FONT_SIZE)
        # font.setBold(True)        # Make the font bold
        # font.setItalic(True)      # Make the font italic
        # font.setUnderline(True)   # Underline the text
        self.table_name_label.setFont(font)

    def _set_initial_table_name(self):
        """Set the table name initially."""
        table = self.table_list[self.current_index]
        table_name = os.path.splitext(os.path.basename(table["vpx_file"]))[0]  # Get file name without extension
        self.table_name_label.setText(table_name)
        
        # Ensure the label's size is adjusted to the text
        self.table_name_label.adjustSize()

        # Get the height of the text based on the current font size
        font_metrics = QFontMetrics(self.table_name_label.font())

        # Update label geometry to match the height of the text
        # Here, we calculate the Y position dynamically based on the table index
        label_height = font_metrics.height()  # Get the height of the text
        y_position = WINDOW_HEIGHT - label_height - (self.current_index * (label_height))  # Adjust based on index

        # Make sure the table name label is positioned correctly for all tables
        self.table_name_label.setGeometry(10, y_position, WINDOW_WIDTH - 20, label_height)

        # Set the style
        self.table_name_label.setStyleSheet(f"color: {TEXT_COLOR}; text-align: left; background-color: {BG_COLOR};")
        self._update_table_name_label_geometry()

    def _update_images_no_animation(self):
        """Update images without animation (used for initial load)."""
        table = self.table_list[self.current_index]

        table_pixmap = QPixmap(table["table_img"])
        if table_pixmap.isNull():
            table_pixmap = QPixmap(WINDOW_WIDTH, WINDOW_HEIGHT)
            table_pixmap.fill(Qt.black)
        table_scaled = table_pixmap.scaled(WINDOW_WIDTH, WINDOW_HEIGHT,
                                         Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        self.table_label.setPixmap(table_scaled)
        self.table_effect.setOpacity(1.0)

        self.table_name_label.setText(table["table_name"]) # Update the table name

        wheel_pixmap = QPixmap(table["wheel_img"])
        if wheel_pixmap.isNull():
            wheel_pixmap = QPixmap(WHEEL_SIZE, WHEEL_SIZE)
            wheel_pixmap.fill(Qt.transparent)
        wheel_scaled = wheel_pixmap.scaled(WHEEL_SIZE, WHEEL_SIZE,
                                         Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.wheel_label.setPixmap(wheel_scaled)
        self.wheel_effect.setOpacity(1.0)

        if self.secondary:
            self.secondary.update_image(table["backglass_img"])

    def _update_table_name_label_geometry(self):
        """Update the geometry of the table name label to fit its text and keep it on screen."""
        font_metrics = QFontMetrics(self.table_name_label.font())
        text = self.table_name_label.text()
        # For Qt5 use width(), for Qt6 horizontalAdvance is preferred.
        try:
            text_width = font_metrics.horizontalAdvance(text)
        except AttributeError:
            text_width = font_metrics.width(text)
        label_height = font_metrics.height()
        padding = 10  # add 10 pixels of padding on all sides
        label_width = text_width + 2 * padding
        label_height = label_height + 2 * padding
        x_position = 10  # fixed left margin
        y_position = WINDOW_HEIGHT - label_height - 20  # fixed 20-pixel margin from the bottom
        self.table_name_label.setGeometry(x_position, y_position, label_width, label_height)

    def update_images(self):
        """Update images with fade animation across all displays."""
        table = self.table_list[self.current_index]

        # Prepare new pixmaps for table and wheel images
        table_pixmap = QPixmap(table["table_img"])
        if table_pixmap.isNull():
            table_pixmap = QPixmap(WINDOW_WIDTH, WINDOW_HEIGHT)
            table_pixmap.fill(Qt.black)
        table_scaled = table_pixmap.scaled(WINDOW_WIDTH, WINDOW_HEIGHT,
                                        Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)

        wheel_pixmap = QPixmap(table["wheel_img"])
        if wheel_pixmap.isNull():
            wheel_pixmap = QPixmap(WHEEL_SIZE, WHEEL_SIZE)
            wheel_pixmap.fill(Qt.transparent)
        wheel_scaled = wheel_pixmap.scaled(WHEEL_SIZE, WHEEL_SIZE,
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
        self.fade_out_table.setEndValue(0.5)
        self.fade_out_table.setEasingCurve(QEasingCurve.InQuad)

        self.fade_out_wheel = QPropertyAnimation(self.wheel_effect, b"opacity")
        self.fade_out_wheel.setDuration(FADE_DURATION // 2)
        self.fade_out_wheel.setStartValue(1.0)
        self.fade_out_wheel.setEndValue(0.5)
        self.fade_out_wheel.setEasingCurve(QEasingCurve.InQuad)

        self.fade_out_backglass = QPropertyAnimation(self.secondary.backglass_effect, b"opacity") if self.secondary else None
        if self.fade_out_backglass:
            self.fade_out_backglass.setDuration(FADE_DURATION // 2)
            self.fade_out_backglass.setStartValue(1.0)
            self.fade_out_backglass.setEndValue(0.5)
            self.fade_out_backglass.setEasingCurve(QEasingCurve.InQuad)

        self.fade_out_table.finished.connect(lambda: self._set_new_images(table_scaled, wheel_scaled, table["backglass_img"]))
        self.fade_out_table.start()
        self.fade_out_wheel.start()
        if self.fade_out_backglass:
            self.fade_out_backglass.start()


    def _set_new_images(self, table_pixmap, wheel_pixmap, backglass_path):
        """Set new images and fade in all displays."""
        self.table_label.setPixmap(table_pixmap)
        self.wheel_label.setPixmap(wheel_pixmap)
        if self.secondary:
            self.secondary.update_image(backglass_path)

        # Fade in all elements
        self.fade_in_table = QPropertyAnimation(self.table_effect, b"opacity")
        self.fade_in_table.setDuration(FADE_DURATION // 2)
        self.fade_in_table.setStartValue(0.5)
        self.fade_in_table.setEndValue(1.0)
        self.fade_in_table.setEasingCurve(QEasingCurve.OutQuad)
        self.fade_in_table.start()

        self.fade_in_wheel = QPropertyAnimation(self.wheel_effect, b"opacity")
        self.fade_in_wheel.setDuration(FADE_DURATION // 2)
        self.fade_in_wheel.setStartValue(0.5)
        self.fade_in_wheel.setEndValue(1.0)
        self.fade_in_wheel.setEasingCurve(QEasingCurve.OutQuad)
        self.fade_in_wheel.start()

        if self.secondary:
            self.fade_in_backglass = QPropertyAnimation(self.secondary.backglass_effect, b"opacity")
            self.fade_in_backglass.setDuration(FADE_DURATION // 2)
            self.fade_in_backglass.setStartValue(0.5)
            self.fade_in_backglass.setEndValue(1.0)
            self.fade_in_backglass.setEasingCurve(QEasingCurve.OutQuad)
            self.fade_in_backglass.start()

    def launch_table(self):
        """Launch the table and close both windows, reopening after game exits."""
        table = self.table_list[self.current_index]
        command = [EXECUTABLE_CMD, EXECUTABLE_SUB_CMD, table["vpx_file"]]
        try:
            # Hide both windows
            # self.hide()
            # if self.secondary:
            #     self.secondary.hide()

            # Launch the game and wait for it to finish
            process = subprocess.Popen(command)
            process.wait()

            # Show windows again after game exits
            self.show()
            self.raise_()          # Bring the main window to the front
            self.activateWindow()  # Activate the window to accept input
            self.setFocus()        # Set focus on the main window
            if self.secondary:
                self.secondary.show()
                self.secondary.update_image(table["backglass_img"])
            self._update_images_no_animation()  # Ensure images are in sync

        except Exception as e:
            print(f"Error launching {table['vpx_file']}: {e}")
            # If there's an error, show windows again
            self.show()
            if self.secondary:
                self.secondary.show()

    def openSettings(self):
        dialog = SettingsDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            values = dialog.getValues()
            config = configparser.ConfigParser()
            config['Settings'] = values

            # Create the ini_file path
            ini_file = os.path.expanduser(CONFIG_FILE)

            # Ensure the directory exists
            directory = os.path.dirname(ini_file)
            if not os.path.exists(directory):
                os.makedirs(directory)
            try:
                with open(ini_file, "w") as f:
                    config.write(f)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save settings: {e}")
                return # exit the function if error.
            
            load_configuration()
            self._set_font_from_config()
            self._set_initial_table_name()
            self.table_list = load_table_list()
            self._update_images_no_animation()
        self.setFocus()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Left:
            self.current_index = (self.current_index - 1) % len(self.table_list)
            self.update_images()  # Update images when switching tables
        elif event.key() == Qt.Key_Right:
            self.current_index = (self.current_index + 1) % len(self.table_list)
            self.update_images()  # Update images when switching tables
        elif event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.launch_table()  # Launch the table
        elif event.key() == Qt.Key_Escape:
            self.close()  # Close the window
        else:
            super().keyPressEvent(event)  # Handle other key events

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
        viewer.setGeometry(main_geom.x(), main_geom.y(), WINDOW_WIDTH, WINDOW_HEIGHT)

    if len(screens) > SECONDARY_MONITOR_INDEX:
        secondary_screen = screens[SECONDARY_MONITOR_INDEX]
        sec_geom = secondary_screen.geometry()
        secondary_window.windowHandle().setScreen(secondary_screen)
        secondary_window.move(sec_geom.topLeft())
        secondary_window.setGeometry(sec_geom.x(), sec_geom.y(), BACKGLASS_WIDTH, BACKGLASS_HEIGHT)

    sys.exit(app.exec_())
