# ui_components.py
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor, QFont
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QGraphicsOpacityEffect

def setup_palette(bg_color):
    """
    Create and return a QPalette with the specified background color.
    """
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(bg_color))
    return palette

def setup_central_widget(parent, bg_color):
    """
    Create and return the central widget for the main window.
    """
    central = QWidget(parent)
    central.setFocusPolicy(Qt.StrongFocus)
    central.setStyleSheet(f"background-color: {bg_color};")
    central.setAttribute(Qt.WA_NoSystemBackground, True)
    return central

def create_table_label(parent, width, height):
    """
    Create the label used for displaying table images with an opacity effect.
    """
    label = QLabel(parent)
    label.setGeometry(0, 0, width, height)
    label.setScaledContents(True)
    label.setStyleSheet("border: none;")
    effect = QGraphicsOpacityEffect(label)
    label.setGraphicsEffect(effect)
    return label, effect

def create_table_name_label(parent, x, y, width, height, text, bg_color, text_color, font_name, font_size):
    """
    Create the label for displaying the table name.
    """
    label = QLabel(parent)
    label.setGeometry(x, y, width, height)
    label.setText(text)
    label.setStyleSheet(f"color: {text_color}; font-size: {font_size}px; text-align: left; background-color: {bg_color};")
    label.setAlignment(Qt.AlignCenter)
    label.setFont(QFont(font_name, font_size))
    return label

def create_settings_button(parent, x, y, size=40):
    """
    Create the settings button positioned in the top-right corner.
    """
    button = QPushButton("⚙", parent)
    button.setFixedSize(size, size)
    button.move(x, y)
    button.setFocusPolicy(Qt.NoFocus)
    button.setStyleSheet("""
        QPushButton {
            font-size: 28px;
            border: none;
            background: transparent;
        }
    """)
    button.raise_()
    return button

def create_wheel_label(parent, x, y, size):
    """
    Create the wheel image label with an opacity effect.
    """
    label = QLabel(parent)
    label.setGeometry(x, y, size, size)
    label.setScaledContents(True)
    label.setAttribute(Qt.WA_TranslucentBackground)
    label.setStyleSheet("background-color: transparent;")
    effect = QGraphicsOpacityEffect(label)
    label.setGraphicsEffect(effect)
    return label, effect

def create_arrow_label(parent, text, x, y, width, height, font_size, bg_color):
    """
    Create a generic arrow label (for left/right hints) with an opacity effect.
    """
    label = QLabel(text, parent)
    label.setAlignment(Qt.AlignCenter)
    font = label.font()
    font.setPointSize(font_size)
    label.setFont(font)
    label.setGeometry(x, y, width, height)
    # Apply styling: background color, rounded corners, and padding
    label.setStyleSheet(f"background-color: {bg_color}; border-radius: 20px; padding-bottom: 5px;")
    effect = QGraphicsOpacityEffect(label)
    label.setGraphicsEffect(effect)
    return label, effect
