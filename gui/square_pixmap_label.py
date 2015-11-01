from PyQt4.QtGui import QLabel, QApplication
from PyQt4.QtCore import Qt, QSize


class SquarePixmapLabel(QLabel):
    def __init__(self, parent):
        super(SquarePixmapLabel, self).__init__(parent)
        self.setMinimumSize(1, 1)
        self.pix = None
        self.get_main_window().RESIZE.connect(self.resize_of_main_win_event)

    def setPixmap(self, pixmap):
        self.pix = pixmap
        super(SquarePixmapLabel, self).setPixmap(pixmap)

    def heightForWidth(self, w):
        return w

    def resize_of_main_win_event(self):
        main_win_size = self.get_main_window().size()
        m = min(main_win_size.height(), main_win_size.width())
        super(SquarePixmapLabel, self).setPixmap(self.pix.scaled(QSize(m, m),
                                                                 Qt.KeepAspectRatio, Qt.SmoothTransformation))

    # noinspection PyArgumentList
    @staticmethod
    def get_main_window():
        widgets = QApplication.instance().topLevelWidgets()
        for widget in widgets:
            if hasattr(widget, 'name'):
                if widget.name == 'Main Window':
                    return widget
