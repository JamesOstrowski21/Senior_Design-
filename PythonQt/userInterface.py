from PySide6 import QtCore, QtWidgets
from PySide6.QtWidgets import QFileDialog
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QColor, QPainter
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
import os
import paramiko


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

        self.ip = self.ui.ip_input.text()
        self.user = self.ui.username_input.text()
        self.password = self.ui.password_input.text()

        self.ui.pi_connect_button.clicked.connect(self.connectSSH)


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
    
    def connectSSH(self):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            ssh.connect('192.168.4.132', 22, 'jameso', '@Ski2024')
            stdin, stdout, stderr = ssh.exec_command('ls')
            x = stdout.read().decode()
            print(x)
            self.ui.terminal_text.setText(x)
            ssh.close()
        except paramiko.AuthenticationException:
            print("Authentication failed")
            self.ui.terminal_text.setText("Authentication failed")
        except paramiko.SSHException as sshException:
            print("Could not establish SSH connection: %s" % sshException)
            self.ui.terminal_text.setText("Could not establish SSH connection: %s" % sshException)
        except Exception as e:
            print("An error has occured:", e)
            self.ui.terminal_text.setText("An error has occured")
        return 

    def show(self):
        self.ui.show()