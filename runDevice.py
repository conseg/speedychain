import sys
from App import DeviceSimulator

def runDevice(nameServerIP, nameServerPort, gatewayName, dev):
    DeviceSimulator.connectDeviceAndRun(nameServerIP, nameServerPort, gatewayName, dev)

nameServerIP = sys.argv[1]
nameServerPort = sys.argv[2]
gatewayName = sys.argv[3]
deviceName = sys.argv[4]
runDevice(nameServerIP, int(nameServerPort), gatewayName, deviceName)