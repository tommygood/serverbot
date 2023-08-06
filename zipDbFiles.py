import subprocess
from subprocess import call, PIPE, run
import datetime, requests, config
from datetime import datetime as dt

# current directory
directory = "/home/tommygood/serverbot/"

# db directory
db_directory = directory + "db"

# backup directory, make sure this directory exist
backup_directory = directory + "db_backups/"

# record the monitor result in log
log_path = directory + "monitor.log"

# chat id
chat_id = config.tg

# bot
bot_token = config.BotAPIKey

def main() :
    result = str(compressFile())
    logResult(result)
    sendTelegram(result) # send to telegram chat room

def sendTelegram(result) :
    send_msg_url = f"https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&text={result}"
    res = requests.get(send_msg_url) # this sends the message

# create new db directory
def createNewDb() :
    result = run(["mkdir", db_directory], stdout=PIPE, stderr=PIPE, universal_newlines=True)
    print(result)
    result = run(["touch", db_directory + "/db.log"], stdout=PIPE, stderr=PIPE, universal_newlines=True)
    print(result)
    result = run(["touch", db_directory + "/dockerContainer.dat"], stdout=PIPE, stderr=PIPE, universal_newlines=True)
    print(result)
    with open(db_directory + "/dockerContainer.dat", 'w') as file:
        file.write("[]")
    file.close()

# compress the .wpress file
def compressFile() :
    file_path = db_directory
    tar_path = backup_directory + str(dt.now().date()) + ".tar.gz"
    # compress file to tar file
    result = run(["tar", "zcvf", tar_path, "-C", file_path, "."], stdout=PIPE, stderr=PIPE, universal_newlines=True)
    result= str(result)
    # compress failed
    if not ("CompletedProcess" in result and "stderr=''" in result) :
        print("Compress failed")
        print(result)
    # compress successfully, remove the original file
    else :
        result = run(["rm", "-r", file_path], stdout=PIPE, stderr=PIPE, universal_newlines=True)
        print("Compress successfully")
        print(result)
        createNewDb() # create new db directory
    return result

def logResult(result) :
    # record the odd directory
    text_file = open(log_path, "a")
    # write into log
    text_file.write(str(datetime.datetime.now()) + " " + result + "\n")
    text_file.close()

main()
