import os
import configparser
import subprocess
from pathlib import Path
import pytest
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog

# Assuming the script is named 'asap_cabinet_fe.py'
from asap_cabinet_fe import (
    load_configuration, CONFIG_FILE, VPX_ROOT_FOLDER, VPX_EXECUTABLE, EXECUTABLE_SUB_CMD,
    CUSTOM_TABLE_VIDEO, CUSTOM_TABLE_IMAGE, CUSTOM_WHEEL_IMAGE,
    CUSTOM_BACKGLASS_VIDEO, CUSTOM_BACKGLASS_IMAGE, CUSTOM_DMD_VIDEO, CUSTOM_MARQUEE_IMAGE,
    DEFAULT_TABLE_IMAGE, DEFAULT_WHEEL_IMAGE, DEFAULT_BACKGLASS_IMAGE, DEFAULT_DMD_VIDEO,
    get_image_path, load_table_list, SettingsDialog, SingleTableViewer, SearchDialog
)

# --- Configuration Loading Tests ---

def test_config_creation(tmp_path, monkeypatch):
    """Test that a config file is created with defaults when it doesn't exist."""
    temp_config_file = tmp_path / "settings.ini"
    monkeypatch.setattr('asap_cabinet_fe.CONFIG_FILE', str(temp_config_file))
    
    assert not temp_config_file.exists()
    load_configuration()
    assert temp_config_file.exists()
    
    config = configparser.ConfigParser()
    config.read(temp_config_file)
    assert config['Main Paths']['VPX_ROOT_FOLDER'] == os.path.expanduser("~/Games/vpinball/build/tables/")
    assert config['Main Paths']['VPX_EXECUTABLE'] == os.path.expanduser("~/Games/vpinball/build/VPinballX_GL")
    assert config['Main Paths']['EXECUTABLE_SUB_CMD'] == "-Play"
    assert config['Custom Media']['CUSTOM_TABLE_VIDEO'] == "video/table.gif"
    assert config['Main Window']['MAIN_MONITOR_INDEX'] == "1"

def test_config_loading(tmp_path, monkeypatch):
    """Test that settings are loaded correctly from an existing config file."""
    temp_config_file = tmp_path / "settings.ini"
    config = configparser.ConfigParser()
    config['Main Paths'] = {
        "VPX_ROOT_FOLDER": "/custom/tables",
        "VPX_EXECUTABLE": "/custom/vpx",
        "EXECUTABLE_SUB_CMD": "-custom"
    }
    config['Custom Media'] = {
        "CUSTOM_TABLE_IMAGE": "custom/table.png",
        "CUSTOM_WHEEL_IMAGE": "custom/wheel.png"
    }
    config['Main Window'] = {
        "MAIN_MONITOR_INDEX": "2"
    }
    with open(temp_config_file, "w") as f:
        config.write(f)
    
    monkeypatch.setattr('asap_cabinet_fe.CONFIG_FILE', str(temp_config_file))
    load_configuration()
    
    assert VPX_ROOT_FOLDER == "/custom/tables"
    assert VPX_EXECUTABLE == "/custom/vpx"
    assert EXECUTABLE_SUB_CMD == "-custom"
    assert CUSTOM_TABLE_IMAGE == "custom/table.png"
    assert CUSTOM_WHEEL_IMAGE == "custom/wheel.png"
    assert isinstance(MAIN_MONITOR_INDEX, int) and MAIN_MONITOR_INDEX == 2

# --- Table Data Loading Tests ---

def test_load_table_list(tmp_path, monkeypatch):
    """Test loading table data from a mock directory structure."""
    monkeypatch.setattr('asap_cabinet_fe.VPX_ROOT_FOLDER', str(tmp_path))
    
    # Table 1: Full media
    table1_dir = tmp_path / "table1"
    table1_dir.mkdir()
    (table1_dir / "table1.vpx").touch()
    os.makedirs(table1_dir / "video", exist_ok=True)
    os.makedirs(table1_dir / "images", exist_ok=True)
    (table1_dir / "video" / "table.gif").touch()  # CUSTOM_TABLE_VIDEO
    (table1_dir / "images" / "wheel.png").touch()  # CUSTOM_WHEEL_IMAGE
    (table1_dir / "video" / "backglass.gif").touch()  # CUSTOM_BACKGLASS_VIDEO
    (table1_dir / "video" / "dmd.gif").touch()  # CUSTOM_DMD_VIDEO
    
    # Table 2: Partial media
    table2_dir = tmp_path / "table2"
    table2_dir.mkdir()
    (table2_dir / "table2.vpx").touch()
    os.makedirs(table2_dir / "images", exist_ok=True)
    (table2_dir / "images" / "table.png").touch()  # CUSTOM_TABLE_IMAGE
    
    tables = load_table_list()
    
    assert len(tables) == 2
    # Table 1 assertions
    assert tables[0]["table_name"] == "table1"
    assert tables[0]["vpx_file"] == str(table1_dir / "table1.vpx")
    assert tables[0]["table_img"] == str(table1_dir / "video" / "table.gif")
    assert tables[0]["wheel_img"] == str(table1_dir / "images" / "wheel.png")
    assert tables[0]["backglass_img"] == str(table1_dir / "video" / "backglass.gif")
    assert tables[0]["dmd_img"] == str(table1_dir / "video" / "dmd.gif")
    # Table 2 assertions
    assert tables[1]["table_name"] == "table2"
    assert tables[1]["vpx_file"] == str(table2_dir / "table2.vpx")
    assert tables[1]["table_img"] == str(table2_dir / "images" / "table.png")
    assert tables[1]["wheel_img"] == DEFAULT_WHEEL_IMAGE
    assert tables[1]["backglass_img"] == DEFAULT_BACKGLASS_IMAGE
    assert tables[1]["dmd_img"] == DEFAULT_DMD_VIDEO

# --- Media Path Resolution Tests ---

def test_get_image_path(tmp_path):
    """Test media path resolution logic."""
    root = tmp_path
    preferred = "video/table.gif"
    fallback = "images/table.png"
    default = DEFAULT_TABLE_IMAGE
    
    # Preferred exists
    os.makedirs(root / "video", exist_ok=True)
    (root / "video" / "table.gif").touch()
    assert get_image_path(str(root), preferred, fallback, default) == str(root / "video" / "table.gif")
    
    # Only fallback exists
    (root / "video" / "table.gif").unlink()
    os.makedirs(root / "images", exist_ok=True)
    (root / "images" / "table.png").touch()
    assert get_image_path(str(root), preferred, fallback, default) == str(root / "images" / "table.png")
    
    # Neither exists
    (root / "images" / "table.png").unlink()
    assert get_image_path(str(root), preferred, fallback, default) == default

# --- Settings Dialog Tests ---

def test_settings_dialog_values(qtbot):
    """Test that SettingsDialog returns updated values."""
    dialog = SettingsDialog()
    qtbot.addWidget(dialog)
    
    # Modify some fields
    dialog.vpxRootEdit.setText("/new/tables")
    dialog.execCmdEdit.setText("/new/vpx")
    dialog.mainMonitor.setText("0")
    
    # Simulate acceptance
    dialog.accept()
    values = dialog.getValues()
    
    assert values["VPX_ROOT_FOLDER"] == "/new/tables"
    assert values["VPX_EXECUTABLE"] == "/new/vpx"
    assert values["MAIN_MONITOR_INDEX"] == "0"

def test_settings_validation(tmp_path, qtbot):
    """Test settings validation logic."""
    dialog = SettingsDialog()
    qtbot.addWidget(dialog)
    
    # Invalid VPX_ROOT_FOLDER
    dialog.vpxRootEdit.setText(str(tmp_path / "nonexistent"))
    dialog.execCmdEdit.setText(str(tmp_path / "vpx"))
    (tmp_path / "vpx").touch()
    errors = dialog.validate_settings(dialog.getValues())
    assert "is not a valid directory" in errors[0]
    
    # No .vpx files
    dialog.vpxRootEdit.setText(str(tmp_path))
    errors = dialog.validate_settings(dialog.getValues())
    assert "No .vpx files found" in errors[0]
    
    # Invalid executable
    dialog.vpxRootEdit.setText(str(tmp_path))
    (tmp_path / "table.vpx").touch()
    dialog.execCmdEdit.setText(str(tmp_path / "nonexistent"))
    errors = dialog.validate_settings(dialog.getValues())
    assert "is not a valid file" in errors[0]

# --- Search Dialog Tests ---

def test_search_dialog(qtbot):
    """Test SearchDialog query retrieval."""
    dialog = SearchDialog()
    qtbot.addWidget(dialog)
    
    dialog.searchEdit.setText("test query")
    dialog.accept()
    
    assert dialog.getSearchQuery() == "test query"

# --- Main Window GUI Tests ---

def test_navigation(qtbot, monkeypatch):
    """Test table navigation with arrow keys."""
    tables = [
        {"table_name": "table1", "vpx_file": "/path/table1.vpx", "folder": "/path",
         "table_img": DEFAULT_TABLE_IMAGE, "wheel_img": DEFAULT_WHEEL_IMAGE,
         "backglass_img": DEFAULT_BACKGLASS_IMAGE, "dmd_img": DEFAULT_DMD_VIDEO},
        {"table_name": "table2", "vpx_file": "/path/table2.vpx", "folder": "/path",
         "table_img": DEFAULT_TABLE_IMAGE, "wheel_img": DEFAULT_WHEEL_IMAGE,
         "backglass_img": DEFAULT_BACKGLASS_IMAGE, "dmd_img": DEFAULT_DMD_VIDEO},
    ]
    monkeypatch.setattr('asap_cabinet_fe.load_table_list', lambda: tables)
    
    viewer = SingleTableViewer()
    qtbot.addWidget(viewer)
    
    assert viewer.current_index == 0
    assert viewer.table_name_label.text() == "table1"
    
    qtbot.keyClick(viewer, Qt.Key_Right)
    assert viewer.current_index == 1
    assert viewer.table_name_label.text() == "table2"
    
    qtbot.keyClick(viewer, Qt.Key_Left)
    assert viewer.current_index == 0
    assert viewer.table_name_label.text() == "table1"

def test_launch_table(qtbot, monkeypatch):
    """Test launching a table with Enter key."""
    mock_popen = mock.Mock()
    mock_process = mock.Mock()
    mock_popen.return_value = mock_process
    monkeypatch.setattr(subprocess, 'Popen', mock_popen)
    
    tables = [
        {"table_name": "table1", "vpx_file": "/path/table1.vpx", "folder": "/path",
         "table_img": DEFAULT_TABLE_IMAGE, "wheel_img": DEFAULT_WHEEL_IMAGE,
         "backglass_img": DEFAULT_BACKGLASS_IMAGE, "dmd_img": DEFAULT_DMD_VIDEO},
    ]
    monkeypatch.setattr('asap_cabinet_fe.load_table_list', lambda: tables)
    monkeypatch.setattr('asap_cabinet_fe.VPX_EXECUTABLE', "/vpx")
    monkeypatch.setattr('asap_cabinet_fe.EXECUTABLE_SUB_CMD', "-play")
    
    viewer = SingleTableViewer()
    qtbot.addWidget(viewer)
    
    qtbot.keyClick(viewer, Qt.Key_Enter)
    mock_popen.assert_called_once_with(["/vpx", "-play", "/path/table1.vpx"])
    mock_process.wait.assert_called_once()

# Mock for QMessageBox in CI
@pytest.fixture(autouse=True)
def mock_qmessagebox(monkeypatch):
    monkeypatch.setattr('PyQt5.QtWidgets.QMessageBox.critical', lambda *args, **kwargs: None)
    monkeypatch.setattr('PyQt5.QtWidgets.QMessageBox.information', lambda *args, **kwargs: None)