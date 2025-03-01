# asap_cabinet_fe/single_table_viewer.py
import os
import subprocess
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QPixmap, QPalette, QColor, QFont, QFontMetrics
from PyQt5.QtWidgets import QMainWindow, QLabel, QWidget, QGraphicsOpacityEffect, QPushButton, QMessageBox, QDialog
from src.config import *
from src.ui import SettingsDialog
from src.table_loader import load_table_list

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
        if not self.table_list:
            raise Exception("No .vpx files found in the specified folder.")
        self.current_index = 0

        central = QWidget(self)
        self.setCentralWidget(central)
        central.setFocusPolicy(Qt.StrongFocus)
        central.setStyleSheet(f"background-color: {BG_COLOR};")
        central.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setFocus()

        self.table_label = QLabel(central)
        self.table_label.setGeometry(0, 0, MAIN_WINDOW_WIDTH, MAIN_WINDOW_HEIGHT)
        self.table_label.setScaledContents(True)
        self.table_label.setStyleSheet("border: none;")
        self.table_effect = QGraphicsOpacityEffect(self.table_label)
        self.table_label.setGraphicsEffect(self.table_effect)

        self.table_name_label = QLabel(central)
        self.table_name_label.setStyleSheet(f"color: {TEXT_COLOR}; font-size: {FONT_SIZE}px; text-align: left; background-color: {BG_COLOR};")
        self.table_name_label.setAlignment(Qt.AlignCenter)
        self._set_table_name()

        self.settingsButton = QPushButton("⚙", central)
        self.settingsButton.setFixedSize(40, 40)
        self.settingsButton.move(MAIN_WINDOW_WIDTH - 50, 10)
        self.settingsButton.setFocusPolicy(Qt.NoFocus)
        self.settingsButton.clicked.connect(self.openSettings)
        self.settingsButton.setStyleSheet("font-size: 28px; border: none; background: transparent;")
        self.settingsButton.raise_()

        wheel_x = MAIN_WINDOW_WIDTH - WHEEL_IMAGE_SIZE - WHEEL_IMAGE_MARGIN
        wheel_y = MAIN_WINDOW_HEIGHT - WHEEL_IMAGE_SIZE - WHEEL_IMAGE_MARGIN
        self.wheel_label = QLabel(central)
        self.wheel_label.setGeometry(wheel_x, wheel_y, WHEEL_IMAGE_SIZE, WHEEL_IMAGE_SIZE)
        self.wheel_label.setScaledContents(True)
        self.wheel_label.setAttribute(Qt.WA_TranslucentBackground)
        self.wheel_label.setStyleSheet("background-color: transparent;")
        self.wheel_effect = QGraphicsOpacityEffect(self.wheel_label)
        self.wheel_label.setGraphicsEffect(self.wheel_effect)

        self.update_images()

    def _set_table_name(self):
        table = self.table_list[self.current_index]
        table_name = os.path.splitext(os.path.basename(table["vpx_file"]))[0]
        self.table_name_label.setText(table_name)
        self.table_name_label.setFont(QFont(FONT_NAME, FONT_SIZE))
        self.table_name_label.adjustSize()
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

        self.table_name_label.setText(os.path.splitext(os.path.basename(table["vpx_file"]))[0])
        self.table_name_label.adjustSize()
        self.table_name_label.setStyleSheet(f"color: {TEXT_COLOR}; text-align: left; background-color: {BG_COLOR};")
        self._update_table_name_label_geometry()

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
            process = subprocess.Popen(command)
            process.wait()
        except Exception as e:
            print(f"Error launching {table['vpx_file']}: {e}")

    def openSettings(self):
        dialog = SettingsDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            values = dialog.getValues()
            config = configparser.ConfigParser()
            config['Settings'] = values
            ini_file = os.path.expanduser(CONFIG_FILE)
            if not os.path.exists(os.path.dirname(ini_file)):
                os.makedirs(os.path.dirname(ini_file))
            try:
                with open(ini_file, "w") as f:
                    config.write(f)
            except Exception as e:
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