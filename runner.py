
import sys

from src.controller import Gateway

nameServerIP = sys.argv[1]
nameServerPort = int(sys.argv[2])
gatewayName = sys.argv[3]
Gateway.main(nameServerIP, nameServerPort, gatewayName)
