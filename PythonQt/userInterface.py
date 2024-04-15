from PySide6 import QtCore, QtWidgets
from PySide6.QtWidgets import QFileDialog
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QColor, QPainter
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
import os
import paramiko
import re
import time
import functions


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
        self.ssh = None
        self.channel = None

        self.ui.play_audio_button.clicked.connect(lambda: self.playAudio(self.filepath))

        self.ui.pi_initialize_button.setEnabled(False)
        self.ui.terminal_action_frame.setEnabled(False)
        self.ui.terminal_text.setReadOnly(True)

        self.ui.pi_connect_button.clicked.connect(self.connectSSH)
        self.ui.pi_initialize_button.clicked.connect(self.initializePi)
        
        self.ui.terminal_input.returnPressed.connect(lambda: self.runCommand(self.ui.terminal_input.text()))
        self.ui.terminal_enter_button.clicked.connect(lambda: self.runCommand(self.ui.terminal_input.text()))
        self.ui.terminal_close_button.clicked.connect(self.closeTerminal)

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
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ip = self.ui.ip_input.text()
        self.user = self.ui.username_input.text()
        self.password = self.ui.password_input.text()
        try:
            self.ssh.connect(self.ip, 22, self.user, self.password)
            self.channel = self.ssh.invoke_shell()
            if self.ssh:
                self.ui.pi_initialize_button.setEnabled(True)
                self.ui.terminal_action_frame.setEnabled(True)
                self.runCommand(' ')
                text = self.ui.terminal_text.toPlainText()
                self.ui.terminal_text.setText(text[:-24])
                self.ui.pi_connect_button.setEnabled(False)
        except paramiko.AuthenticationException:
            print("Authentication failed")
            self.ui.terminal_text.setText("Authentication failed")
        except paramiko.SSHException as sshException:
            print("Could not establish SSH connection: %s" % sshException)
            self.ui.terminal_text.setText("Could not establish SSH connection: %s" % sshException)
        except Exception as e:
            print("An error has occured:", e)
            self.ui.terminal_text.setText("An error has occured")
    
    def runCommand(self, command):
        if self.channel:
            self.channel.send(command + '\n')  # Send the command to the channel
            self.channel.setblocking(False)  # Set the channel to non-blocking mode
            output = ''
            start_time = time.time()
            while True:
                # Read data from the channel
                try:
                    data = self.channel.recv(1024).decode()
                    if data:
                        output += data
                    else:
                        break  # No more data available, exit loop
                except:
                    pass  # No data available, continue loop
                # Check if the command has been running for more than 1 second
                if time.time() - start_time > 1:
                    break
                time.sleep(0.1)  # Sleep for a short time to prevent busy looping

            # Filter out ANSI escape codes using regular expressions
            filtered_output = re.sub(r'\x1b\[([0-9]{1,2}(;[0-9]{1,2})?)?[m|K]', '', output)
            filtered_output = re.sub(r'\x1b\[.*?[@-~]', '', filtered_output)
            old = self.ui.terminal_text.toPlainText()
            modified = self.modifyContent(old, filtered_output.strip())
            self.ui.terminal_text.setText(modified)
            self.ui.terminal_text.verticalScrollBar().setValue(self.ui.terminal_text.verticalScrollBar().maximum())
            self.ui.terminal_input.clear()


    def modifyContent(self, text, new):
        if text.endswith("\n"):
            text = text[:-1]
        text = text + ' ' + new + "\n"
        return text
    
    def closeTerminal(self):
        self.ui.terminal_text.clear()
        self.ui.terminal_action_frame.setEnabled(False)
        self.ui.pi_connect_button.setEnabled(True)
        self.ui.pi_initialize_button.setEnabled(False)
        self.ssh.close()
    
    def initializePi(self):
        # self.runCommand('sudo apt-get update && sudo apt-get upgrade -y')
        # self.runCommand(f'{self.password}')
        # self.runCommand("sudo apt-get install git cmake libusb-dev libusb-1.0-0-dev build-essential && git clone https://github.com/rxseger/rx_tools.git && \
        #                 cd rx_tools && mkdir build && cd build && cmake ../ && make && sudo make install && \
        #                 rx_fm_demod -h && sudo apt-get install vsftpd && sudo systemctl start vsftpd && \
        #                 sudo systemctl enable vsftpd && sudo systemctl status vsftpd")
        # self.runCommand("mkdir images")
        #self.runCommand("cd images && mkdir NOAA15 && mkdir NOAA18 && mkdir NOAA19")
        functions.ftp_connect(self.ip, self.user, self.password, f"/home/{self.user}/images/NOAA15", "NOAA15")
        functions.ftp_connect(self.ip, self.user, self.password, f"/home/{self.user}/images/NOAA18", "NOAA18")
        functions.ftp_connect(self.ip, self.user, self.password, f"/home/{self.user}/images/NOAA19", "NOAA19")
        

    def show(self):
        self.ui.show()