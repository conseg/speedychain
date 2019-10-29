import sys
import os
import errno

import logging
from logging.handlers import RotatingFileHandler
try:
    import colorlog
    HAVE_COLORLOG = True
except ImportError:
    HAVE_COLORLOG = False

def configure(filename):
    """ Setup the logging environment """
    log = logging.getLogger("speedychain")
    log.setLevel(logging.INFO)
    # logging in file
    # Dev local
    # logFolder = os.path.join(os.getcwd(), "log")
    logFolder = "/var/log"
    if not os.path.exists(logFolder):
        try:
            os.makedirs(logFolder)
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise
    fileHandler = ""
    try:
        fileHandler = RotatingFileHandler(filename = os.path.join(logFolder, filename), maxBytes = 1 * 1024 * 1024, backupCount = 5)
    except IOError as err:
        fileHandler = RotatingFileHandler(filename = os.path.join(".", filename), maxBytes = 1 * 1024 * 1024, backupCount = 5)    
    fileHandler.setLevel(logging.INFO)
    formatStr = "%(asctime)s;%(levelname)-8s;%(message)s;"
    dateFormat = "%Y-%m-%d %H:%M:%S"
    fileFormatter = logging.Formatter(formatStr, dateFormat)
    fileHandler.setFormatter(fileFormatter)
    log.addHandler(fileHandler)
    # logging in std output
    if HAVE_COLORLOG and os.isatty(2):
        cformat = "%(log_color)s" + formatStr
        colors = {"DEBUG": "reset",
                  "INFO": "reset",
                  "WARNING": "bold_yellow",
                  "ERROR": "bold_red",
                  "CRITICAL": "bold_red"}
        consoleFormatter = colorlog.ColoredFormatter(cformat, dateFormat, log_colors=colors)
    else:
        consoleFormatter = logging.Formatter(formatStr, dateFormat)
    streamHandler = logging.StreamHandler(sys.stdout)
    streamHandler.setLevel(logging.INFO)
    streamHandler.setFormatter(consoleFormatter)
    log.addHandler(streamHandler)
    return log
