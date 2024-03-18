from PySide6 import QtCore, QtWidgets
from PySide6.QtWidgets import QFileDialog
from PySide6.QtUiTools import QUiLoader

loader = QUiLoader()

class UserInterface(QtCore.QObject):
    def __init__(self):
        super().__init__()
        self.ui = loader.load("uiFile/mainwindow.ui", None)
        self.ui.setWindowTitle("intelliTrack")
 
        self.ui.file_import_button.clicked.connect(self.open_wav_file)
        self.ui.decode_button.setEnabled(False)

    @QtCore.Slot()
    def open_wav_file(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self.ui, "Open Wav File", "", "Wav Files (*.wav)", options=options)
        if file_name:
            self.ui.file_type_label.setText(file_name)
            self.ui.decode_button.setEnabled(True)

    def show(self):
        self.ui.show()