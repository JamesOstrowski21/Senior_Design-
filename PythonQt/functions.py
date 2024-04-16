from ftplib import FTP
import os

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

def updateConfigFile(imagesPath, ip, username, password):
    path = os.path.join(os.getcwd(), "config.txt")
    try:
        with open(path, "w") as file:
            file.write(f"{imagesPath}\n")
            file.write(f"{ip}\n")
            file.write(f"{username}\n")
            file.write(f"{password}\n")
    except Exception as e:
        print(e)

def loadConfigFile():
    path = os.path.join(os.getcwd(), "config.txt")
    try:
        with open(path, "r") as file:
            lines = file.readlines()
            if lines:
                return lines[0].strip(), lines[1].strip(), lines[2].strip(), lines[3].strip()
    except Exception as e:
        print(e)
        return None
