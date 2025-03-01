# asap_cabinet_fe/secondary_window.py
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QMovie
from PyQt5.QtWidgets import QMainWindow, QLabel, QGraphicsOpacityEffect
from src.config import *

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

        table_dmd_path = os.path.join(table_folder, TABLE_DMD_PATH)
        dmd_path = table_dmd_path if os.path.exists(table_dmd_path) else DEFAULT_DMD_PATH

        if os.path.exists(dmd_path):
            self.dmd_movie = QMovie(dmd_path)
            self.dmd_movie.setCacheMode(QMovie.CacheAll)
            self.dmd_movie.start()
            frame_size = self.dmd_movie.currentPixmap().size()
            self.dmd_movie.stop()

            dmd_width, dmd_height = frame_size.width(), frame_size.height()
            if dmd_width > 0 and dmd_height > 0:
                aspect_ratio = dmd_width / dmd_height
                new_width = min(DMD_WIDTH, int(DMD_HEIGHT * aspect_ratio))
                new_height = min(DMD_HEIGHT, int(DMD_WIDTH / aspect_ratio))

                if new_width > DMD_WIDTH:
                    new_width = DMD_WIDTH
                    new_height = int(DMD_WIDTH / aspect_ratio)
                if new_height > DMD_HEIGHT:
                    new_height = DMD_HEIGHT
                    new_width = int(DMD_HEIGHT * aspect_ratio)

                self.dmd_movie.setScaledSize(QSize(new_width, new_height))
                x_offset = (DMD_WIDTH - new_width) // 2
                y_offset = (DMD_HEIGHT - new_height) // 2
                self.dmd_label.setGeometry(x_offset, BACKGLASS_IMAGE_HEIGHT + y_offset, new_width, new_height)

            self.dmd_label.setMovie(self.dmd_movie)
            self.dmd_movie.start()