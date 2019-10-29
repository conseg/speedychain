import io
import time

import Pyro4
import Pyro4.naming
import subprocess
from .src.controller import Gateway
from threading import Thread
import Pyro4.naming

def run(nameServerIP, nameServerPort, gatewayName):
    pyro = Thread(target=runPyro4, args=(nameServerIP, nameServerPort)).start()
    time.sleep(1)
    runGateway(nameServerIP, nameServerPort, gatewayName)

def runGateway(nameServerIP, nameServerPort, gatewayName):
    Gateway.main(nameServerIP, nameServerPort, gatewayName)

def runPyro4(nameServerIP, nameServerPort):
    Pyro4.naming.startNSloop(nameServerIP, nameServerPort)
    #subprocess.call(["bash -c \'python -m Pyro4.naming -n 127.0.0.1 -p 9090; exec bash\'"], shell=True)