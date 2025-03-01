import os
import subprocess
import logging
from .config import EXECUTABLE_CMD, EXECUTABLE_SUB_CMD

def launch_table(table):
    """Launches the selected table and logs output."""
    command = [EXECUTABLE_CMD, EXECUTABLE_SUB_CMD, table["vpx_file"]]
    
    log_path = os.path.expanduser("~/.asap-cabinet-fe/launcher.log")
    log_dir = os.path.dirname(log_path)
    os.makedirs(log_dir, exist_ok=True)

    try:
        with open(log_path, "w") as log_file:
            process = subprocess.Popen(command, stdout=log_file, stderr=log_file)
            process.wait()
    except Exception as e:
        logging.error(f"Error launching {table['vpx_file']}: {e}")
