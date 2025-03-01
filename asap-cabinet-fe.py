import os
import sys
import logging
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QGuiApplication
from src.config import (MAIN_MONITOR_INDEX, MAIN_WINDOW_WIDTH, MAIN_WINDOW_HEIGHT,
                        SECONDARY_MONITOR_INDEX, BACKGLASS_WINDOW_WIDTH, BACKGLASS_WINDOW_HEIGHT, load_configuration)
from src.secondary_window import SecondaryWindow
from src.main_window import SingleTableViewer

'''
This is the entry point of your application. It loads the configuration,
creates both windows, positions them on the right screens, and starts
the Qt event loop.
'''

# --- Logging Configuration ---
# Expand the path to the errors log file
errors_log_path = os.path.expanduser("~/.asap-cabinet-fe/errors.log")
errors_log_dir = os.path.dirname(errors_log_path)
if not os.path.exists(errors_log_dir):
    os.makedirs(errors_log_dir)

# Configure the logging module to write errors to the log file
logging.basicConfig(
    filename=errors_log_path,
    level=logging.ERROR,  # Only log messages with level ERROR or higher
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Catch any uncaught exceptions and log them
def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logging.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

sys.excepthook = handle_exception

# --- Main Application ---
if __name__ == "__main__":
    # Check session type for potential Wayland issues
    session_type = os.environ.get("XDG_SESSION_TYPE", "unknown")
    if session_type.lower() == "wayland":
        print("Running under Wayland. For precise window positioning, consider launching with QT_QPA_PLATFORM=xcb")
        logging.error("Running under Wayland. For precise window positioning, consider launching with QT_QPA_PLATFORM=xcb")
    
    # Load application configuration
    load_configuration()
    
    # Create the QApplication instance
    app = QApplication(sys.argv)

    # Create and show the secondary (backglass) window
    secondary_window = SecondaryWindow()
    secondary_window.show()

    # Create and show the main viewer window, passing the secondary window reference
    viewer = SingleTableViewer(secondary_window)
    viewer.show()

    # Position windows on the correct monitors
    screens = QGuiApplication.screens()
    if len(screens) > MAIN_MONITOR_INDEX:
        main_screen = screens[MAIN_MONITOR_INDEX]
        main_geom = main_screen.geometry()
        viewer.windowHandle().setScreen(main_screen)
        viewer.move(main_geom.topLeft())
        viewer.setGeometry(main_geom.x(), main_geom.y(), MAIN_WINDOW_WIDTH, MAIN_WINDOW_HEIGHT)

    if len(screens) > SECONDARY_MONITOR_INDEX:
        secondary_screen = screens[SECONDARY_MONITOR_INDEX]
        sec_geom = secondary_screen.geometry()
        secondary_window.windowHandle().setScreen(secondary_screen)
        secondary_window.move(sec_geom.topLeft())
        secondary_window.setGeometry(sec_geom.x(), sec_geom.y(), BACKGLASS_WINDOW_WIDTH, BACKGLASS_WINDOW_HEIGHT)

    # Start the Qt event loop
    sys.exit(app.exec_())
