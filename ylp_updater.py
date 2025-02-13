import atexit
import logging
import os
import requests
import shutil
import sys

from alive_progress import alive_bar
from bs4            import BeautifulSoup
from time           import sleep


LAUNCHPAD_PATH = os.path.join(os.getenv("APPDATA"), "YimLaunchpad")
LOG_FILE = os.path.join(LAUNCHPAD_PATH, "yimlaunchpad.log")
logfile = open(LOG_FILE, "a")
logfile.write("Updating Yimlaunchpad...\n\n")
logfile.close()
log = logging.getLogger("UPDATER")
logging.basicConfig(
    filename = LOG_FILE,
    encoding = 'utf-8',
    level    = logging.DEBUG,
    format   = '%(asctime)s %(levelname)s %(name)s %(message)s',
    datefmt  = '%H:%M:%S'
)


def get_release_tag():
    try:
        r = requests.get('https://github.com/xesdoog/YimLaunchpad/tags')
        soup = BeautifulSoup(r.content, 'html.parser')
        result = soup.find(class_= 'Link--primary Link')
        s = str(result)
        result = s.replace('</a>', '')
        charLength = len(result)
        latest_version = result[charLength - 6:]
        log.info(f'Latest YimLaunchpad version: {latest_version}')
        return latest_version   
    except requests.exceptions.RequestException as e:
       print(f'Failed to get the latest Github version. Check your Internet connection and try again.\nError message: {e}')
       log.exception(f'Failed to get the latest Github version. Traceback: {e}')


REM_VER = get_release_tag()
EXE_URL = f"https://github.com/xesdoog/YimLaunchpad/releases/download/{REM_VER}/YimLaunchpad.exe"
LOCAL_EXE = "./YimLaunchpad.exe"


def banner():
 os.system("cls")
 print("            \033[1;36;40m YimLaunchpad Updater")
 print("    \033[1;32;40m https://github.com/xesdoog/YimLaunchpad\033[0m")
 print("\n\n") 


def on_success():
    log.info("Download complete.")
    input(f"\n    YimLaunchpad has been sucessfully updated to {REM_VER}. Press Enter to exit.")
    log.info(f"YimLaunchpad has been sucessfully updated! Terminating the updater and starting YimLaunchpad v{REM_VER}...\n\nFarewell!\n")
    os.execvp("./YimLaunchpad.exe", ['YimLaunchpad'])


def on_interrupt():
    if os.path.exists("./_backup"):
        if os.path.isfile("./_backup/YimLaunchpad.exe"):
            shutil.copy2("./_backup/YimLaunchpad.exe", "./")
            os.remove("./_backup/YimLaunchpad.exe")
        os.removedirs("./_backup")
    print("\n   \033[93mOperation canceled by the user. Reverting changes if any...\033[0m")
    log.warning("Operation canceled by the user. Reverting changes if any...\n")


def on_exit():
    log.info("Farewell!\n")


def updater():
    banner()
    try:
        if os.path.isfile("./YimLaunchpad.exe"):
            log.info("Found YimLaunchpad executable")
            if not os.path.exists("./_backup"):
                os.makedirs("./_backup")
                log.info("Creating backup folder...")
            try:
                shutil.copy2("./YimLaunchpad.exe", "./_backup")
                log.info("Moving old YimLaunchpad version into backup folder...")
                with requests.get(EXE_URL, stream = True) as r:
                    r.raise_for_status()
                    total_size = int(r.headers.get("content-length", 0))
                    log.info(f'Starting download...')
                    log.info(f'Total size: {"{:.2f}".format(total_size/1048576)}MB')
                    with open(LOCAL_EXE, "wb") as f:
                        with alive_bar(total_size) as bar:
                            for chunk in r.iter_content(128000):
                                f.write(chunk)
                                bar()
                print("")
            except requests.exceptions.RequestException as e:
                print(f"    \033[91mFailed to download YimLaunchpad. Check your Internet connection and try again.\nError message: {e}\033[0m")
                shutil.copy2("./_backup/YimLaunchpad.exe", "./")
                sys.exit(0)
            try:
                os.remove("./_backup/YimLaunchpad.exe")
                os.removedirs("./_backup")
            except OSError:
                pass
            on_success()
        else:
            print("    \033[91m'YimLaunchpad.exe' not found! Aborting operation in a few seconds...\033[0m")
            log.error("'YimLaunchpad.exe' not found! Aborting operation in a few seconds...")
            sleep(3)
            sys.exit(0)
    except KeyboardInterrupt:
        on_interrupt()


atexit.register(on_exit)

if __name__ == "__main__":
    updater()
