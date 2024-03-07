from PySide6 import QtCore, QtWidgets
from PySide6.QtUiTools import QUiLoader

loader = QUiLoader()

class UserInterface(QtCore.QObject):
    def __init__(self):
        super().__init__()
        self.ui = loader.load("uiFile/mainwindow.ui", None)
        self.ui.setWindowTitle("My App")

    def show(self):
        self.ui.show()