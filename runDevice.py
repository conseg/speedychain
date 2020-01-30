import sys
import argparse
from App import DeviceSimulator

def runDevice(nameServerIP, nameServerPort, gatewayName, dev):
    DeviceSimulator.connectDeviceAndRun(nameServerIP, nameServerPort, gatewayName, dev)


parser = argparse.ArgumentParser(description='Connect and run the device')

parser.add_argument('-n', '--nameServerIP', type=str, metavar='', help='Server IP address')
parser.add_argument('-p', '--nameServerPort', type=str, metavar='', help='Server port')
parser.add_argument('-G', '--gatewayName', type=str, metavar='', help='The name of the gateway')
parser.add_argument('-D', '--deviceName', type=str, metavar='', help='The name of the device connecting')
args = parser.parse_args()

#nameServerIP = sys.argv[1]
#nameServerPort = sys.argv[2]
#gatewayName = sys.argv[3]
#deviceName = sys.argv[4]

runDevice(args.nameServerIP, int(args.nameServerPort), args.gatewayName, args.deviceName)