import os
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QMovie
from PyQt5.QtWidgets import QMainWindow, QLabel, QGraphicsOpacityEffect
import src.config as config

'''
This module defines the secondary window used for displaying
the backglass image and DMD GIF.
'''

class SecondaryWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Secondary Display (Backglass)")
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setFixedSize(config.BACKGLASS_WINDOW_WIDTH, config.BACKGLASS_WINDOW_HEIGHT)
        self.setStyleSheet("background-color: black;")

        # Backglass image label
        self.label = QLabel(self)
        self.label.setGeometry(0, 0, config.BACKGLASS_IMAGE_WIDTH, config.BACKGLASS_IMAGE_HEIGHT)
        self.label.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        self.backglass_effect = QGraphicsOpacityEffect(self.label)
        self.label.setGraphicsEffect(self.backglass_effect)
        self.backglass_effect.setOpacity(1.0)

        # DMD GIF label
        self.dmd_label = QLabel(self)
        self.dmd_label.setGeometry(0, config.BACKGLASS_IMAGE_HEIGHT, config.DMD_WIDTH, config.DMD_HEIGHT)
        self.dmd_label.setStyleSheet("background-color: black;")
        self.dmd_label.setAlignment(Qt.AlignCenter)

    def update_image(self, image_path, table_folder):
        """
        Updates the backglass image and the DMD GIF.
        If the table-specific DMD GIF does not exist, uses the default.
        """
        if not os.path.exists(image_path):
            image_path = config.DEFAULT_BACKGLASS_PATH

        pixmap = QPixmap(image_path)
        if pixmap.isNull():
            pixmap = QPixmap(config.BACKGLASS_IMAGE_WIDTH, config.BACKGLASS_IMAGE_HEIGHT)
            pixmap.fill(Qt.black)
        else:
            pixmap = pixmap.scaled(config.BACKGLASS_IMAGE_WIDTH, config.BACKGLASS_IMAGE_HEIGHT,
                                   Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.label.setPixmap(pixmap)
        self.backglass_effect.setOpacity(1.0)

        config.TABLE_DMD_PATH = os.path.join(table_folder, config.TABLE_DMD_PATH)
        dmd_path = config.TABLE_DMD_PATH if os.path.exists(config.TABLE_DMD_PATH) else config.DEFAULT_DMD_PATH

        if os.path.exists(dmd_path):
            self.dmd_movie = QMovie(dmd_path)
            self.dmd_movie.setCacheMode(QMovie.CacheAll)
            self.dmd_movie.start()  # Start to get frame size
            frame_size = self.dmd_movie.currentPixmap().size()
            self.dmd_movie.stop()

            config.DMD_WIDTH, config.DMD_HEIGHT = frame_size.width(), frame_size.height()
            if config.DMD_WIDTH > 0 and config.DMD_HEIGHT > 0:
                aspect_ratio = config.DMD_WIDTH / config.DMD_HEIGHT
                new_width = min(config.DMD_WIDTH, int(config.DMD_HEIGHT * aspect_ratio))
                new_height = min(config.DMD_HEIGHT, int(config.DMD_WIDTH / aspect_ratio))
                if new_width > config.DMD_WIDTH:
                    new_width = config.DMD_WIDTH
                    new_height = int(config.DMD_WIDTH / aspect_ratio)
                if new_height > config.DMD_HEIGHT:
                    new_height = config.DMD_HEIGHT
                    new_width = int(config.DMD_HEIGHT * aspect_ratio)
                self.dmd_movie.setScaledSize(QSize(new_width, new_height))
                x_offset = (config.DMD_WIDTH - new_width) // 2
                y_offset = (config.DMD_HEIGHT - new_height) // 2
                self.dmd_label.setGeometry(x_offset, config.BACKGLASS_IMAGE_HEIGHT + y_offset, new_width, new_height)
            self.dmd_label.setMovie(self.dmd_movie)
            self.dmd_movie.start()
