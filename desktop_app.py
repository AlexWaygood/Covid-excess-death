from src.desktop_app.desktop_app_maximise_window import MaximiseWindow
from traceback_with_variables import printing_exc
from src.common_files import use_case

MaximiseWindow()
GUI_USAGE = False
SAVE_FILE = True


if __name__ == '__main__':
    with printing_exc():
        use_case.GUI_USAGE = GUI_USAGE
        from src.desktop_app.desktop_app_helpers import DesktopGraphPlotter
        DesktopGraphPlotter(GUIUsage=GUI_USAGE, SaveFile=SAVE_FILE).Run()
