import os
import tempfile
import pytest

# --- Test for helper functions ---

def test_get_image_path(tmp_path):
    # Create a temporary file to simulate an image file.
    file_path = tmp_path / "table.png"
    file_path.write_text("dummy content")
    
    # When the file exists, get_image_path should return its path.
    from asap_cabinet_fe import get_image_path
    result = get_image_path(str(tmp_path), "table.png", "nonexistent.png", "default.png")
    assert result == str(tmp_path / "table.png")
    
    # When the file does not exist, it should return the default.
    result_default = get_image_path(str(tmp_path), "nonexistent.png", "also_nonexistent.png", "default.png")
    # Note: get_image_path returns os.path.join(root, default_media_path)
    assert result_default == str(tmp_path / "default.png")

def test_load_table_list(tmp_path, monkeypatch):
    # Create a temporary directory to simulate VPX_ROOT_FOLDER.
    temp_tables_dir = tmp_path / "vpx_tables"
    temp_tables_dir.mkdir()
    
    # Create a dummy .vpx file inside the temporary directory.
    dummy_vpx = temp_tables_dir / "test_table.vpx"
    dummy_vpx.write_text("dummy table content")
    
    # Monkey-patch VPX_ROOT_FOLDER to point to our temporary directory.
    monkeypatch.setattr("asap_cabinet_fe.VPX_ROOT_FOLDER", str(temp_tables_dir))
    
    from asap_cabinet_fe import load_table_list
    tables = load_table_list()
    assert isinstance(tables, list)
    # Check that our dummy file is found.
    found = any("test_table.vpx" in table["vpx_file"] for table in tables)
    assert found, "The dummy .vpx file should be found in the table list."

# --- Test for GUI components using pytest-qt ---

def test_search_dialog(qtbot):
    # Test the SearchDialog by simulating text input.
    from asap_cabinet_fe import SearchDialog
    dialog = SearchDialog()
    qtbot.addWidget(dialog)
    
    test_query = "sample search"
    dialog.searchEdit.setText(test_query)
    # Check that getSearchQuery returns what we entered.
    assert dialog.getSearchQuery() == test_query

def test_settings_dialog(qtbot):
    # Test the SettingsDialog by setting some fields and retrieving them.
    from asap_cabinet_fe import SettingsDialog
    dialog = SettingsDialog()
    qtbot.addWidget(dialog)
    
    # Set some test values.
    dialog.vpxRootEdit.setText("/dummy/path")
    dialog.execCmdEdit.setText("/dummy/executable")
    # Retrieve values.
    values = dialog.getValues()
    assert values["VPX_ROOT_FOLDER"] == "/dummy/path"
    # Updated expected key from EXECUTABLE_CMD to VPX_EXECUTABLE.
    assert values["VPX_EXECUTABLE"] == "/dummy/executable"

# --- Test for configuration loader ---

def test_load_configuration(tmp_path, monkeypatch):
    # Override CONFIG_FILE to use a temporary settings file.
    from asap_cabinet_fe import load_configuration, CONFIG_FILE
    fake_config = tmp_path / "settings.ini"
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setattr("asap_cabinet_fe.CONFIG_FILE", str(fake_config))
    
    # Ensure the file doesn't exist before loading configuration.
    if fake_config.exists():
        fake_config.unlink()
    
    load_configuration()
    
    # After load_configuration, the config file should have been created.
    assert fake_config.exists()
