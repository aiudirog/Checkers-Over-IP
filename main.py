# main.py
from Globals import *
import Globals
from GUI import Window
import sys



def main():
    app = QApplication(sys.argv)
    screen_rect = app.desktop().screenGeometry()
    height = screen_rect.height()
    Globals.mainWindow = Window(height)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()