import argparse
import Pyro4
import csv
import pickle


import sys
import os
import time
import socket
import random
import pickle

import Pyro4

import json
import requests
import traceback

from Crypto.PublicKey import RSA

# SpeedCHAIN modules
from ..tools import Logger as Logger
from ..tools import CryptoFunctions

from Crypto.PublicKey import RSA

global server
global privateKey
global publicKey
global serverAESEncKey


#Functions
def defineConsensus(receivedConsensus):
    #receivedConsensus = str(input('Set a consensus (None, PBFT, PoW, dBFT or Witness3) (None is default) : '))
    # server will set its consensus and send it to all peers
    server.setConsensus(receivedConsensus)
    # print("Consensus " + receivedConsensus + " was defined")
    return True

def addBlockOnChain():
    """ Take the value of 'publicKey' var, and add it to the chain as a block"""
    global serverAESEncKey
    serverAESEncKey = server.addBlock(publicKey)
    decryptAESKey(serverAESEncKey)

def decryptAESKey(data):
    """ Receive a encrypted data, decrypt it and put it in the global var 'serverAESKey' """
    global serverAESKey
    serverAESKey = CryptoFunctions.decryptRSA2(privateKey, data)

def sendDataSC(stringSC):
    t = ((time.time() * 1000) * 1000)
    timeStr = "{:.0f}".format(t)
    data = timeStr + stringSC
    signedData = CryptoFunctions.signInfo(privateKey, data)
    #logger.debug("###Printing Signing Data before sending: "+signedData)
    # print ("###Signature lenght: " + str(len(signedData)))
    toSend = signedData + timeStr + stringSC
    encobj = CryptoFunctions.encryptAES(toSend, serverAESKey)
    server.addTransactionSC(publicKey, encobj)
    # server.addTransaction(toSend)

def createBlockForSC2(SK, PK):
    #newKeyPair()

    global privateKey
    global publicKey
    privateKey = SK
    publicKey = PK

    addBlockOnChain()
    while (not (server.isBlockInTheChain(publicKey))):
        continue
        # time.sleep(1)
    firstTransactionSC = '{ "Tipo" : "", "Data": "", "From": "", "To" : "", "Root" : "56e81f171bcc55a6ff8345e692c0f86e5b48e01b996cadc001622fb5e363b421" }'
    sendDataSC(firstTransactionSC)
    #s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def callEVMInterface(privatekey, publickey, callType, data, origin, dest):

    #callType = str(input("Type (Exec,Criar,Cham): "))
    #data = str(input("Data (binary in hexa): "))
    #origin = str(input("From account: "))
    #dest = str(input("Destination account: "))
    scInfo = callType+data+origin+dest
    signedData = CryptoFunctions.signInfo(privateKey,scInfo)
    scType = pickle.dumps(callType)
    scData = pickle.dumps(data)
    scFrom = pickle.dumps(origin)
    scDest = pickle.dumps(dest)
    scSignedData = pickle.dumps(signedData)
    scPublicKey = pickle.dumps(publicKey)
    #logger.debug("###Printing Signing Sc before sending: "+signedData)

    server.callEVM(scType,scData,scFrom,scDest,scSignedData,scPublicKey)
    #print("depois do callEVM")
    return True


def loadConnection(nameServerIP, nameServerPort, gatewayName):
    #global deviceName
    """ Load the URI of the connection  """
    # ----> Adicionado por Arruda
    ns = Pyro4.locateNS(host=nameServerIP) #, port=nameServerPort)
    gatewayURI = ns.lookup(gatewayName)
    # print(gatewayURI)
    global server
    # fname = socket.gethostname()
    # text_file = open("localhost", "r")
    # uri = text_file.read()
    # print(uri)
    server = Pyro4.Proxy(gatewayURI)
    # text_file.close()
    # os.remove(fname)
    # ---->
    defineConsensus("dBFT")
    return gatewayURI

#Loading args
argpaerser = argparse.ArgumentParser(description='Load test batch')
argpaerser.add_argument('-ip', type=str, help='Server IP', required=True)
argpaerser.add_argument('-port', type=str, help='Server Port', required=True)
argpaerser.add_argument('-gn', type=str, help='Gateway Name', required=True)
argpaerser.add_argument('-file', type=str, help='file name', required=True)
args = argpaerser.parse_args()

#Connecting to server
print ("Conectando " + args.ip + ":" + args.port )
nameServerIP = args.ip 
nameServerPort = args.port 
gatewayName = args.gn

gatewayURI = loadConnection(nameServerIP, nameServerPort, gatewayName)


#Loading csv
print ("Carregando " + args.file)

with open(args.file) as csvfile:
    reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')

    for row in reader: #Starting Batch
        time.sleep(5)
        if row['Command'] == "1":
            createBlockForSC2(row['SK'], row['PK'])
            #continue
        elif row['Command'] == "2":
            callEVMInterface(row['SK'], row['PK'], "Exec", row['Data'], row['From'], row['To'])
            #continue
        elif row['Command'] == "3":
            callEVMInterface(row['SK'], row['PK'], "Criar", row['Data'], row['From'], row['To'])
            #continue
        elif row['Command'] == "4":
            callEVMInterface(row['SK'], row['PK'], "Cham", row['Data'], row['From'], row['To'])
            #continue

#Closing
print ("Finalizando")
