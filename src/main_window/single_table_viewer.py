import os
from PyQt5.QtCore import Qt, QEasingCurve, QParallelAnimationGroup
from PyQt5.QtGui import QPixmap, QFont, QFontMetrics
from PyQt5.QtWidgets import QMainWindow
import src.config as config
# Relative imports since this file is inside the main_window package
from ..table_loader import load_table_list
from ..game_launcher import launch_table
from .ui_components import (
    setup_palette,
    setup_central_widget,
    create_table_label,
    create_table_name_label,
    create_settings_button,
    create_wheel_label,
    create_arrow_label
)
from .animations import create_fade_animation, create_loop_fade_animation
from src.settings_editor import IniEditorDialog

class SingleTableViewer(QMainWindow):
    """
    Main window (Table Viewer) that lets you navigate tables, 
    display images with fade transitions, and launch games.
    """
    def __init__(self, secondary_window=None):
        super().__init__()
        self.setWindowTitle("Primary Display (Table Viewer)")
        self.setFixedSize(config.MAIN_WINDOW_WIDTH, config.MAIN_WINDOW_HEIGHT)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.secondary = secondary_window

        # Set background color
        self.setPalette(setup_palette(config.BG_COLOR))

        # Load the table list; exit if no tables found.
        self.table_list = load_table_list()
        if not self.table_list:
            raise Exception("No .vpx files found in the specified folder.")
        self.current_index = 0

        # Setup the central widget
        central = setup_central_widget(self, config.BG_COLOR)
        self.setCentralWidget(central)
        self.setFocus()

        # Setup table image label and associated opacity effect
        self.table_label, self.table_effect = create_table_label(central, config.MAIN_WINDOW_WIDTH, config.MAIN_WINDOW_HEIGHT)

        # Setup table name label
        initial_table_name = os.path.splitext(os.path.basename(self.table_list[self.current_index]["vpx_file"]))[0]
        self.table_name_label = create_table_name_label(
            central, 10, config.MAIN_WINDOW_HEIGHT - 30,
            config.MAIN_WINDOW_WIDTH - 20, 30,
            initial_table_name, config.BG_COLOR, config.TEXT_COLOR, config.FONT_NAME, config.FONT_SIZE
        )
        self._set_table_name()

        # Setup settings button in the top-right corner
        self.settingsButton = create_settings_button(central, config.MAIN_WINDOW_WIDTH - 50, 10)
        self.settingsButton.clicked.connect(self.openSettings)

        # Setup wheel image label
        wheel_x = config.MAIN_WINDOW_WIDTH - config.WHEEL_IMAGE_SIZE - config.WHEEL_IMAGE_MARGIN
        wheel_y = config.MAIN_WINDOW_HEIGHT - config.WHEEL_IMAGE_SIZE - config.WHEEL_IMAGE_MARGIN
        self.wheel_label, self.wheel_effect = create_wheel_label(central, wheel_x, wheel_y, config.WHEEL_IMAGE_SIZE)

        # Setup blinking arrow hints for navigation
        arrow_width = 50
        arrow_height = 50
        current_y = (config.MAIN_WINDOW_HEIGHT - arrow_height) // 2
        bottom_y = config.MAIN_WINDOW_HEIGHT - arrow_height
        new_y = (current_y + bottom_y) // 2

        self.leftArrow, self.leftArrowEffect = create_arrow_label(central, "←", 10, new_y,
                                                                    arrow_width, arrow_height, 28, config.BG_COLOR)
        self.rightArrow, self.rightArrowEffect = create_arrow_label(
            central, "→", config.MAIN_WINDOW_WIDTH - arrow_width - 10, new_y,
            arrow_width, arrow_height, 28, config.BG_COLOR
        )
        # Start looping fade animations for the arrow hints
        self.leftArrowAnimation = create_loop_fade_animation(self.leftArrowEffect, 1250)
        self.rightArrowAnimation = create_loop_fade_animation(self.rightArrowEffect, 1250)

        # Load the initial images
        config.load_configuration()
        self.update_images()

    def _set_table_name(self):
        """
        Update the table name label based on the current table.
        """
        table = self.table_list[self.current_index]
        table_name = os.path.splitext(os.path.basename(table["vpx_file"]))[0]
        self.table_name_label.setText(table_name)
        self.table_name_label.setFont(QFont(config.FONT_NAME, config.FONT_SIZE))
        self.table_name_label.adjustSize()
        font_metrics = QFontMetrics(self.table_name_label.font())
        label_height = font_metrics.height()
        y_position = config.MAIN_WINDOW_HEIGHT - label_height - (self.current_index * label_height)
        self.table_name_label.setGeometry(10, y_position, config.MAIN_WINDOW_WIDTH - 20, label_height)
        self.table_name_label.setStyleSheet(f"color: {config.TEXT_COLOR}; text-align: left; background-color: {config.BG_COLOR};")
        self._update_table_name_label_geometry()

    def _update_table_name_label_geometry(self):
        """
        Adjust the geometry of the table name label based on its content.
        """
        font_metrics = QFontMetrics(self.table_name_label.font())
        text = self.table_name_label.text()
        try:
            text_width = font_metrics.horizontalAdvance(text)
        except AttributeError:
            text_width = font_metrics.width(text)
        label_height = font_metrics.height() + 20  # Adding padding
        label_width = text_width + 20              # Adding padding
        self.table_name_label.setGeometry(10, config.MAIN_WINDOW_HEIGHT - label_height - 20, label_width, label_height)


    def update_images(self):
        """
        Update images for the table, wheel, and (if available) secondary window.
        Fades out the current images, then loads new ones.
        """
        table = self.table_list[self.current_index]
        table_pixmap = QPixmap(table["table_img"])
        if table_pixmap.isNull():
            table_pixmap = QPixmap(config.MAIN_WINDOW_WIDTH, config.MAIN_WINDOW_HEIGHT)
            table_pixmap.fill(Qt.black)
        table_scaled = table_pixmap.scaled(config.MAIN_WINDOW_WIDTH, config.MAIN_WINDOW_HEIGHT,
                                            Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)

        wheel_pixmap = QPixmap(table["wheel_img"])
        if wheel_pixmap.isNull():
            wheel_pixmap = QPixmap(config.WHEEL_IMAGE_SIZE, config.WHEEL_IMAGE_SIZE)
            wheel_pixmap.fill(Qt.transparent)
        wheel_scaled = wheel_pixmap.scaled(config.WHEEL_IMAGE_SIZE, config.WHEEL_IMAGE_SIZE,
                                            Qt.KeepAspectRatio, Qt.SmoothTransformation)

        # Update table name label
        table_name = os.path.splitext(os.path.basename(table["vpx_file"]))[0]
        self.table_name_label.setText(table_name)
        self.table_name_label.adjustSize()
        self.table_name_label.setStyleSheet(f"color: {config.TEXT_COLOR}; text-align: left; background-color: {config.BG_COLOR};")
        self._update_table_name_label_geometry()

        # Create fade-out animations for table and wheel images
        self.fade_out_table = create_fade_animation(self.table_effect, config.FADE_DURATION // 2,
                                                    1.0, config.FADE_OPACITY, QEasingCurve.InQuad)
        self.fade_out_wheel = create_fade_animation(self.wheel_effect, config.FADE_DURATION // 2,
                                                    1.0, config.FADE_OPACITY, QEasingCurve.InQuad)
        if self.secondary:
            self.fade_out_backglass = create_fade_animation(self.secondary.backglass_effect, config.FADE_DURATION // 2,
                                                            1.0, config.FADE_OPACITY, QEasingCurve.InQuad)
        else:
            self.fade_out_backglass = None

        # Group fade-out animations to synchronize them
        fade_out_group = QParallelAnimationGroup()
        fade_out_group.addAnimation(self.fade_out_table)
        fade_out_group.addAnimation(self.fade_out_wheel)
        if self.fade_out_backglass:
            fade_out_group.addAnimation(self.fade_out_backglass)

        def on_fade_out_finished():
            self._set_new_images(table_scaled, wheel_scaled, table["backglass_img"], table["folder"])
            # Optionally clear the reference after finishing
            self._fade_out_group = None

        fade_out_group.finished.connect(on_fade_out_finished)
        # Store the group as an instance variable to prevent garbage collection
        self._fade_out_group = fade_out_group
        self._fade_out_group.start()

    def _set_new_images(self, table_pixmap, wheel_pixmap, backglass_path, table_folder):
        # Set the new images first.
        self.table_label.setPixmap(table_pixmap)
        self.wheel_label.setPixmap(wheel_pixmap)
        if self.secondary:
            self.secondary.update_image(backglass_path, table_folder)

        # Create fade-in animations for table and wheel images.
        self.fade_in_table = create_fade_animation(self.table_effect, config.FADE_DURATION // 2,
                                                    config.FADE_OPACITY, 1.0, QEasingCurve.OutQuad)
        self.fade_in_wheel = create_fade_animation(self.wheel_effect, config.FADE_DURATION // 2,
                                                    config.FADE_OPACITY, 1.0, QEasingCurve.OutQuad)
        # Optionally create fade-in animation for secondary window.
        if self.secondary:
            self.fade_in_backglass = create_fade_animation(self.secondary.backglass_effect, config.FADE_DURATION // 2,
                                                            config.FADE_OPACITY, 1.0, QEasingCurve.OutQuad)
        else:
            self.fade_in_backglass = None

        # Group fade-in animations.
        fade_in_group = QParallelAnimationGroup()
        fade_in_group.addAnimation(self.fade_in_table)
        fade_in_group.addAnimation(self.fade_in_wheel)
        if self.fade_in_backglass:
            fade_in_group.addAnimation(self.fade_in_backglass)
        # Store the group to prevent garbage collection.
        self._fade_in_group = fade_in_group
        self._fade_in_group.start()


    def launch_table(self):
        """
        Launch the game corresponding to the current table.
        """
        table = self.table_list[self.current_index]
        launch_table(table)

    def openSettings(self):
        """Opens the integrated settings editor dialog."""
        ini_file_path = os.path.expanduser(config.CONFIG_FILE)
        editor_dialog = IniEditorDialog(ini_file_path, self)
        if editor_dialog.exec_():
            # Optionally refresh settings if needed after dialog is accepted
            self.update_images()
        self.setFocus()

    def keyPressEvent(self, event):
        """
        Handle key press events for navigation and launching.
        """
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
        """
        Handle the close event, ensuring any secondary windows are also closed.
        """
        if self.secondary:
            self.secondary.close()
        event.accept()
