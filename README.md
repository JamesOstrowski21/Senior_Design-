# intelliTrack-Qt
This is an application to support intelliTrack. We are building a system system capable of seamlessly acquiring, processing, and analyzing satellite imagery from various orbits, including low earth, geosynchronous, and polar orbits. This application is built using PySide6 a python binding for the Qt C++ Framework. 

## Usage Instructions
Ensure you have at least python 3.10 installed, and install the required dependencies with your favorite package manager. 
`pip install -r requirements.txt`

## Running the Application
Currently this application is run via the main.py script, but in the future there will be a full release package available to be integrated for macos, linux, and windows. 

run with `python pythonQT/main.py` 

## Decode Page 
The decode page is used to decode the APT information recorded and saved in a .wav format. The decoding algorihtm with resample you input waveforms to 22050Hz then perform the decoding algorithm. 

You can select the file you want to decode by clicking the "Select File" button. Then name your output image in the textbox provided. 

You can also select which channels you want to have saved, if you select None the raw sync image will be saved to the satellites respective directory. 

You may also want to listen to your recording, and that can be done via the play function below the file input. (RECOMMENDED not to be wearing headphones, and keep device audio very low as recordings can sometimes be VERY loud)

## Schedule Page
To utilize this page first input the latitude, longitude, and elevation of the ground station you are trying to predict the satellite position for. For now use external tools such as google earth to get this information. 

After which you can select the satellites you want to predict, and how many days in advance you want to predict for. The table on the right will then be populated with the satellite name, and the start time, end time, and a quality metric. This metric takes into account duration of pass, max elevation, and length of duration at heights above 30 degrees in elevation. 

You may also view the station points of the pass, and see the tradjectory the satellite will be taking. 

Once you are satisfied you can select passes with a `ctrl-click` action, and then press the `Predict` button to save those times and dates for your convience

## Images Page
In this page you can view all the images that have been decoded with IntelliTrack. They are stored based off the satellite you selected in the decode page.

## Settings Page 

Here is where you can connect to your raspberry pi for automous recording of passes. Ensure that your pi is connected to the same network, and that you know its IP address, and login information for a secure ssh connection. 

Once connected you can send commands directly to the pi using the embedded interface. 
The scheduling on the pi can be done via the command line, or by using the `crontab` command.

# Development/Contribution
Below are some useful steps to start working on this repository

## Qt Information
This is an open source framwork capable of building full stack desktop applications. 
[Qt Download](https://www.qt.io/download-open-source) 

## Qt Installation
If you already have python installed on you machine you can follow these instructuions [Qt For Python](https://doc.qt.io/qtforpython-6/quickstart.html)

## Git Cloning 
*** DO NOT WORK OFF OF MAIN ***

```sh
git clone https://github.com/JamesOstrowski21/Senior_Design-.git
cd Senior-Design-
git checkout -b <branch_name>
git submodule update --init --recursive
```

## Git Commit/Push

```sh
git add .
git commit -m "<your message>"
git push
```
## After Merge
```sh
git fetch
git pull
```
## Py Initialization
Ensure PI is turned on with Raspberry PI OS installed and connected to wifi or ethernet and ssh is enabled. 

## Init Commands
```sh
sudo apt-get update && sudo apt-get upgrade -y
sudo apt-get install git cmake libusb-dev libusb-1.0-0-dev build-essential
git clone https://github.com/rxseger/rx_tools.git
cd rx_tools
mkdir build
cd build
cmake ../
make 
sudo make install
rx_fm_demod -h
sudo apt-get install vsftpd
sudo systmect1 start vsftpd
sudo systemct1 enable vsftpd
sudo systemct1 status vsftpd
mkdir -p intelliTrack
cd intelliTrack
mkdir -p images
cd images
mkdir -p NOAA15
mdkir -p NOAA18
mdkir -p NOAA19
```
