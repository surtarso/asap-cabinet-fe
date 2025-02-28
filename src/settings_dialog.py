import os
from PyQt5.QtWidgets import QDialog, QFormLayout, QLineEdit, QDialogButtonBox, QLabel
from .config import (CONFIG_FILE, VPX_ROOT_FOLDER, EXECUTABLE_CMD, EXECUTABLE_SUB_CMD,
                    TABLE_IMAGE_PATH, TABLE_WHEEL_PATH, TABLE_BACKGLASS_PATH, TABLE_DMD_PATH,
                    MAIN_MONITOR_INDEX, MAIN_WINDOW_WIDTH, MAIN_WINDOW_HEIGHT,
                    SECONDARY_MONITOR_INDEX, BACKGLASS_WINDOW_WIDTH, BACKGLASS_WINDOW_HEIGHT,
                    WHEEL_IMAGE_SIZE, WHEEL_IMAGE_MARGIN, FONT_NAME, FONT_SIZE,
                    BG_COLOR, TEXT_COLOR, FADE_DURATION, SETTINGS_WIDTH, SETTINGS_HEIGHT)

'''
This module contains the settings dialog where users can update paths,
dimensions, and style options.
'''

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(SETTINGS_WIDTH, SETTINGS_HEIGHT)
        self.layout = QFormLayout(self)
        ini_path = CONFIG_FILE.replace(os.path.expanduser("~"), "~")
        self.setWindowTitle(f"[Settings] {ini_path}")

        # Create input fields for each setting
        self.vpxRootEdit         = QLineEdit(VPX_ROOT_FOLDER)
        self.execCmdEdit         = QLineEdit(EXECUTABLE_CMD)
        self.execSubCmdEdit      = QLineEdit(EXECUTABLE_SUB_CMD)
        self.tableImageEdit      = QLineEdit(TABLE_IMAGE_PATH)
        self.wheelImageEdit      = QLineEdit(TABLE_WHEEL_PATH)
        self.backglassImageEdit  = QLineEdit(TABLE_BACKGLASS_PATH)
        self.dmdTableEdit        = QLineEdit(TABLE_DMD_PATH)
        self.mainMonitor         = QLineEdit(str(MAIN_MONITOR_INDEX))
        self.windowWidthEdit     = QLineEdit(str(MAIN_WINDOW_WIDTH))
        self.windowHeightEdit    = QLineEdit(str(MAIN_WINDOW_HEIGHT))
        self.secondaryMonitor    = QLineEdit(str(SECONDARY_MONITOR_INDEX))
        self.backglassWidthEdit  = QLineEdit(str(BACKGLASS_WINDOW_WIDTH))
        self.backglassHeightEdit = QLineEdit(str(BACKGLASS_WINDOW_HEIGHT))
        self.wheelSizeEdit       = QLineEdit(str(WHEEL_IMAGE_SIZE))
        self.wheelMarginEdit     = QLineEdit(str(WHEEL_IMAGE_MARGIN))
        self.fontNameEdit        = QLineEdit(FONT_NAME)
        self.fontSizeEdit        = QLineEdit(str(FONT_SIZE))
        self.bgColorEdit         = QLineEdit(BG_COLOR)
        self.textColorEdit       = QLineEdit(TEXT_COLOR)
        self.fadeDurationEdit    = QLineEdit(str(FADE_DURATION))
        
        # Add sections and rows to the form layout
        self.add_section_title("Main Paths (Use absolute paths)")
        self.layout.addRow("Tables Folder:",        self.vpxRootEdit)
        self.layout.addRow("VPX Executable:",       self.execCmdEdit)
        self.layout.addRow("VPX Argument:",         self.execSubCmdEdit)
        self.add_section_title("Custom Media Paths (/tables/<table_name/)")
        self.layout.addRow("Playfield Images Path:", self.tableImageEdit)
        self.layout.addRow("Wheel Images Path:",     self.wheelImageEdit)
        self.layout.addRow("Backglass Images Path:", self.backglassImageEdit)
        self.layout.addRow("DMD GIFs Path:",         self.dmdTableEdit)
        self.add_section_title("Screens Dimensions")
        self.layout.addRow("Playfield Monitor:",     self.mainMonitor)
        self.layout.addRow("Playfield Width:",       self.windowWidthEdit)
        self.layout.addRow("Playfield Height:",      self.windowHeightEdit)
        self.layout.addRow("Backglass Monitor:",     self.secondaryMonitor)
        self.layout.addRow("Backglass Width:",       self.backglassWidthEdit)
        self.layout.addRow("Backglass Height:",      self.backglassHeightEdit)
        self.add_section_title("Table Title Style")
        self.layout.addRow("Wheel Size:",            self.wheelSizeEdit)
        self.layout.addRow("Wheel Margin:",          self.wheelMarginEdit)
        self.layout.addRow("Font Name:",             self.fontNameEdit)
        self.layout.addRow("Font Size:",             self.fontSizeEdit)
        self.layout.addRow("Background Color:",      self.bgColorEdit)
        self.layout.addRow("Text Color:",            self.textColorEdit)
        self.layout.addRow("Transition Duration:",   self.fadeDurationEdit)
        
        # Add OK/Cancel button box with icon-only buttons
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
        ok_button.setIconSize(ok_button.size())
        cancel_button.setIconSize(cancel_button.size())

    def getValues(self):
        """Return a dictionary of current settings from the dialog."""
        return {
            "VPX_ROOT_FOLDER":         self.vpxRootEdit.text(),
            "EXECUTABLE_CMD":          self.execCmdEdit.text(),
            "EXECUTABLE_SUB_CMD":      self.execSubCmdEdit.text(),
            "TABLE_IMAGE_PATH":        self.tableImageEdit.text(),
            "TABLE_WHEEL_PATH":        self.wheelImageEdit.text(),
            "TABLE_BACKGLASS_PATH":    self.backglassImageEdit.text(),
            "TABLE_DMD_PATH":          self.dmdTableEdit.text(),
            "MAIN_MONITOR_INDEX":      self.mainMonitor.text(),
            "MAIN_WINDOW_WIDTH":       self.windowWidthEdit.text(),
            "MAIN_WINDOW_HEIGHT":      self.windowHeightEdit.text(),
            "SECONDARY_MONITOR_INDEX": self.secondaryMonitor.text(),
            "BACKGLASS_WINDOW_WIDTH":  self.backglassWidthEdit.text(),
            "BACKGLASS_WINDOW_HEIGHT": self.backglassHeightEdit.text(),
            "WHEEL_IMAGE_SIZE":        self.wheelSizeEdit.text(),
            "WHEEL_IMAGE_MARGIN":      self.wheelMarginEdit.text(),
            "FONT_NAME":               self.fontNameEdit.text(),
            "FONT_SIZE":               self.fontSizeEdit.text(),
            "BG_COLOR":                self.bgColorEdit.text(),
            "TEXT_COLOR":              self.textColorEdit.text(),
            "FADE_DURATION":           self.fadeDurationEdit.text()
        }
    
    def add_section_title(self, title):
        """Adds a bold section title to the dialog."""
        title_label = QLabel(title)
        title_label.setStyleSheet("font-weight: bold; font-size: 14px; padding: 5px;")
        self.layout.addWidget(title_label)
