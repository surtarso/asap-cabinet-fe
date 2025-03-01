import importlib
import src.config as config
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QScrollArea, QWidget, QLineEdit, QPushButton, QFormLayout,
    QMessageBox
)

def read_ini_preserve_keys(filename):
    """
    Reads an INI file and returns a dictionary mapping section names to an ordered
    dictionary of key/value pairs. This parser preserves key capitalization.
    Comments and blank lines are ignored.
    """
    data = {}
    current_section = None
    with open(filename, 'r') as f:
        for line in f:
            stripped = line.strip()
            # Skip comments and blank lines
            if not stripped or stripped.startswith(';'):
                continue
            # Create new section if line is a section header
            if stripped.startswith('[') and stripped.endswith(']'):
                current_section = stripped[1:-1]
                data[current_section] = {}
            elif '=' in line and current_section is not None:
                key, value = line.split('=', 1)
                key = key.strip()   # Preserve original case
                value = value.strip()
                data[current_section][key] = value
    return data

def write_ini_preserve_keys(filename, data):
    """
    Writes the INI data (a dict mapping sections to key/value pairs)
    back to a file while preserving comments and blank lines.
    """
    with open(filename, 'r') as f:
        lines = f.readlines()

    with open(filename, 'w') as f:
        current_section = None
        for line in lines:
            stripped = line.strip()
            # Preserve comments and blank lines
            if not stripped or stripped.startswith(';'):
                f.write(line)
                continue
            # Write section headers as is
            if stripped.startswith('[') and stripped.endswith(']'):
                current_section = stripped[1:-1]
                f.write(line)
                continue
            # For key=value lines, update value if key exists in data
            if '=' in line and current_section:
                key, value = line.split('=', 1)
                key = key.strip()   # Preserve original case
                value = value.strip()
                if key in data[current_section]:
                    f.write(f'{key} = {data[current_section][key]}\n')
                else:
                    f.write(f'{key} = {value}\n')
            else:
                f.write(line)

class IniEditorDialog(QDialog):
    """
    IniEditorDialog provides a PyQt dialog for editing an INI file.
    It loads the INI file, lets the user edit key-value pairs per section,
    and shows key explanations as tooltips when the user clicks the "?" button.
    """
    def __init__(self, ini_file_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Settings Editor - {ini_file_path}")
        self.setMinimumSize(600, 400)
        self.ini_file_path = ini_file_path
        self.ini_data = read_ini_preserve_keys(self.ini_file_path)
        
        # Explanations for specific keys (must exactly match the INI file keys)
        self.explanations = {
            "vpx_root_folder": "The root directory where your Visual Pinball X tables (.vpx files) are located.",
            "executable_cmd": "The path to the Visual Pinball X executable.",
            "executable_sub_cmd": "The command-line argument used to launch a table (e.g., '-play').",
            "table_image_path": "The relative path to custom images used for table previews.",
            "table_wheel_path": "The relative path to custom images used for table wheel art.",
            "table_backglass_path": "The relative path to custom images used for table backglass displays.",
            "table_dmd_path": "The relative path to custom images used for table DMD displays.",
            "main_monitor_index": "The index of the monitor used for the main display.",
            "main_window_width": "The width of the main display window in pixels.",
            "main_window_height": "The height of the main display window in pixels.",
            "wheel_image_size": "The size (width and height) of the table wheel image in pixels.",
            "wheel_image_margin": "The margin (in pixels) between the table wheel image and the window edge.",
            "font_name": "The name of the font used for text displays.",
            "font_size": "The size of the font used for text displays in pixels.",
            "bg_color": "The background color (in hexadecimal format).",
            "text_color": "The color of the text displayed in the application windows.",
            "secondary_monitor_index": "The index of the monitor used for the secondary display.",
            "backglass_window_width": "The width of the backglass display window in pixels.",
            "backglass_window_height": "The height of the backglass display window in pixels.",
            "backglass_image_width": "The width of the backglass image in pixels.",
            "backglass_image_height": "The height of the backglass image in pixels.",
            "dmd_width": "The width of the DMD display in pixels.",
            "dmd_height": "The height of the DMD display in pixels.",
            "fade_duration": "The duration of fade transitions in milliseconds.",
            "fade_opacity": "The opacity level during fade transitions (0.0 to 1.0)."
        }
        self.entry_widgets = {}  # Will store QLineEdit widgets keyed by INI key

        self.init_ui()

    def init_ui(self):
        """
        Set up the dialog's user interface.
        """
        main_layout = QVBoxLayout(self)

        # Section selection controls
        section_layout = QHBoxLayout()
        section_label = QLabel("Select Section:")
        section_layout.addWidget(section_label)

        self.section_combo = QComboBox()
        self.section_combo.addItems(list(self.ini_data.keys()))
        self.section_combo.currentTextChanged.connect(self.load_section)
        section_layout.addWidget(self.section_combo)
        main_layout.addLayout(section_layout)

        # Scroll area to contain key/value entries
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.entries_widget = QWidget()
        self.entries_layout = QFormLayout(self.entries_widget)
        self.scroll_area.setWidget(self.entries_widget)
        main_layout.addWidget(self.scroll_area)

        # Buttons for saving or cancelling
        button_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_changes)
        button_layout.addWidget(save_button)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        main_layout.addLayout(button_layout)

        # Load the first section by default
        if self.ini_data:
            first_section = list(self.ini_data.keys())[0]
            self.section_combo.setCurrentText(first_section)
            self.load_section(first_section)

    def load_section(self, section):
        """
        Loads key-value pairs from the selected section into the form.
        """
        # Clear existing entries
        while self.entries_layout.count():
            item = self.entries_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        self.entry_widgets.clear()

        if section not in self.ini_data:
            return

        section_data = self.ini_data[section]
        for key, value in section_data.items():
            # For each key, create a horizontal layout with a label, an optional info button, and a QLineEdit.
            row_widget = QWidget()
            row_layout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(0, 0, 0, 0)
            key_label = QLabel(key)
            row_layout.addWidget(key_label)

            # Add a "?" button if an explanation exists for this key
            if key in self.explanations:
                info_button = QPushButton("?")
                info_button.setFixedSize(20, 20)
                info_button.setToolTip(self.explanations[key])
                row_layout.addWidget(info_button)

            line_edit = QLineEdit(value)
            row_layout.addWidget(line_edit)
            self.entry_widgets[key] = line_edit

            self.entries_layout.addRow(row_widget)

    def save_changes(self):
        """
        Save any changes made in the form back to the INI file.
        """
        section = self.section_combo.currentText()
        if section not in self.ini_data:
            QMessageBox.critical(self, "Error", f"Section '{section}' not found.")
            return

        # Update ini_data with new values
        for key, widget in self.entry_widgets.items():
            self.ini_data[section][key] = widget.text()

        try:
            write_ini_preserve_keys(self.ini_file_path, self.ini_data)
            QMessageBox.information(self, "Success", f"Changes saved to {self.ini_file_path}")
            self.accept()  # Close dialog on success
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save changes: {str(e)}")
        
        # Reload the configuration file
        config.load_configuration()

        # Reload the module so all values are updated dynamically
        importlib.reload(config)
