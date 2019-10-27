#import __builtin__

import cv2
import numpy as np
import threading
import base64
import hashlib
import subprocess

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
import Logger as Logger
import CryptoFunctions

##########################################################################
FILE_OUTPUT = './out/output.avi'

# Checks and deletes the output file
# You cant have a existing file or it will through an error
if os.path.isfile(FILE_OUTPUT):
    os.remove(FILE_OUTPUT)

# Playing video from file:
# cap = cv2.VideoCapture('vtest.avi')
# Capturing video from webcam:
#cap = cv2.VideoCapture(0)
cap = cv2.VideoCapture('http://129.94.175.139:5000/video_feed')
currentFrame = 0

outputFile = None
lock = threading.Lock()
out = None

def newVideo():
    global cap, out, cv2
    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)   # float
    print("Video width ="+str(width))
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT) # float
    print("Video height ="+str(height))
    fourcc=cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(FILE_OUTPUT, fourcc, 20.0, (int(width),int(height)))
##########################################################################


logger = Logger.logging.getLogger("speedychain")
deviceName = ""
consensus = ""

fname = socket.gethostname()

server = "localhost"
serverAESEncKey = ""
serverAESKey = ""
privateKey = "-----BEGIN PRIVATE KEY-----\nMIIBVAIBADANBgkqhkiG9w0BAQEFAASCAT4wggE6AgEAAkEA7P6DKm54NjLE7ajy\nTks298FEJeHJNxGT+7DjbTQgJdZKjQ6X9lYW8ittiMnvds6qDL95eYFgZCvO22YT\nd1vU1QIDAQABAkBEzTajEOMRSPfmzw9ZL3jLwG3aWYwi0pWVkirUPze+A8MTp1Gj\njaGgR3sPinZ3EqtiTA+PveMQqBsCv0rKA8NZAiEA/swxaCp2TnJ4zDHyUTipvJH2\nqe+KTPBHMvOAX5zLNNcCIQDuHM/gISL2hF2FZHBBMT0kGFOCcWBW1FMbsUqtWcpi\nMwIhAM5s0a5JkHV3qkQMRvvkgydBvevpJEu28ofl3OAZYEwbAiBJHKmrfSE6Jlx8\n5+Eb8119psaFiAB3yMwX9bEjVy2wRwIgd5X3n2wD8tQXcq1T6S9nr1U1dmTz7407\n1UbKzu4J8GQ=\n-----END PRIVATE KEY-----\n"
publicKey = "-----BEGIN PUBLIC KEY-----\nMFwwDQYJKoZIhvcNAQEBBQADSwAwSAJBAOz+gypueDYyxO2o8k5LNvfBRCXhyTcR\nk/uw4200ICXWSo0Ol/ZWFvIrbYjJ73bOqgy/eXmBYGQrzttmE3db1NUCAwEAAQ==\n-----END PUBLIC KEY-----\n"

# input = getattr(__builtin__, 'raw_input', input)

def getMyIP():
     """ Return the IP from the gateway
     @return str 
     """
     s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
     s.connect(("8.8.8.8", 80))
     myIP = s.getsockname()[0]
     s.close()
     return myIP

def generateRSAKeyPair():
    """ Creates a pair of RSA key, one public and one private.\n
        @return pub - public key\n
        @return prv - private key
    """
    #randValue = Random.random.randrange(24)
    private = RSA.generate(1024)

    #private = RSA.generate(1024,randValue)
    pubKey = private.publickey()
    prv = private.exportKey()
    pub = pubKey.exportKey()
    return pub, prv

def setServer():
    """ Ask for the user to input the server URI and put it in the global var 'server' """
    global server
    #server = raw_input('Gateway IP:')
    uri = input("Enter the uri of the gateway: ").strip()
    server = Pyro4.Proxy(uri)

def addBlockOnChain():
    """ Take the value of 'publicKey' var, and add it to the chain as a block"""
    global serverAESEncKey
    # print("###addBlockonChain in devicesimulator, publicKey")
    print(publicKey)
    serverAESEncKey = server.addBlock(publicKey)
    # print("###addBlockonChain in devicesimulator, serverAESEncKey")
    # print(serverAESEncKey)
    # while len(serverAESEncKey) < 10:
    #    serverAESEncKey = server.addBlock(publicKey)
    decryptAESKey(serverAESEncKey)
    # print("###after decrypt aes")

def sendDataTest():
    """ Send fake data to test the system """
    pub, priv = generateRSAKeyPair()
    temperature = readSensorTemperature()
    t = ((time.time() * 1000) * 1000)
    timeStr = "{:.0f}".format(t)
    data = timeStr + temperature
    signedData = CryptoFunctions.signInfo(priv, data)
    ver = CryptoFunctions.signVerify(data, signedData, pub)
    logger.debug("Sending data test " + str(ver) + "...")
    # print ("done: "+str(ver))

def sendData():
    """ Read the sensor data, encrypt it and send it as a transaction to be validated by the peers """
    temperature = readSensorTemperature()
    t = ((time.time() * 1000) * 1000)
    timeStr = "{:.0f}".format(t)
    data = timeStr + temperature
    logger.debug("data = "+data)
    signedData = CryptoFunctions.signInfo(privateKey, data)
    toSend = signedData + timeStr + temperature
    logger.debug("ServeAESKEY = " + serverAESKey)
    encobj = CryptoFunctions.encryptAES(toSend, serverAESKey)
    server.addTransaction(publicKey, encobj)

def sendDataSC(stringSC):
    t = ((time.time() * 1000) * 1000)
    timeStr = "{:.0f}".format(t)
    data = timeStr + stringSC
    signedData = CryptoFunctions.signInfo(privateKey, data)
    logger.debug("###Printing Signing Data before sending: "+signedData)
    # print ("###Signature lenght: " + str(len(signedData)))
    toSend = signedData + timeStr + stringSC
    encobj = CryptoFunctions.encryptAES(toSend, serverAESKey)
    server.addTransactionSC(publicKey, encobj)
    # server.addTransaction(toSend)

def decryptAESKey(data):
    """ Receive a encrypted data, decrypt it and put it in the global var 'serverAESKey' """
    global serverAESKey
    serverAESKey = CryptoFunctions.decryptRSA2(privateKey, data)

def readSensorTemperature():
    """ Generates random data like '23 C' """
    temp = str(random.randint(10, 40)) + " C"
    return temp

def addPeer():
    """ Ask for the user to inform a peer URI and add it to the server """
    # if sys.version_info < (3, 0):
    #     input = raw_input
    uri = input("Enter the PEER uri: ").strip()
    server.addPeer(uri, True)

def listBlockHeader():
    """ Log all blocks """
    server.showIoTLedger()

def listTransactions():
    """ Ask for the user to input an index and show all transaction of the block with that index """
    index = input("Which IoT Block do you want to print?")
    server.showBlockLedger(int(index))


def listPeers():
    """ List all peers in the network """
    logger.debug("calling server...")
    server.listPeer()

def newKeyPair():
    """ Generates a new pair of keys and put is on global vars 'privateKey' and 'publicKey' """
    global privateKey
    global publicKey
    publicKey, privateKey = generateRSAKeyPair()
    while len(publicKey) < 10 or len(privateKey) < 10:
        publicKey, privateKey = generateRSAKeyPair()

def brutePairAuth(retry):
    """ Add a block on the chain with brute force until it's add"""
    isOk = True
    while isOk:
        try:
            newKeyPair()
            addBlockOnChain()
            isOk = False
        except KeyboardInterrupt:
            sys.exit()
        except:
            logger.error("failed to execute:"+str(retry))
            isOk = True

def bruteSend(retry):
    """ Try to send a random data with brute force until it's sended """
    isOk = True
    while isOk:
        try:
            sendData()
            isOk = False
        except KeyboardInterrupt:
            sys.exit()
        except:
            logger.error("failed to execute:"+str(retry))
            exc_type, exc_value, exc_traceback = sys.exc_info()
            logger.error("*** print_exception:\n" + str(traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)))
            #global serverAESKey
            # print("the size of the serverAESKey is: "+str(len(serverAESKey)))
            return  # addBlockConsensusCandiate

def defineAutomaNumbers():
    """ Ask for the user to input how many blocks and transaction he wants and calls the function automa()"""
    blocks = int(input('How many Blocks:'))
    trans = int(input('How many Transactions:'))
    automa(blocks, trans)

def automa(blocks, trans):
    """ Adds a specifc number of blocks and transaction to the chain\n
        @param blocks - int number of blocks\n
        @param trans - int number of transactions
    """
    for blk in range(0, blocks):
        logger.info("Adding block #" + str(blk) + "...")
        newKeyPair()
        addBlockOnChain()
        # brutePairAuth(blk)
        for tr in range(0, trans):
            logger.info("Sending transaction #" + str(tr) + "...")
            # sendData()
            while (not (server.isBlockInTheChain(publicKey))):
                continue
                # time.sleep(1)
            bruteSend(tr)

def merkle():
    """ Calculates the hash markle tree of the block """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    blk = int(input("Which block you want to create the merkle tree:"))
    server.calcMerkleTree(blk)  # addBlockConsensusCandiate
    # print ("done")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def newElection():
    server.electNewOrchestrator()
    return True
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) ###WHAT???###

def defineInteractiveConsensus():
    receivedConsensus = str(input('Set a consensus (None, PBFT, PoW, dBFT or Witness3) (None is default) : '))
    print("after receiving consensus string: "+receivedConsensus)
    print(server)
    server.setConsensus(receivedConsensus)
    return True

def defineConsensus(receivedConsensus):
    #receivedConsensus = str(input('Set a consensus (None, PBFT, PoW, dBFT or Witness3) (None is default) : '))
    # server will set its consensus and send it to all peers
    server.setConsensus(receivedConsensus)
    # print("Consensus " + receivedConsensus + " was defined")
    return True

def createBlockForSC():
    newKeyPair()
    addBlockOnChain()
    while (not (server.isBlockInTheChain(publicKey))):
        continue
        # time.sleep(1)
    firstTransactionSC = '{ "Tipo" : "", "Data": "", "From": "", "To" : "", "Root" : "56e81f171bcc55a6ff8345e692c0f86e5b48e01b996cadc001622fb5e363b421" }'
    sendDataSC(firstTransactionSC)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def showLastTransactionData():
    blockIndex = int(input('Type the index to show the last transaction data: '))
    lastDataTransactionData = server.showLastTransactionData(blockIndex)
    return lastDataTransactionData

def callEVMInterface():
    return True


def evmConnector():
    return True


def executeEVM():
    return True

def saveStream():
    global cap, outputFile, lock, out
    currentFrame = 0
    newKeyPair()
    addBlockOnChain()  
    newVideo()
    i=0
    while True:
        ret, frame = cap.read()
        #printInfo(cap)
        if ret == True:
            # Handles the mirroring of the current frame
            #frame = cv2.flip(frame,1)
            # Saves for video
            out.write(frame)
            # Display the resulting frame
            #cv2.imshow('frame',frame)
            currentFrame += 1
            print(str(currentFrame))
            if(currentFrame >= 40):
                i = i +1
                out.release()
                ipfsName=sentToIPFS()             
                s = makeTransaction(ipfsName)
                saveFile(i,s, ipfsName)
                currentFrame = 0
                newVideo()


def sha256_checksum(filename, block_size=65536):
    sha256 = hashlib.sha256()
    with open(filename, 'rb') as f:
        for block in iter(lambda: f.read(block_size), b''):
            sha256.update(block)
    return sha256.hexdigest()


#Generate  a new transaction for blockchain
def makeTransaction(ipfsName):
    sha256 = sha256_checksum("./out/output.avi")
    print(str(sha256))    
    sendMetadataTransactions(sha256, ipfsName)
    return sha256

def sendMetadataTransactions(fileHash, ipfsName):
    t = ((time.time() * 1000) * 1000)
    timeStr = "{:.0f}".format(t)
    data = timeStr + str(fileHash) + ipfsName

    signedData = CryptoFunctions.signInfo(privateKey, data)
    toSend = signedData + timeStr + str(fileHash) + ipfsName
    #logger.debug("ServeAESKEY = " + serverAESKey)
    encobj = CryptoFunctions.encryptAES(toSend, serverAESKey)
    server.addTransaction(publicKey, encobj)
    ##################################DEBUG ONLY
    # toSend = signedData + timeStr + str(fileHash)+ipfsName
    # f = open("./"+str(fileHash),"w+")
    # f.write(str(toSend))
    # signature = toSend[:-126]     
    # devTime = toSend[-126:-110]    
    # deviceData = toSend[-110:-46] #file Hash
    # ipfs= toSend[-46:]
    # f.write("\n")
    # f.write("\n")
    # f.write("Signature="+str(signature))
    # f.write("\n")
    # f.write("devTime="+str(devTime))
    # f.write("\n")
    # f.write("fileshash="+str(deviceData))
    # f.write("\n")
    # f.write("ipfs="+str(ipfs))    
    # f.close()

def sentToIPFS():
    cmdIPFS = "ipfs add ./out/output.avi"
    ret = subprocess.Popen(cmdIPFS, shell=True, stdout=subprocess.PIPE).stdout.read()
    fileNameIPFS = ret[6:52]
    #fileOriginalName = ret[53:]
    return fileNameIPFS

#Create a bkp
def saveFile(i, shaFileValue, ipfsAdd):
    os.rename("./out/output.avi", "../x/output"+str(i)+".avi")
    f = open("../x/output"+str(i)+".sha256","w+")
    f.write(str(shaFileValue))
    f.write("\n")
    f.write(str(ipfsAdd))
    f.close()

    

def loadConnection(nameServerIP, nameServerPort, gatewayName):
    global deviceName
    """ Load the URI of the connection  """
    # ----> Adicionado por Arruda
    ns = Pyro4.locateNS(host=nameServerIP, port=nameServerPort)
    gatewayURI = ns.lookup(gatewayName)
    print(gatewayURI)
    global server
    # fname = socket.gethostname()
    # text_file = open("localhost", "r")
    # uri = text_file.read()
    # print(uri)
    server = Pyro4.Proxy(gatewayURI)
    print("asdf")
    # text_file.close()
    # os.remove(fname)
    # ---->
    #defineConsensus(consensus)
    return gatewayURI

#############################################################################
#############################################################################
######################          Main         ################################
#############################################################################
#############################################################################
def InteractiveMain():
    """ Creates an interactive screen for the user with all option of a device"""
    print("InteractiveMain")
    global server
    options = {
        1: setServer,
        2: addPeer,
        3: addBlockOnChain,
        4: sendData,
        5: listBlockHeader,
        6: listTransactions,
        7: listPeers,
        8: newKeyPair,
        9: defineAutomaNumbers,
        10: merkle,
        11: newElection,
        12: defineInteractiveConsensus,
        13: createBlockForSC,
        14: showLastTransactionData,
        15: callEVMInterface,
        16: evmConnector,
        17: executeEVM,
        18: saveStream
    }

    mode = -1
    while True:
        print("Choose your option [" + str(server) + "]")
        print("0 - Exit")
        print("1 - Set Server Address[ex:PYRO:chain.server@blablabala:00000]")
        print("2 - Add Peer")
        print(
            "3 - Authentication Request [a)Gw Generate AES Key;b)Enc key with RSA;c)Dec AES Key]")
        print(
            "4 - Produce Data [a)sign data;b)encrypt with AES key;c)Send to Gateway;d)GW update ledger and peers")
        print("5 - List Block Headers from connected Gateway")
        print("6 - List Transactions for a given Block Header")
        print("7 - List PEERS")
        print("8 - Recreate Device KeyPair")
        print("9 - Run a batch operation...")
        print("10 - Create Merkle Tree for a given block")
        print(
            "11 - Elect a new node as Orchestator (used for voting based consensus")
        print("12 - Set a consensus algorithm")
        print("13 - Create a block for Smart Contract")
        print("14 - Show data from last transaction from block Index")
        print("15 - Call Smart Contract")
        # print("16 - EVM connector")
        # print("17 - execute EVM code")
        print("18 - Run Save Stream Handler ")

        try:
            mode = int(input('Input:'))
        except ValueError:
            print ("Not a number")
        if (mode == 0):
            break
        options[mode]()

if __name__ == '__main__':

    # if len(sys.argv[1:]) > 1:
        # ----> Adicionado por Arruda
        # print ("Command Line usage:")
        # print (
        #     "    python deviceSimulator.py <name server IP> <gateway name> <blocks> <transactions>")
        # ---->
        # os.system("clear")
        # print("running automatically")
    if len(sys.argv[1:])<4:
        print("Command line syntax:")
        print("  python DeviceSimulator.py <name server IP> <name server port> <gateway name> <device name>")
        #saveStream()
    else:
        nameServerIP = sys.argv[1]
        nameServerPort = int(sys.argv[2])
        gatewayName = sys.argv[3]
        deviceName = sys.argv[4]
        logger = Logger.configure(deviceName + ".log")
        logger.info("Running device " + deviceName + " in " + getMyIP())

        gatewayURI = loadConnection(nameServerIP, nameServerPort, gatewayName)

        logger.info("Connected to gateway: " + gatewayURI.asString())

        if (len(sys.argv) < 6): #when it is not called with number of blocks/transactions and consensus, it is called interactive mode
            print("Setting consensus and showing menu")
            #server.setConsensus("None")
            InteractiveMain()
        else:
            print(" nothing to do")
            blocks = sys.argv[5]
            transactions = sys.argv[6]
            #consensus = sys.argv[7]
            #saveStream()
            #logger.info("Processing " + blocks + " blocks and " + transactions + " transactions...")
            #automa(int(blocks), int(transactions))

            #t = threading.Thread(target=detect_motion, args=(args["frame_count"],))
            # t = threading.Thread(target=saveStream)
            # t.daemon = True
            # t.start()
            

        # else:
        # os.system("clear")
        # loadConnection()
        # main()
