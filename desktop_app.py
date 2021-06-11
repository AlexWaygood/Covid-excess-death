from src.desktop_app.maximise_terminal_window import MaximiseWindow
from traceback_with_variables import printing_exc
from src.common_files import use_case

MaximiseWindow()
GUI_USAGE = True
SAVE_FILE = False


if __name__ == '__main__':
    with printing_exc():
        use_case.GUI_USAGE = GUI_USAGE
        use_case.LOCAL_HOSTING = True
        use_case.WEB_MODE = False
        use_case.DESKTOP_MODE = True

        from src.desktop_app.desktop_graph_plotting import DesktopGraphPlotter
        DesktopGraphPlotter(GUIUsage=GUI_USAGE, SaveFile=SAVE_FILE).Run()
