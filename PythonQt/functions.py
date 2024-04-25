from ftplib import FTP
import os
import requests
import datetime

def ftp_connect(host, user, passwd, filepath, folder, localpath):
    ftp = FTP(host)
    ftp.login(user, passwd)
    ftp.cwd(filepath)
    fileList = ftp.nlst()
    os.makedirs(os.path.join(localpath,"images", folder), exist_ok=True)

    for filename in fileList:
        if filename.endswith(".png"):
            print(filename)
            localpath = os.path.join(localpath, "images", folder, filename)

            if not os.path.exists(localpath):
                with open(localpath , "wb") as file:
                    ftp.retrbinary("RETR " + filename, file.write)

    ftp.quit()

def makeDirs():
    os.makedirs(os.path.join(os.getcwd(),"images", "NOAA 15"), exist_ok=True)
    os.makedirs(os.path.join(os.getcwd(),"images", "NOAA 18"), exist_ok=True)
    os.makedirs(os.path.join(os.getcwd(),"images", "NOAA 19"), exist_ok=True)

def makeFiles():
    path = os.path.join(os.getcwd(), "scheduledPasses.txt")
    if not os.path.exists(path):
        try:
            with open(path, "w") as file:
                pass
        except Exception as e:
            print(e)
            return
        
    path = os.path.join(os.getcwd(), "config.txt")
    if not os.path.exists(path):
        try:
            with open(path, "w") as file:
                file.write(os.getcwd())
                file.write("")
                file.write("")
                file.write("")
                file.write("")
                file.write("")
                file.write("")
        except Exception as e:
            print(e)
            return
        
def lineExists(_line):
    path = os.path.join(os.getcwd(), "scheduledPasses.txt")
    try:
        with open(path , "r") as file:
            lines = file.readlines()
            for line in lines:
                if _line in line:
                    return True
    except Exception as e:
        print(e)
    return False

def readScheduledPasses():
    path = os.path.join(os.getcwd(), "scheduledPasses.txt")
    try:
        with open(path , "r") as file:
            lines = file.readlines()
    except Exception as e:
        print(e)
    return lines
    
def updateScheduledPasses(_pass):
    path = os.path.join(os.getcwd(), "scheduledPasses.txt")
    if not lineExists(_pass):
        try:
            with open(path, "a") as file:
                file.write(_pass)
        except Exception as e:
            print(e)
            return
        
def removePreviousPasses():
    path = os.path.join(os.getcwd(), "scheduledPasses.txt")
    try:
        with open(path, "r") as file:
            lines = file.readlines()

        current_datetime = datetime.datetime.now()

        updated_lines = []
        for line in lines:
            parts = line.split("\t")
            end_datetime_str = parts[2]
            end_datetime = datetime.datetime.strptime(end_datetime_str, "%m-%d-%Y %H:%M:%S")

            if end_datetime >= current_datetime:
                updated_lines.append(line)

        with open(path, "w") as file:
            file.writelines(updated_lines)
    except Exception as e:
        print(e)
        return

def updateConfigFile(imagesPath, ip, username, password, longitude, latitude, elevation):
    path = os.path.join(os.getcwd(), "config.txt")   
    try:
        with open(path, "w") as file:
            file.write(f"{imagesPath}\n")
            file.write(f"{ip}\n")
            file.write(f"{username}\n")
            file.write(f"{password}\n")
            file.write(f"{latitude}\n")
            file.write(f"{longitude}\n")
            file.write(f"{elevation}\n")
    except Exception as e:
        print(e)

def loadConfigFile():
    path = os.path.join(os.getcwd(), "config.txt")
    try:
        with open(path, "r") as file:
            lines = file.readlines()
            if lines:
                return lines[0].strip(), lines[1].strip(), lines[2].strip(), lines[3].strip(), lines[4].strip(), lines[5].strip(), lines[6].strip()
    except Exception as e:
        print(e)
        return None
    
def checkInternetConnection():
    try:
        requests.get("http://www.google.com", timeout=5)
        return True
    except requests.ConnectionError:
        return False
