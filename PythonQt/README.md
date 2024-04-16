## Pip Installs
```sh
pip install pyside6
pip install paramiko
pip install ftplib
```

## Py Initialization
Ensure PI is turned on and connected to wifi or ethernet and ssh is enabled. 

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