import os
import tempfile
import pytest
from shutil import copyfile
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtTest import QTest

# --- Test for SecondaryWindow.update_image ---
def test_secondary_window_update_image(qtbot, tmp_path, monkeypatch):
    # Create minimal GIF data (1x1 pixel) for testing QMovie-based media
    minimal_gif = b"GIF89a\x01\x00\x01\x00\x80\x01\x00\x00\x00\x00\xff\xff\xff,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"
    
    # Create temporary backglass GIF file
    backglass_gif = tmp_path / "backglass.gif"
    backglass_gif.write_bytes(minimal_gif)
    
    # Create temporary static image for backglass fallback (PNG)
    image = QImage(10, 10, QImage.Format_RGB32)
    image.fill(Qt.red)
    backglass_png = tmp_path / "backglass.png"
    image.save(str(backglass_png))
    
    # Create temporary DMD media files:
    # Custom DMD video (GIF)
    custom_dmd_video = tmp_path / "custom_dmd.gif"
    custom_dmd_video.write_bytes(minimal_gif)
    
    # Custom DMD image (PNG)
    custom_dmd_image = tmp_path / "custom_dmd.png"
    image.fill(Qt.green)
    custom_dmd_image_path = tmp_path / "custom_dmd_image.png"
    image.save(str(custom_dmd_image_path))
    
    # Default DMD video (GIF)
    default_dmd_video = tmp_path / "default_dmd.gif"
    default_dmd_video.write_bytes(minimal_gif)
    
    # Monkey-patch paths for DMD media in the module.
    from asap_cabinet_fe import SecondaryWindow, CUSTOM_DMD_VIDEO, CUSTOM_MARQUEE_IMAGE, DEFAULT_DMD_VIDEO
    monkeypatch.setattr("asap_cabinet_fe.CUSTOM_DMD_VIDEO", str(custom_dmd_video.relative_to(tmp_path)))
    monkeypatch.setattr("asap_cabinet_fe.CUSTOM_MARQUEE_IMAGE", str(custom_dmd_image_path.relative_to(tmp_path)))
    monkeypatch.setattr("asap_cabinet_fe.DEFAULT_DMD_VIDEO", str(default_dmd_video.relative_to(tmp_path)))
    
    # Create a temporary folder to act as the table folder.
    table_folder = str(tmp_path)
    
    # Instantiate SecondaryWindow
    sec_win = SecondaryWindow()
    qtbot.addWidget(sec_win)
    
    # --- Test Backglass update with GIF ---
    sec_win.update_image(str(backglass_gif), table_folder)
    # Check that the backglass label has a movie set.
    assert sec_win.label.movie() is not None, "Backglass should be using QMovie for a GIF."
    
    # --- Test DMD update with custom DMD video available ---
    sec_win.update_image(str(backglass_gif), table_folder)
    # Expect dmd_label to have a movie (since custom_dmd_video exists).
    assert sec_win.dmd_label.movie() is not None, "DMD should use QMovie when a custom DMD video is available."
    
    # --- Test DMD update with custom DMD video missing but custom image present ---
    # Remove custom DMD video
    custom_dmd_video.unlink()
    sec_win.update_image(str(backglass_gif), table_folder)
    # Expect dmd_label to have no movie, but a pixmap instead.
    assert sec_win.dmd_label.movie() is None, "DMD movie should be None when custom video is missing."
    assert sec_win.dmd_label.pixmap() is not None, "DMD pixmap should be set when custom DMD image is available."
    
    # --- Test DMD update with both custom video and custom image missing ---
    # Remove custom DMD image
    custom_dmd_image_path.unlink()
    sec_win.update_image(str(backglass_gif), table_folder)
    # Expect fallback to default DMD video.
    assert sec_win.dmd_label.movie() is not None, "DMD should fall back to default video when custom media are missing."

# --- Test for SingleTableViewer key events ---
def test_single_table_viewer_key_events(qtbot, monkeypatch):
    # Create a dummy table list
    dummy_table = {
        "table_name": "Test Table",
        "vpx_file": "dummy.vpx",
        "folder": ".",
        "table_img": "dummy_table.png",
        "wheel_img": "dummy_wheel.png",
        "backglass_img": "dummy_backglass.png",
        "dmd_img": "dummy_dmd.png"
    }
    # Monkey-patch load_table_list to return our dummy table list
    from asap_cabinet_fe import SingleTableViewer
    monkeypatch.setattr("asap_cabinet_fe.load_table_list", lambda: [dummy_table, dummy_table])
    
    # Create an instance of SingleTableViewer (without a secondary window)
    viewer = SingleTableViewer(secondary_window=None)
    qtbot.addWidget(viewer)
    
    # Check initial index
    init_index = viewer.current_index
    # Simulate right arrow key press
    QTest.keyClick(viewer.centralWidget(), Qt.Key_Right)
    # current_index should increase
    assert viewer.current_index == (init_index + 1) % 2, "Right key should switch to next table."
    
    # Simulate left arrow key press
    QTest.keyClick(viewer.centralWidget(), Qt.Key_Left)
    # current_index should wrap around or decrease accordingly
    assert viewer.current_index == init_index, "Left key should switch back to the original table."

# --- Test for launch_table without executing an external process ---
def test_launch_table(monkeypatch):
    from asap_cabinet_fe import SingleTableViewer
    dummy_table = {
        "table_name": "Test Table",
        "vpx_file": "dummy.vpx",
        "folder": ".",
        "table_img": "dummy_table.png",
        "wheel_img": "dummy_wheel.png",
        "backglass_img": "dummy_backglass.png",
        "dmd_img": "dummy_dmd.png"
    }
    monkeyatch_tables = [dummy_table]
    
    # Monkey-patch load_table_list to return our dummy table list.
    monkeypatch.setattr("asap_cabinet_fe.load_table_list", lambda: monkeyatch_tables)
    
    # Create an instance of SingleTableViewer.
    viewer = SingleTableViewer(secondary_window=None)
    
    # Monkey-patch subprocess.Popen to avoid launching an actual process.
    called_args = []
    class DummyProcess:
        def wait(self):
            return
    def dummy_popen(cmd, **kwargs):
        called_args.append(cmd)
        return DummyProcess()
    monkeypatch.setattr("asap_cabinet_fe.subprocess.Popen", dummy_popen)
    
    viewer.launch_table()
    # Check that the command list includes the VPX_EXECUTABLE and table file.
    assert len(called_args) == 1
    cmd = called_args[0]
    assert "dummy.vpx" in cmd[2], "launch_table should include the dummy vpx file in the command."

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
