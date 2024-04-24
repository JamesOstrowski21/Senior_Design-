from PySide6 import QtCore, QtWidgets
from PySide6.QtWidgets import QFileDialog, QVBoxLayout, QTreeWidgetItem, QMainWindow, QLabel
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QColor, QPainter, QPixmap, QIcon
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
import os
import paramiko
import re
import time
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import functions
from intelliTrack.schedule_passes import Scheduler 
from intelliTrack.intelliTrack.compute_passes import make_station as makeStation
from beyond.dates import timedelta

loader = QUiLoader()

class UserInterface(QtCore.QObject):
    def __init__(self):
        super().__init__()
        self.filepath = ""
        self.localpath = ""
        self.ui = loader.load("uiFile/mainwindow.ui", None)
        self.ui.setWindowTitle("intelliTrack")
        self.ui.full_size_window = None
        self.ip = None
        self.user = None
        self.password = None
        
        self.station = None 
        self.scheduler = Scheduler()

        self.ui.image_frame.setLayout(QVBoxLayout())
        self.ui.file_import_button.clicked.connect(self.openWavFile)
        self.ui.decode_button.setEnabled(False)
        self.ui.play_audio_button.setEnabled(False)

        self.ui.audio_slider.setRange(0, 100)
        self.ui.audio_slider.setValue(50)
        self.ui.audio_slider.valueChanged.connect(self.setVolume)
        
        self.checkboxes = [self.ui.checkbox_2, self.ui.checkbox_3, self.ui.checkbox_none]
        for checkbox in self.checkboxes:
            checkbox.stateChanged.connect(self.updateDecodeButton)
        
        self.ui.checkbox_none.stateChanged.connect(self.updateBoxes)

        self.mediaPlayer = QMediaPlayer()
        self.audioOutput = QAudioOutput()
        self.mediaPlayer.setAudioOutput(self.audioOutput)
        self.ssh = None
        self.channel = None

        self.ui.ip_input.textChanged.connect(self.checkEnable)
        self.ui.username_input.textChanged.connect(self.checkEnable)
        self.ui.password_input.textChanged.connect(self.checkEnable)
        self.ui.pause_button.clicked.connect(self.pauseAudio)

        self.ui.play_audio_button.clicked.connect(lambda: self.playAudio(self.filepath))

        self.ui.pi_initialize_button.setEnabled(False)
        self.ui.terminal_action_frame.setEnabled(False)
        self.ui.imagePathFrame.setEnabled(False)
        self.ui.pi_connect_button.setEnabled(False)
        self.ui.scheduling_page.setEnabled(False)
        self.ui.images_page.setEnabled(False)
        self.ui.settings_page.setEnabled(False)
        self.ui.pause_button.setEnabled(False)
        self.ui.terminal_text.setReadOnly(True)

        self.ui.pi_connect_button.clicked.connect(self.connectSSH)
        self.ui.pi_initialize_button.clicked.connect(self.initializePi)
        self.ui.refresh_images_button.clicked.connect(self.refreshImages)
        self.ui.images_path_text.returnPressed.connect(self.refreshImages)
        self.ui.decode_button.clicked.connect(self.decodeImage)

        self.ui.terminal_text.setReadOnly(True)
        
        self.ui.terminal_input.returnPressed.connect(lambda: self.runCommand(self.ui.terminal_input.text()))
        self.ui.terminal_enter_button.clicked.connect(lambda: self.runCommand(self.ui.terminal_input.text()))
        self.ui.terminal_close_button.clicked.connect(self.closeTerminal)

        self.checkInternetConnection()
        self.loadCongif()

        ## Image Page
        self.ui.image_structure.itemSelectionChanged.connect(self.updateImages)
        self.ui.image_display.itemClicked.connect(self.fullSizeImage)
        self.addRootItems()

        ## Scheduling Page
        self.ui.predict_button.setEnabled(False)
        self.ui.predict_button.clicked.connect(self.predictPasses)
        self.ui.schedule_button.setEnabled(False)
        self.predictBoxes = [self.ui.NOAA15_checkbox, self.ui.NOAA18_checkbox, self.ui.NOAA19_checkbox]
        for checkbox in self.predictBoxes:
            checkbox.stateChanged.connect(self.updatePredictButton)
            checkbox.setFocusPolicy(QtCore.Qt.NoFocus)
            
        self.ui.latitude.textChanged.connect(self.updatePredictButton)
        self.ui.longitude.textChanged.connect(self.updatePredictButton)
        self.ui.elevation.textChanged.connect(self.updatePredictButton)

    def predictPasses(self):
        self.longitude = self.ui.longitude.text()
        self.latitude = self.ui.latitude.text()
        self.elevation = self.ui.elevation.text()
        self.ui.predicted_passes.clearContents()
        self.ui.predicted_passes.setRowCount(0)
        sats = []
        if self.ui.NOAA15_checkbox.isChecked():
            sats.append("NOAA 15")
        if self.ui.NOAA18_checkbox.isChecked():
            sats.append("NOAA 18")
        if self.ui.NOAA19_checkbox.isChecked():
            sats.append("NOAA 19")

        # TODO: if the user changes their ground station update the lle, else do nothing
        lle = (float(self.ui.latitude.text()), float(self.ui.longitude.text()), float(self.ui.elevation.text()))
        self.station = makeStation("Home", *lle)
    
        # TODO: allow user to set a quality thresh, also maybe allow them to set the stop time (up to a week maybe)
        # scheduler.quality_thres = 0.25
        self.confirmed_passes = self.scheduler.schedule_passes(sats, self.station, stop=timedelta(days=1))
        for _pass in self.confirmed_passes:
            quality = "{:.2f}".format(_pass.quality)
            duration = "{:.2f}".format(_pass.duration.total_seconds()/60) + " minutes"
            self.ui.predicted_passes.insertRow(self.ui.predicted_passes.rowCount())
            data = [_pass.satellite, 
                    _pass.start_time.strftime('%M-%d-%Y %H:%M:%S'), 
                    _pass.end_time.strftime('%M-%d-%Y %H:%M:%S'), 
                    duration, quality]
            
            for column, value in enumerate(data):
                item = QtWidgets.QTableWidgetItem(value)
                self.ui.predicted_passes.setItem(self.ui.predicted_passes.rowCount()-1, column, item)
                
        # TODO: If the user presses the upper left corner of the label, the buttons to view the pointings vanishes
        for row in range(self.ui.predicted_passes.rowCount()):
            button = QtWidgets.QPushButton("View Plot")
            button.clicked.connect(self.viewPlot)
            self.ui.predicted_passes.setCellWidget(row, 5, button)
            
        self.ui.predicted_passes.setColumnWidth(1, 118)
        self.ui.predicted_passes.setColumnWidth(2, 118)
        # self.ui.predicted_passes.cellClicked.connect(lambda row, col: self.viewPlot(row, col))
        self.updateConfig()
    
    def viewPlot(self):
        # print(self.ui.predicted_passes.currentRow())
        self.confirmed_passes[self.ui.predicted_passes.currentRow()].plot_station_pointings()

    def updatePredictButton(self):
        temp = False
        if any(checkbox.isChecked() for checkbox in self.predictBoxes):
            temp = True
        else:
            self.ui.predict_button.setEnabled(False)
            temp = False

        if self.ui.longitude.text() and self.ui.latitude.text() and self.ui.elevation.text() and temp:
            self.ui.predict_button.setEnabled(True)

    def addRootItems(self):
        rootItem1 = QTreeWidgetItem(self.ui.image_structure, ["NOAA15"])
        rootItem1.setIcon(0, QIcon(os.path.join(os.getcwd(), "resources/folderIcon.png")))
        rootItem2 = QTreeWidgetItem(self.ui.image_structure, ["NOAA18"])
        rootItem2.setIcon(0, QIcon(os.path.join(os.getcwd(), "resources/folderIcon.png")))
        rootItem3 = QTreeWidgetItem(self.ui.image_structure, ["NOAA19"])
        rootItem3.setIcon(0, QIcon(os.path.join(os.getcwd(), "resources/folderIcon.png")))

    def updateImages(self):
        selectedItem = self.ui.image_structure.currentItem()
        folder = selectedItem.text(0)
        folderPath = os.path.join(self.localpath, "images", folder)

        self.clearImages()

        imageFiles = [f for f in os.listdir(folderPath) if f.endswith(".png")]


        for idx, image in enumerate(imageFiles):
            pixmap = QPixmap(os.path.join(folderPath, image))
            pixmap = pixmap.scaled(250, 300, QtCore.Qt.KeepAspectRatio)

            # Create a QLabel widget to display the image
            image_label = QtWidgets.QLabel()
            image_label.setPixmap(pixmap)

            # Create a QLabel widget to display the filename
            filename_label = QtWidgets.QLabel(image)
            filename_label.setAlignment(QtCore.Qt.AlignCenter)

            # Create a QVBoxLayout to stack the image and filename labels vertically
            layout = QtWidgets.QVBoxLayout()
            layout.addWidget(image_label)
            layout.addWidget(filename_label)
            layout.setAlignment(QtCore.Qt.AlignCenter)

            # Create a QWidget to hold the layout
            widget = QtWidgets.QWidget()
            widget.setLayout(layout)

            # Add the QWidget to a QListWidgetItem
            item = QtWidgets.QListWidgetItem()
            item.setSizeHint(QtCore.QSize(280,300))
            item.setText(f"{folder}/{image}")  # Set the size hint for the item
            self.ui.image_display.addItem(item)
            self.ui.image_display.setItemWidget(item, widget)

        # Set the layout mode and resize mode of the QListWidget
        self.ui.image_display.setLayoutMode(QtWidgets.QListView.SinglePass)
        self.ui.image_display.setResizeMode(QtWidgets.QListView.Adjust)
        self.ui.image_display.setViewMode(QtWidgets.QListView.IconMode)

        scrollBar = self.ui.image_display.verticalScrollBar()
        scrollBar.setSingleStep(10)
        
    def clearImages(self):
            self.ui.image_display.clear()

    def fullSizeImage(self, item):
        # Get the text (filename) of the clicked item
        filename = item.text()

        # Create a new window to display the full-size image
        self.full_size_window = QMainWindow()
        self.full_size_window.setWindowTitle(filename)
        self.full_size_window.setStyleSheet("QMainWindow { border: 10px solid black; }")
        # Create a label to display the full-size image
        full_size_label = QLabel()
        pixmap = QPixmap(os.path.join(self.localpath, "images", filename))
        full_size_label.setPixmap(pixmap)
        full_size_label.setScaledContents(True)
        # Set size policy for the label to "Ignored" to allow free resizing
        full_size_label.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)

        # Create a vertical layout for the central widget and add the label
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(full_size_label)

        # Create a widget to serve as the central widget and set the layout
        central_widget = QtWidgets.QWidget()
        central_widget.setLayout(layout)

        # Set the central widget of the QMainWindow
        self.full_size_window.setCentralWidget(central_widget)

        # Resize the window to fit the image, with a maximum size limit
        max_width = 800  # Set maximum width for the window
        max_height = 600  # Set maximum height for the window
        window_width = min(pixmap.width(), max_width)
        window_height = min(pixmap.height(), max_height)
        self.full_size_window.resize(window_width, window_height)

        # Show the window
        self.full_size_window.show()

    @QtCore.Slot()
    def openWavFile(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self.ui, "Open Wav File", "", "Wav Files (*.wav)", options=options)
        if file_name:
            self.ui.file_type_label.setText(os.path.basename(file_name))
            self.updateDecodeButton()
            self.filepath = file_name
            self.ui.play_audio_button.setEnabled(True)

    @QtCore.Slot()
    def updateDecodeButton(self):
        if any(checkbox.isChecked() for checkbox in self.checkboxes):
            self.ui.decode_button.setEnabled(True)
        else:
            self.ui.decode_button.setEnabled(False)

    @QtCore.Slot()
    def updateBoxes(self):
        if self.ui.checkbox_none.isChecked():
            self.ui.checkbox_2.setEnabled(False)
            self.ui.checkbox_3.setEnabled(False)
            self.ui.checkbox_2.setChecked(False)
            self.ui.checkbox_3.setChecked(False)
        elif self.ui.checkbox_none.isChecked() == False:
            self.ui.checkbox_2.setEnabled(True)
            self.ui.checkbox_3.setEnabled(True)


    def playAudio(self, file_path):
        self.mediaPlayer.setSource(QtCore.QUrl.fromLocalFile(file_path))
        self.audioOutput.setVolume(self.ui.audio_slider.value()/1000.0)
        self.mediaPlayer.play()
        self.ui.play_audio_button.setEnabled(False)
        self.ui.pause_button.setEnabled(True)

    def pauseAudio(self):
        self.mediaPlayer.pause()
        self.ui.pause_button.setEnabled(False)
        self.ui.play_audio_button.setEnabled(True)

    def setVolume(self):
        self.audioOutput.setVolume(self.ui.audio_slider.value()/1000.0)
    
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
                self.ui.imagePathFrame.setEnabled(True)
                self.updateConfig()
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
        self.runCommand('sudo apt-get update && sudo apt-get upgrade -y')
        self.runCommand(f'{self.password}')
        self.runCommand("sudo apt-get install git cmake libusb-dev libusb-1.0-0-dev build-essential && git clone https://github.com/rxseger/rx_tools.git && \
                        cd rx_tools && mkdir -p build && cd build && cmake ../ && make && sudo make install && \
                        rx_fm_demod -h && sudo apt-get install vsftpd && sudo systemctl start vsftpd && \
                        sudo systemctl enable vsftpd && sudo systemctl status vsftpd")
        self.runCommand("mkdir -p intelliTrack")
        self.runCommand("cd intelliTrack")
        self.runCommand("mkdir -p images")
        self.runCommand("cd images && mkdir -p NOAA15 && mkdir -p NOAA18 && mkdir -p NOAA19")
        self.localpath = os.getcwd()
        self.updateConfig()
        self.loadCongif()

    def refreshImages(self):
        self.localpath = self.ui.images_path_text.text()
        functions.ftp_connect(self.ip, self.user, self.password, f"/home/{self.user}/intelliTrack/images/NOAA15", "NOAA15", self.localpath)
        functions.ftp_connect(self.ip, self.user, self.password, f"/home/{self.user}/intelliTrack/images/NOAA18", "NOAA18", self.localpath)
        functions.ftp_connect(self.ip, self.user, self.password, f"/home/{self.user}/intelliTrack/images/NOAA19", "NOAA19", self.localpath)
        self.updateConfig()

    def updateConfig(self):
        functions.updateConfigFile(self.localpath, self.ip, self.user, self.password, self.longitude, self.latitude, self.elevation)

    def loadCongif(self):
        path, ip, name, password, longitude, latitude, elevation = functions.loadConfigFile()
        self.ui.images_path_text.setText(path)
        self.ui.ip_input.setText(ip)
        self.ui.username_input.setText(name)
        self.ui.password_input.setText(password)
        self.ui.longitude.setText(longitude)
        self.ui.latitude.setText(latitude)
        self.ui.elevation.setText(elevation)

    def checkEnable(self):
        if self.ui.ip_input.text() and self.ui.username_input.text() and self.ui.password_input.text():
            self.ui.pi_connect_button.setEnabled(True)

    def checkInternetConnection(self):
        if functions.checkInternetConnection():
            self.ui.scheduling_page.setEnabled(True)
            self.ui.images_page.setEnabled(True)
            self.ui.settings_page.setEnabled(True)

    def decodeImage(self):
        image = os.path.join(os.getcwd(), "images/NOAA15/test15.png")
        pixmage = QPixmap(image)
        self.ui.image_label.setPixmap(pixmage)
        self.ui.image_label.setScaledContents(True)

    def show(self):
        self.ui.show()