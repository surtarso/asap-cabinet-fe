import os
import subprocess
import logging
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QPalette, QColor, QPixmap, QFont, QFontMetrics
from PyQt5.QtWidgets import QMainWindow, QLabel, QWidget, QPushButton, QGraphicsOpacityEffect
from .config import (MAIN_WINDOW_WIDTH, MAIN_WINDOW_HEIGHT, BG_COLOR, TEXT_COLOR, FONT_NAME, FONT_SIZE,
                    WHEEL_IMAGE_SIZE, WHEEL_IMAGE_MARGIN, FADE_OPACITY, FADE_DURATION, EXECUTABLE_CMD, EXECUTABLE_SUB_CMD)
from .table_loader import load_table_list
from .settings_dialog import SettingsDialog

'''
This module contains the primary window (table viewer) that lets you navigate tables,
display images with fade transitions, and launch games.
'''

class SingleTableViewer(QMainWindow):
    def __init__(self, secondary_window=None):
        super().__init__()
        self.setWindowTitle("Primary Display (Table Viewer)")
        self.setFixedSize(MAIN_WINDOW_WIDTH, MAIN_WINDOW_HEIGHT)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.secondary = secondary_window

        # Set backgrounf color
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(BG_COLOR))
        self.setPalette(palette)

        self.table_list = load_table_list()
        if not self.table_list:
            raise Exception("No .vpx files found in the specified folder.")
        self.current_index = 0

        # Set up the central widget
        central = QWidget(self)
        self.setCentralWidget(central)
        central.setFocusPolicy(Qt.StrongFocus)
        central.setStyleSheet(f"background-color: {BG_COLOR};")
        central.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setFocus()

        # Table image label and opacity effect
        self.table_label = QLabel(central)
        self.table_label.setGeometry(0, 0, MAIN_WINDOW_WIDTH, MAIN_WINDOW_HEIGHT)
        self.table_label.setScaledContents(True)
        self.table_label.setStyleSheet("border: none;")
        self.table_effect = QGraphicsOpacityEffect(self.table_label)
        self.table_label.setGraphicsEffect(self.table_effect)

        # Table name label
        self.table_name_label = QLabel(central)
        self.table_name_label.setGeometry(10, MAIN_WINDOW_HEIGHT - 30, MAIN_WINDOW_WIDTH - 20, 30)
        self.table_name_label.setStyleSheet(f"color: {TEXT_COLOR}; font-size: {FONT_SIZE}px; text-align: left; background-color: {BG_COLOR};")
        self.table_name_label.setAlignment(Qt.AlignCenter)
        self._set_table_name()

        # Settings button in top-right corner
        self.settingsButton = QPushButton("⚙", central)
        self.settingsButton.setFixedSize(40, 40)
        self.settingsButton.move(MAIN_WINDOW_WIDTH - 50, 10)
        self.settingsButton.setFocusPolicy(Qt.NoFocus)
        self.settingsButton.clicked.connect(self.openSettings)
        self.settingsButton.raise_()
        self.settingsButton.setStyleSheet("""
            QPushButton {
                font-size:  28px;
                border:     none;
                background: transparent;
            }
        """)

        # Wheel image label
        wheel_x = MAIN_WINDOW_WIDTH - WHEEL_IMAGE_SIZE - WHEEL_IMAGE_MARGIN
        wheel_y = MAIN_WINDOW_HEIGHT - WHEEL_IMAGE_SIZE - WHEEL_IMAGE_MARGIN
        self.wheel_label = QLabel(central)
        self.wheel_label.setGeometry(wheel_x, wheel_y, WHEEL_IMAGE_SIZE, WHEEL_IMAGE_SIZE)
        self.wheel_label.setScaledContents(True)
        self.wheel_label.setAttribute(Qt.WA_TranslucentBackground)
        self.wheel_label.setStyleSheet("background-color: transparent;")
        self.wheel_effect = QGraphicsOpacityEffect(self.wheel_label)
        self.wheel_label.setGraphicsEffect(self.wheel_effect)

        # --- Blinking arrow hints ---
        # Create left arrow label
        self.leftArrow = QLabel("←", central)
        self.leftArrow.setAlignment(Qt.AlignCenter)
        arrowFont = self.leftArrow.font()
        arrowFont.setPointSize(28)  # Adjust size as needed
        self.leftArrow.setFont(arrowFont)
        arrow_width = 50
        arrow_height = 50
        current_y = (MAIN_WINDOW_HEIGHT - arrow_height) // 2  # current center position
        bottom_y = MAIN_WINDOW_HEIGHT - arrow_height # lowest possible position (top of arrow at bottom)
        new_y = (current_y + bottom_y) // 2  # midpoint between current and bottom
        self.leftArrow.setGeometry(10, new_y, arrow_width, arrow_height)
        # self.leftArrow.setAttribute(Qt.WA_TranslucentBackground)
        self.leftArrow.setStyleSheet("background-color: {BG_COLOR};")

        # Create right arrow label
        self.rightArrow = QLabel("→", central)
        self.rightArrow.setAlignment(Qt.AlignCenter)
        self.rightArrow.setFont(arrowFont)
        self.rightArrow.setGeometry(MAIN_WINDOW_WIDTH - arrow_width - 10, new_y, arrow_width, arrow_height)
        # self.rightArrow.setAttribute(Qt.WA_TranslucentBackground)
        self.rightArrow.setStyleSheet("background-color: {BG_COLOR};")

        arrow_style = """
            QLabel {
                border-radius: 20px;  /* Adjust to control roundness */
                padding-bottom: 5px;  /* Ensures the arrow is not too close to the border */
            }
        """

        self.leftArrow.setStyleSheet(arrow_style)
        self.rightArrow.setStyleSheet(arrow_style)

        # Set up QGraphicsOpacityEffect for each arrow
        self.leftArrowEffect = QGraphicsOpacityEffect(self.leftArrow)
        self.leftArrow.setGraphicsEffect(self.leftArrowEffect)

        self.rightArrowEffect = QGraphicsOpacityEffect(self.rightArrow)
        self.rightArrow.setGraphicsEffect(self.rightArrowEffect)

        # Set up QPropertyAnimation for the left arrow
        self.leftArrowAnimation = QPropertyAnimation(self.leftArrowEffect, b"opacity")
        self.leftArrowAnimation.setDuration(1250)  # total duration in milliseconds
        self.leftArrowAnimation.setStartValue(0.0)
        self.leftArrowAnimation.setKeyValueAt(0.5, 1.0)  # Fully visible halfway through
        self.leftArrowAnimation.setEndValue(0.0)
        self.leftArrowAnimation.setLoopCount(-1)  # Loop indefinitely
        self.leftArrowAnimation.start()

        # Set up QPropertyAnimation for the right arrow
        self.rightArrowAnimation = QPropertyAnimation(self.rightArrowEffect, b"opacity")
        self.rightArrowAnimation.setDuration(1250)
        self.rightArrowAnimation.setStartValue(0.0)
        self.rightArrowAnimation.setKeyValueAt(0.5, 1.0)
        self.rightArrowAnimation.setEndValue(0.0)
        self.rightArrowAnimation.setLoopCount(-1)
        self.rightArrowAnimation.start()

        # Initial image load
        self.update_images()

    def _set_table_name(self):
        table = self.table_list[self.current_index]
        table_name = os.path.splitext(os.path.basename(table["vpx_file"]))[0]
        self.table_name_label.setText(table_name)
        self.table_name_label.setFont(QFont(FONT_NAME, FONT_SIZE))
        self.table_name_label.adjustSize()
        font_metrics = QFontMetrics(self.table_name_label.font())
        label_height = font_metrics.height()
        y_position = MAIN_WINDOW_HEIGHT - label_height - (self.current_index * label_height)
        self.table_name_label.setGeometry(10, y_position, MAIN_WINDOW_WIDTH - 20, label_height)
        self.table_name_label.setStyleSheet(f"color: {TEXT_COLOR}; text-align: left; background-color: {BG_COLOR};")
        self._update_table_name_label_geometry()

    def _update_table_name_label_geometry(self):
        font_metrics = QFontMetrics(self.table_name_label.font())
        text = self.table_name_label.text()
        try:
            text_width = font_metrics.horizontalAdvance(text)
        except AttributeError:
            text_width = font_metrics.width(text)
        label_height = font_metrics.height()
        padding = 10
        label_width = text_width + 2 * padding
        label_height = label_height + 2 * padding
        x_position = 10
        y_position = MAIN_WINDOW_HEIGHT - label_height - 20
        self.table_name_label.setGeometry(x_position, y_position, label_width, label_height)

    def update_images(self):
        table = self.table_list[self.current_index]
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

        table_name = os.path.splitext(os.path.basename(table["vpx_file"]))[0]
        self.table_name_label.setText(table_name)
        self.table_name_label.adjustSize()
        self.table_name_label.setStyleSheet(f"color: {TEXT_COLOR}; text-align: left; background-color: {BG_COLOR};")
        self._update_table_name_label_geometry()

        # Fade out current images
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
        else:
            self.fade_out_backglass = None

        def on_fade_out_finished():
            self._set_new_images(table_scaled, wheel_scaled, table["backglass_img"], table["folder"])
        self.fade_out_table.finished.connect(on_fade_out_finished)
        self.fade_out_table.start()
        self.fade_out_wheel.start()
        if self.fade_out_backglass:
            self.fade_out_backglass.start()

    def _set_new_images(self, table_pixmap, wheel_pixmap, backglass_path, table_folder):
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
        table = self.table_list[self.current_index]
        command = [EXECUTABLE_CMD, EXECUTABLE_SUB_CMD, table["vpx_file"]]
        try:
            # Define the log file path and ensure its directory exists
            log_path = os.path.expanduser("~/.asap-cabinet-fe/launcher.log")
            log_dir = os.path.dirname(log_path)
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            
            # Open the log file and redirect both stdout and stderr to it
            with open(log_path, "w") as log_file:
                process = subprocess.Popen(command, stdout=log_file, stderr=log_file)
                process.wait()

            # After the game exits, show the windows again and update images
            self.show()
            self.raise_()
            self.activateWindow()
            self.setFocus()
            if self.secondary:
                self.secondary.show()
                self.secondary.update_image(table["backglass_img"], table["folder"])
            self.update_images()

        except Exception as e:
            logging.error(f"Error launching {table['vpx_file']}: {e}")
            self.show()
            if self.secondary:
                self.secondary.show()

    def openSettings(self):
        from .config import CONFIG_FILE, load_configuration
        dialog = SettingsDialog(self)
        if dialog.exec_() == dialog.Accepted:
            values = dialog.getValues()
            import configparser
            config = configparser.ConfigParser()
            config['Settings'] = values
            ini_file = os.path.expanduser(CONFIG_FILE)
            directory = os.path.dirname(ini_file)
            if not os.path.exists(directory):
                os.makedirs(directory)
            try:
                with open(ini_file, "w") as f:
                    config.write(f)
            except Exception as e:
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.critical(self, "Error", f"Failed to save settings: {e}")
                return
            load_configuration()
            self._set_table_name()
            self.table_list = load_table_list()
            self.update_images()
        self.setFocus()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Left:
            self.current_index = (self.current_index - 1) % len(self.table_list)
            self.update_images()
        elif event.key() == Qt.Key_Right:
            self.current_index = (self.current_index + 1) % len(self.table_list)
            self.update_images()
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
