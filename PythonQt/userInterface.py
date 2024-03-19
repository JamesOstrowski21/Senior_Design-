from PySide6 import QtCore, QtWidgets
from PySide6.QtWidgets import QFileDialog
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QColor, QPainter
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
import os


loader = QUiLoader()

class UserInterface(QtCore.QObject):
    def __init__(self):
        super().__init__()
        self.filepath = ""
        self.ui = loader.load("uiFile/mainwindow.ui", None)
        self.ui.setWindowTitle("intelliTrack")

        self.ui.file_import_button.clicked.connect(self.openWavFile)
        self.ui.decode_button.setEnabled(False)
        self.ui.play_audio_button.setEnabled(False)

        
        self.checkboxes = [self.ui.checkbox_1, self.ui.checkbox_2, self.ui.checkbox_3, self.ui.checkbox_none]
        for checkbox in self.checkboxes:
            checkbox.stateChanged.connect(self.updateDecodeButton)

        self.mediaPlayer = QMediaPlayer()
        self.audioOutput = QAudioOutput()
        self.mediaPlayer.setAudioOutput(self.audioOutput)

        self.ui.play_audio_button.clicked.connect(self.playAudio(self.filepath))


    @QtCore.Slot()
    def openWavFile(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self.ui, "Open Wav File", "", "Wav Files (*.wav)", options=options)
        if file_name:
            self.ui.file_type_label.setText(os.path.basename(file_name))
            self.updateDecodeButton()
            self.filepath = file_name
            self.ui.play_audio_button.setEnabled(True)
            self.ui.play_audio_button.clicked.connect(self.playAudio(self.filepath))

    @QtCore.Slot()
    def updateDecodeButton(self):
        if any(checkbox.isChecked() for checkbox in self.checkboxes):
            self.ui.decode_button.setEnabled(True)
        else:
            self.ui.decode_button.setEnabled(False)

    def playAudio(self, file_path):
        print(file_path)
        self.mediaPlayer.setSource(QtCore.QUrl.fromLocalFile(file_path))
        self.audioOutput.setVolume(0.03)
        self.mediaPlayer.play()

    def show(self):
        self.ui.show()