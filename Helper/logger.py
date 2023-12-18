import logging
import sys
import os

from datetime import date

today = date.today()
logName = today.strftime("%d-%m-%Y")
logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")

logger = logging.getLogger("main_app")
logger.setLevel(logging.DEBUG)


logger_file_path = os.path.join(os.getenv('LOCALAPPDATA'), "MAOS", "log")

if not os.path.exists(logger_file_path):
    os.mkdir(logger_file_path)

fileHandler = logging.FileHandler(f"{logger_file_path}/{logName}.log")
fileHandler.setFormatter(logFormatter)
fileHandler.setLevel(logging.DEBUG)
logger.addHandler(fileHandler)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
fileHandler.setLevel(logging.DEBUG)
logger.addHandler(consoleHandler)

