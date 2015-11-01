# main.py
import Globals as Gl
from gui import Window
import platform
import os
import sys
from PyQt4.QtGui import QApplication, QIcon
from PyQt4.QtCore import QSize


# Allow ctrl+c to kill program from cli.
import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)


def main():
    # Assign this program an App ID so that the task bar icon will appear on Windows.
    if platform.system() == "Windows":
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(u'aiudirog.checkersoverip.main.1')

    app = QApplication(sys.argv)

    # Create and set application icon
    app_icon = QIcon()
    app_icon.addFile(os.path.join(Gl.Graphics, "Logos", 'Logo16x16.png'), QSize(16, 16))
    app_icon.addFile(os.path.join(Gl.Graphics, "Logos", 'Logo24x24.png'), QSize(24, 24))
    app_icon.addFile(os.path.join(Gl.Graphics, "Logos", 'Logo32x32.png'), QSize(32, 32))
    app_icon.addFile(os.path.join(Gl.Graphics, "Logos", 'Logo48x48.png'), QSize(48, 48))
    app_icon.addFile(os.path.join(Gl.Graphics, "Logos", 'Logo.png'), QSize(108, 108))
    app_icon.addFile(os.path.join(Gl.Graphics, "Logos", 'Logo256x256.png'), QSize(256, 256))
    Gl.AppIcon = app_icon
    app.setWindowIcon(Gl.AppIcon)

    Gl.mainWindow = Window(app.desktop().screenGeometry())
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
