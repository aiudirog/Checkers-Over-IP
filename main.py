# main.py
from Globals import *
import Globals
from GUI import Window
import signal
import platform
signal.signal(signal.SIGINT, signal.SIG_DFL)

def main():
    if platform.system() == "Windows":
        import ctypes
        myappid = u'aiudirog.checkersoverip.main.1' # arbitrary string
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    app = QApplication(sys.argv)
    app_icon = QIcon()
    app_icon.addFile(os.path.join(Graphics, "Logos", 'Logo16x16.png'), QSize(16,16))
    app_icon.addFile(os.path.join(Graphics, "Logos", 'Logo24x24.png'), QSize(24,24))
    app_icon.addFile(os.path.join(Graphics, "Logos", 'Logo32x32.png'), QSize(32,32))
    app_icon.addFile(os.path.join(Graphics,"Logos", 'Logo48x48.png'), QSize(48,48))
    app_icon.addFile(os.path.join(Graphics,"Logos", 'Logo.png'), QSize(108,108))
    app_icon.addFile(os.path.join(Graphics,"Logos", 'Logo256x256.png'), QSize(256,256))
    Globals.AppIcon = app_icon
    app.setWindowIcon(Globals.AppIcon)
    screen_rect = app.desktop().screenGeometry()
    height = screen_rect.height()
    Globals.mainWindow = Window(height)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()