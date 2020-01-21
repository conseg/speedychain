"""
import io
import time

import Pyro4
import Pyro4.naming
import subprocess
from .src.controller import Gateway
from threading import Thread
import Pyro4.naming

import sys

from .src.controller import Gateway


def runGateway(nameServerIP, nameServerPort, gatewayName):
    Gateway.main(nameServerIP, nameServerPort, gatewayName)

def runPyro4(nameServerIP, nameServerPort):
    Pyro4.naming.startNSloop(nameServerIP, nameServerPort)

def runPyro(nameServerIP, nameServerPort):
    pyro = Thread(target=runPyro4, args=(nameServerIP, nameServerPort)).start()
"""
import sys

from src.controller import Gateway

nameServerIP = sys.argv[1]
nameServerPort = int(sys.argv[2])
gatewayName = sys.argv[3]
gatewayContext = sys.argv[4]
Gateway.main(nameServerIP, nameServerPort, gatewayName, gatewayContext)