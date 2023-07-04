
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
import argparse

from src.controller import Gateway

parser = argparse.ArgumentParser(description='Run the Gateway')

parser.add_argument('-n', '--nameServerIP', type=str, metavar='', help='Server IP address')
parser.add_argument('-p', '--nameServerPort', type=str, metavar='', help='Server port')
parser.add_argument('-G', '--gatewayName', type=str, metavar='', help='The name of the gateway')
parser.add_argument('-C', '--gatewayContext', type=str, metavar='', help='The context of the gateway')
parser.add_argument('-S', '--poolSize', type=str, metavar='', help='Amount of Tx from each Pool')
args = parser.parse_args()

Gateway.main(args.nameServerIP, int(args.nameServerPort), args.gatewayName, args.gatewayContext,int(args.poolSize))
