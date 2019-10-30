"""
This is an example of an App runner file, in order to use the SpeedyChain API
Just follow these 5 simple steps to start using it

1-Import the API runner, we made this to keep everything simple.
2-Import the Python Thread.
3-Once all imports are done, setup a device name for you, as well as a gateway, port and IP
4-Run the blockchain in a separated thread (call a separated function that calls the runner.run) passing along your info
5-Connect and run your device! (If you need, we have an example code.)

Be Aware: Your runner python file must be located at the root of your App folder/package
"""
import time

from API import runner

from App import DeviceSimulator
from threading import Thread


nameServerIP = "127.0.0.1"
nameServerPort = 9090
gatewayName = "gwa"
deviceName = "dev-a"


def runBlockchain(nameServerIP, nameServerPort, gatewayName):
    runner.run(nameServerIP, nameServerPort, gatewayName)

def runDevice(nameServerIP, nameServerPort, gatewayName, dev):
    DeviceSimulator.connectDeviceAndRun(nameServerIP, nameServerPort, gatewayName, dev)

block = Thread(target=runBlockchain,args=(nameServerIP, nameServerPort, gatewayName)).start()
time.sleep(2)
runDevice(nameServerIP, nameServerPort, gatewayName, deviceName)
