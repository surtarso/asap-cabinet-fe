import os
import tempfile
import pytest

from asap_cabinet_fe import get_image_path, load_table_list

def test_get_image_path(tmp_path):
    # Create a temporary file to simulate an image file.
    file_path = tmp_path / "table.png"
    file_path.write_text("dummy content")

    # Test when file exists: should return the file path.
    result = get_image_path(str(tmp_path), "table.png", "default.png")
    assert result == str(tmp_path / "table.png")

    # Test when file does not exist: should return the default.
    result_default = get_image_path(str(tmp_path), "nonexistent.png", "default.png")
    assert result_default == "default.png"

def test_load_table_list(tmp_path, monkeypatch):
    # Create a temporary directory to simulate VPX_ROOT_FOLDER.
    temp_tables_dir = tmp_path / "vpx_tables"
    temp_tables_dir.mkdir()

    # Create a dummy .vpx file inside the temporary directory.
    dummy_vpx = temp_tables_dir / "test_table.vpx"
    dummy_vpx.write_text("dummy table content")

    # Monkey-patch VPX_ROOT_FOLDER to point to our temporary directory.
    monkeypatch.setattr("asap_cabinet_fe.VPX_ROOT_FOLDER", str(temp_tables_dir))

    # Call load_table_list and check that it finds our dummy .vpx file.
    tables = load_table_list()
    assert isinstance(tables, list)
    # Look for our dummy file in the list of tables.
    found = any("test_table.vpx" in table["vpx_file"] for table in tables)
    assert found, "The dummy .vpx file should be found in the table list."
