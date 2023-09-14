from serverCode import app as app
from serverCode import writeLog,closeLog
import os
import io
import time



configfname="serverconfig.txt"
configs={}

def readConfig():
    f=open(configfname,"r")
    all=f.readlines()
    for el in all:
        el=el.strip()
        ##    # character is for commenting
        if el[0] != "#":
            arr=el.split(":")
            configs[arr[0].strip()]=arr[1].strip()
    f.close()

if __name__ == '__main__':
    try:    
        from os.path import exists
        file_exists = exists(configfname)
        if not file_exists:
            print(configfname," does not exist")
            quit()
        readConfig()
        if configs.get("LOGFILE",None) is not None:
            log_file_name=configs["LOGFILE"]

        if configs.get("SIMPLE",None) == "True":
            print("Simple one")
            #app.run(ssl_context=('../cert.pem', '../key.pem'),host="0.0.0.0", port=5000)
            app.run(host="0.0.0.0", port=5000)
        else:
            from waitress import serve
            with app.app_context():
                serve(app,host="0.0.0.0",port=5000,connection_limit=200,threads=8,cleanup_interval=90,url_scheme='https')
                # if you are not using HTTPS support remove the field url_scheme from the above
    except KeyboardInterrupt:
        print("Exited")
        writeLog("Flask Exited because of keyboard Interrupt")

    closeLog()
