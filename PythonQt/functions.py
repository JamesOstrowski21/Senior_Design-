from ftplib import FTP
import os

def ftp_connect(host, user, passwd, filepath, folder):
    ftp = FTP(host)
    ftp.login(user, passwd)
    ftp.cwd(filepath)
    fileList = ftp.nlst()
    # localpath = os.path.join(os.getcwd(), folder, filename)
    os.makedirs(os.path.join(os.getcwd(),"images", folder), exist_ok=True)

    for filename in fileList:
        if filename.endswith(".png"):
            print(filename)
            localpath = os.path.join(os.getcwd(), "images", folder, filename)

            if not os.path.exists(localpath):
                with open(localpath , "wb") as file:
                    ftp.retrbinary("RETR " + filename, file.write)

    ftp.quit()