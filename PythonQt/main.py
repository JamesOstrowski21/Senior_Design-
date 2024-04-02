import sys

from PySide6 import QtWidgets
from userInterface import UserInterface


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = UserInterface()
    window.show()
    sys.exit(app.exec())