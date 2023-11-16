import sys
import os
from os import listdir
from os.path import isfile, join
import time
import threading
from threading import Thread
import pickle
import socket
#import for python 3 or above
#import _thread as thread
#import for python 2
import thread
import random
import json
import Queue

from flask import Flask, request

import Pyro4
import merkle

# SpeedCHAIN modules
from ..model.Chain import ChainFunctions
from ..model.Chain import ChainFunctionsMulti
from ..model.Peer import PeerInfo
from ..model.Transaction import Transaction
from ..model.Transaction import LifecycleEvent
from ..tools import CryptoFunctions
from ..tools import DeviceInfo
from ..tools import DeviceKeyMapping
from ..tools import Logger


def getMyIP():
    """ Return the IP from the gateway
    @return str
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("10.255.255.255", 1))
        myIP = s.getsockname()[0]
    except:
        myIP = '127.0.0.1'
    finally:
        s.close()
        # hostname = socket.gethostname()
        # IPAddr = socket.gethostbyname(hostname)
        # myIP = IPAddr

    return myIP


def getTime():
    """ Return the current time
    @return str
    """
    return time.time()

blkCounter = 0 # blkCounter is used to choose blk context

logT3 = [] # time to insert a block in local chain (block ledger)
logT5 = []
logT6 = []
logT20 = [] # time/latency to insert a transaction (from creation on device to insertion in the gw BC)
logT21 = [] # time to insert a set of transactions in local chain (time to process/insert a list of Tr
logT22 = [] # time to perform transaction concensus, transations per transaction consensus, and throuput per transaction consensus
logT23 = []  # time to validate a candidate list and vote
logT24 = []  # time to original/proposer of tx consensus to validate txdata
logT25 = []  # time to insert transaction in the pool
logT26 = []  # time/latency to insert a transaction in the First Gw(from creation on device to insertion in the gw BC)
# logT29 =[]
lock = thread.allocate_lock()
transListLock  = thread.allocate_lock()
consensusLock = thread.allocate_lock()
blockConsensusCandidateList = []

# Enable/Disable the transaction validation when peer receives a transaction
validatorClient = True

myName = socket.gethostname()

app = Flask(__name__)
peers = []

genKeysPars = []
myURI = ""
gwPvt = ""
gwPub = ""
myOwnBlock = ""
orchestratorObject = ""
consensus = "PBFT"  # it can be None, dBFT, PBFT, PoW, PoA, Witness3
nameServerIP =""
nameServerPort=""
# list of votes for new orchestrator votes are: voter gwPub, voted gwPub, signature
votesForNewOrchestrator = []
myVoteForNewOrchestrator = []  # my gwPub, voted gwPub, my signed vote

# transactionTime will store the time that a transaction was inserted in local BC
# transaction time is { dataSign : timestamp}
# transactionsTime = {}
contextPeers = []
# contextPeers = [["0001",[]]]
# context peers is [[context, [peers]], [context2, [peers]], [context3, [peers]]]
transactionConsensusCandidateList =[]
transactionLockList = []
contextLockList =[]
transactionSharedPool = []
# transactionSharedPool could be understood as = [["0001", [(devKey1, tr1),(devKey2,tr2]],["0002",[]]]
# i.e., print transactionSharedPool[0] is ["0001,  [(devKey1, tr1),(devKey2,tr2]]
# i.e., print transactionSharedPool[0][1] is (devKey1,tr1), (devKey2, tr2)
# i.e., print transactionSharedPool[0][1][1] is (devKey2, tr2)
# i.e., transactionSharedPool[0][1].append((devKey3,tr3)) results in:
# [["0001", [(devKey1, tr1),(devKey2,tr2], (devKey3,tr3)],["0002",[]]]
blockContext = "0001"
# should have all context here
# 
gwContextConsensus = [("0001", "PoA"),("0002", "PoA"),("0003", "PoA")]
sizePool = 100
# list of votes for new orchestrator votes are: context, voter gwPub, voted gwPub, signature
votesForNewContextOrchestrator =[]
myVoteForNewContextOrchestrator =[]

# should have all context here
orchestratorContextObject = []
# [["0001", ""], ["0002", ""]]
# transactionSharedPool could be understood as = [["0001", gwOrchestratorObj],["0002", gwOrchestratorObj]]

componentsId = []
components = ["CPU", "RAM", "SSD", "VID"]
chainFile = "chain.txt"
chainFileMulti = "chainmulti.txt"
deviceName = "dev-"

# example from: www.stackoverflow.com/questions/6893968/how-to-get-the-return-value-from-a-thread-in-pyhton
class ThreadWithReturn(Thread):
    def __init__(self, group=None, target=None, name=None, args=(), kwargs={}, Verbose=None):
        Thread.__init__(self, group, target, name, args,kwargs, Verbose)
        self._return = None
    def run(self):
        if self._Thread__target is not None:
            self._return = self._Thread__target(*self._Thread__args, **self._Thread__kwargs)
    def join(self):
        Thread.join(self)
        return self._return


# my_queue = Queue.Queue()
#
# def storeInQueue(f):
#     def wrapper(*args):
#         my_queue.put(f(*args))
#     return wrapper

def bootstrapChain2():
    """ generate the RSA key pair for the gateway and create the chain"""
    global gwPub
    global gwPvt
    ChainFunctions.startBlockChain()
    ChainFunctionsMulti.startBlockChain()
    gwPub, gwPvt = CryptoFunctions.generateRSAKeyPair()

#############################################################################
#############################################################################
#########################    PEER MANAGEMENT  ###############################
#############################################################################
#############################################################################


def findPeer(peerURI):
    """ Receive the peer URI generated automatically by pyro4 and verify if it on the network\n
        @param peerURI URI from the peer wanted\n
        @return True - peer found\n
        @return False - peer not found
    """
    global peers
    for p in peers:
        if p.peerURI == peerURI:
            return True
    return False


def getPeer(peerURI):
    """ Receive the peer URI generated automatically by pyro4 and return the peer object\n
        @param peerURI URI from the peer wanted\n
        @return p - peer object \n
        @return False - peer not found
    """
    global peers
    for p in peers:
        if p.peerURI == peerURI:
            return p
    return False


def addBack(peer, isFirst):
    """ Receive a peer object add it to a list of peers.\n
        the var isFirst is used to ensure that the peer will only be added once.\n
        @param peer - peer object\n
        @param isFirst - Boolean condition to add only one time a peer
    """
    global myURI
    global blockContext
    if(isFirst):
        obj = peer.object
        obj.addPeer(myURI, isFirst, gwContextConsensus)
        # pickedUri = pickle.dumps(myURI)
        # print("Before gettin last chain blocks")
        # print("Picked URI in addback: " + str(pickedUri))
        # obj.getLastChainBlocks(pickedUri, 0)
    # else:
    #    print ("done adding....")


def sendTransactionToPeers(devPublicKey, transaction):
    """ Send a transaction received to all peers connected.\n
        @param devPublickey - public key from the sending device\n
        @param transaction - info to be add to a block
    """
    global peers
    for peer in peers:
        obj = peer.object
        # logger.debug("Sending transaction to peer " + peer.peerURI)
        trans = pickle.dumps(transaction)
        res = obj.updateBlockLedger(devPublicKey, trans)
        # print ("sendTransactionToPeers res = "+res)
        # transaction.__class__ = Transaction.Transaction
        # candidateDevInfo = transaction.data
        # candidateDevInfo.__class__ = DeviceInfo.DeviceInfo
        # t = ((time.time() * 1000) * 1000)
        # print(t)
        # t2 = "{:.0f}".format(((time.time() * 1000) * 1000))
        # print(t2)
        # print(str(candidateDevInfo))
        # print(candidateDevInfo)
        # print(candidateDevInfo.timestamp)
        # originalTimestamp = float(candidateDevInfo.timestamp)

        # currentTimestamp = float(((time.time()) * 1000) * 1000)
        # logT20.append("gateway;" + gatewayName + ";T20;Transaction Latency;" + str(
        #     (currentTimestamp - originalTimestamp) / 1000))


# class sendBlks(threading.Thread):
#     def __init__(self, threadID, iotBlock):
#         threading.Thread.__init__(self)
#         self.threadID = threadID
#         self.iotBlock = iotBlock
#
#     def run(self):
#         print "Starting "
#         # Get lock to synchronize threads
#         global peers
#         for peer in peers:
#             print ("runnin in a thread: ")
#             obj = peer.object
#             # logger.debug("sending IoT Block to: " + peer.peerURI)
#             dat = pickle.dumps(self.iotBlock)
#             obj.updateIOTBlockLedger(dat)


def sendBlockToPeers(IoTBlock):
    """
    Receive a block and send it to all peers connected.\n
    @param IoTBlock - BlockHeader object
    """
    global peers
    # print("sending block to peers")
    # logger.debug("Running through peers")
    for peer in peers:
        # print ("Inside for in peers")
        obj = peer.object
        # print("sending IoT Block to: " + str(peer.peerURI))
        # logger.debug("Sending block to peer " + str(peer.peerURI))
        dat = pickle.dumps(IoTBlock)
        obj.updateIOTBlockLedger(dat, myName)
    # print("block sent to all peers")


def syncChain(newPeer):
    """
    Send the actual chain to a new peer\n
    @param newPeer - peer object

    TODO update this pydoc after write this method code
    """
    # write the code to identify only a change in the iot block and insert.
    return True


def connectToPeers(nameServer):
    """this method recieves a nameServer parameter, list all remote objects connected to it, and
    add these remote objetcts as peers to the current node \n
    @param nameServer - list all remote objects connected to it
    """
    # print ("found # results:"+str(len(nameServer.list())))
    for peerName in nameServer.list():
        if(peerName != gatewayName and peerName != "Pyro.NameServer"):
            # print ("adding new peer:"+peerURI)
            peerURI = nameServer.lookup(peerName)
            addPeer2(peerURI)
            # addPeersToContextPeers()
            # orchestratorObject
        # else:
            # print ("nothing to do")
            # print (peerURI )
    # print ("finished connecting to all peers")


def addPeersToContextPeers():
    global peers
    global contextPeers

    for p in peers:
        print("running add peer in addPeer in contextPeers")
        obj = p.object
        print("After creating obj in ADDpeer")
        newPeerContext = obj.getRemoteContext()
        print("after getting remote context")
        foundContextPeer = False
        for index in range(len(contextPeers)):
            if (contextPeers[index][0] == newPeerContext):
                print("Context found: " + newPeerContext)
                contextPeers[index][1].append(p)
                print("Peer added to context Peer"+str(contextPeers))
                foundContextPeer = True
        if(foundContextPeer==False):
            print("did not find context in contextPeers, creating and appending")
            contextPeers.append([newPeerContext, [p]])
            print("CONTEXT and PEER added to context Peer"+str(contextPeers))

    return


def addPeer2(peerURI):
    """ Receive a peerURI and add the peer to the network if it is not already in\n
        @param peerURI - peer id on the network\n
        @return True - peer added to the network\n
        @return False - peer already in the network
    """
    global peers
    global contextPeers

    if not (findPeer(peerURI)):
        # print ("peer not found. Create new node and add to list")
        # print ("[addPeer2]adding new peer:" + peerURI)
        newPeer = PeerInfo.PeerInfo(peerURI, Pyro4.Proxy(peerURI))
        peers.append(newPeer)
        # print("Runnin addback...")
        # print("running add peer in addPeer2 in contextPeers")
        obj = newPeer.object
        # print("After creating obj in ADDpeer2")
        # newPeerContext = obj.getRemoteContext()
        newPeerContext = obj.getRemoteContexts()
        # print("after getting remote context")
        for x,y in newPeerContext:
            foundContextPeer = False
            for index in range(len(contextPeers)):
                if (contextPeers[index][0] == x):
                    print("Context found: " + x)
                    contextPeers[index][1].append(newPeer)
                    print("Peer added2 to context Peer" + str(contextPeers))
                    foundContextPeer = True
            if (foundContextPeer == False):
                # print("2did not find context in contextPeers, creating and appending")
                contextPeers.append([x, [newPeer]])
                print("2CONTEXT and PEER added to context Peer" + str(contextPeers))
        # foundContextPeer = False
        # for index in range(len(contextPeers)):
        #     if (contextPeers[index][0] == newPeerContext):
        #         print("Context found: " + newPeerContext)
        #         contextPeers[index][1].append(newPeer)
        #         print("Peer added2 to context Peer" + str(contextPeers))
        #         foundContextPeer = True
        # if (foundContextPeer == False):
        #     # print("2did not find context in contextPeers, creating and appending")
        #     contextPeers.append([newPeerContext, [newPeer]])
        #     print("2CONTEXT and PEER added to context Peer" + str(contextPeers))


        addBack(newPeer, True)
        # syncChain(newPeer)
        # print ("finished addback...")
        return True
    return False

#############################################################################
#############################################################################
#########################    CRIPTOGRAPHY    ################################
#############################################################################
#############################################################################


def generateAESKey(devPubKey):
    """ Receive a public key and generate a private key to it with AES 256\n
        @param devPubKey - device public key\n
        @return randomAESKey - private key linked to the device public key
    """
    global genKeysPars
    randomAESKey = os.urandom(32)  # AES key: 256 bits
    obj = DeviceKeyMapping.DeviceKeyMapping(devPubKey, randomAESKey)
    genKeysPars.append(obj)
    return randomAESKey


def findAESKey(devPubKey):
    """ Receive the public key from a device and found the private key linked to it\n
        @param devPubKey - device public key\n
        @return AESkey - found the key\n
        @return False - public key not found
    """
    global genKeysPars
    for b in genKeysPars:
        if (b.publicKey == devPubKey):
            return b.AESKey
    return False


def removeAESKey(AESKey):
    """ Receive the public key from a device and found the private key linked to it\n
        @param devPubKey - device public key\n
        @return AESkey - found the key\n
        @return False - public key not found
    """
    global genKeysPars
    for b in genKeysPars:
        if (b.AESKey == AESKey):
            logger.error("****************************************")
            logger.error("****************************************")
            logger.error("removing AES Key")
            genKeysPars.remove(b)
            logger.error("****************************************")
            logger.error("****************************************")
    return False

#############################################################################
#############################################################################
#################    Consensus Algorithm Methods    #########################
#############################################################################
#############################################################################


answers = {}
trustedPeers = []


def addTrustedPeers():
    """ Run on the peers list and add all to a list called trustedPeers """
    global peers
    for p in peers:
        trustedPeers.append(p.peerURI)

# Consensus PoW
# TODO -> should create a nonce in the block and in the transaction in order to generate it
# we could add also a signature set (at least 5 as ethereum or 8 as bitcoin?) to do before send the block for update
# peers should verify both block data, hash, timestamp, etc and the signatures, very similar to what is done by verifyBlockCandidate
# maybe this verifications could be put in a another method... maybe something called " verifyBlockData "
# END NEW CONSENSUS @Roben
##########################


def peerIsTrusted(i):
    global trustedPeers
    for p in trustedPeers:
        if p == i:
            return True
    return False


def peerIsActive(i):
    return True  # TO DO


def sendBlockToConsensus(newBlock, gatewayPublicKey, devicePublicKey):
    obj = peer.object
    data = pickle.dumps(newBlock)
    obj.isValidBlock(data, gatewayPublicKey, devicePublicKey)


def receiveBlockConsensus(self, data, gatewayPublicKey, devicePublicKey, consensus):
    newBlock = pickle.loads(data)
    answer[newBlock].append(consensus)


def isValidBlock(self, data, gatewayPublicKey, devicePublicKey, peer):
    newBlock = pickle.loads(data)
    blockIoT = ChainFunctions.findBlock(devicePublicKey)
    consensus = True
    if blockIoT == False:
        # print("Block not found in IoT ledger")
        consensus = False

    lastBlock = blockIoT.blockLedger[len(blockIoT.blockLedger) - 1]
    if newBlock.index != lastBlock.index + 1:
        # print("New blovk Index not valid")
        consensus = False

    if lastBlock.calculateHashForBlockLedger(lastBlock) != newBlock.previousHash:
        # print("New block previous hash not valid")
        consensus = False

    now = "{:.0f}".format(((time.time() * 1000) * 1000))

    # check time
    if not (newBlock.timestamp > newBlock.signature.timestamp and newBlock.timestamp < now):
        # print("New block time not valid")
        consensus = False

    # check device time
    if not (newBlock.signature.timestamp > lastBlock.signature.timestamp and newBlock.signature.timestamp < now):
        # print("New block device time not valid")
        consensus = False

    # check device signature with device public key
    if not (CryptoFunctions.signVerify(newBlock.signature.data, newBlock.signature.deviceSignature, gatewayPublicKey)):
        # print("New block device signature not valid")
        consensus = False
    peer = getPeer(peer)
    obj = peer.object
    obj.receiveBlockConsensus(data, gatewayPublicKey,
                              devicePublicKey, consensus)


def isTransactionValid(transaction, pubKey):
    #data = str(transaction.data)[-22:-2]
    data, signature = transaction.getDataAndSignatureInsideLifecycle()
    #signature = str(transaction.data)[:-22]
    res = CryptoFunctions.signVerify(data, signature, pubKey)
    return res

def isBlockValid(block):
    # Todo Fix the comparison between the hashes... for now is just a mater to simulate the time spend calculating the hashes...
    # global BlockHeaderChain
    # print(str(len(BlockHeaderChain)))
    lastBlk = ChainFunctions.getLatestBlock()
    # print("Index:"+str(lastBlk.index)+" prevHash:"+str(lastBlk.previousHash)+ " time:"+str(lastBlk.timestamp)+ " pubKey:")
    # lastBlkHash = CryptoFunctions.calculateHash(lastBlk)

    lastBlkHash = CryptoFunctions.calculateHash(lastBlk.index, lastBlk.previousHash, lastBlk.timestamp, 
                        lastBlk.nonce, lastBlk.publicKey, lastBlk.blockContext, lastBlk.device)

    # print ("This Hash:"+str(lastBlkHash))
    # print ("Last Hash:"+str(block.previousHash))
    if(lastBlkHash == block.previousHash):
        # logger.info("isBlockValid == true")
        return True
    else:
        logger.error("isBlockValid == false")
        logger.error("lastBlkHash = " + str(lastBlkHash))
        logger.error("block.previous = " + str(block.previousHash))
        logger.error("lastBlk Index = " + str(lastBlk.index))
        logger.error("block.index = " + str(block.index))
        # return False
        return True

#############################################################################
#############################################################################
######################      R2AC Class    ###################################
#############################################################################
#############################################################################


@Pyro4.expose
@Pyro4.behavior(instance_mode="single")
class R2ac(object):
    def __init__(self):
        """ Init the R2AC chain on the peer"""
        logger.info("SpeedyCHAIN Gateway initialized")
        # thread to perform transaction consensus
        # time.sleep(5)

    def startTransactionsConsThreads(self):
        for x,y in gwContextConsensus:
            threading.Thread(target=self.threadTransactionConsensus, args=(x,y)).start()
            # if (gwContextConsensus[0]) [("0001", "PoA"),("0002", "PBFT")]

    def threadTransactionConsensus(self, context, consensus):
        # a sleep time to give time to all gateways connect and etc
        # time.sleep(5)
        # the other sleep times in this method is due to bad parallelism of Python... without any sleep, this thread can leave others in starvation
        if(consensus=="PoA"):
            while (True):
                self.performTransactionPoolPoAConsensus(context)
                time.sleep(0.5)
        if(consensus=="PBFT"):
            # while(True):
                for index in range(len(orchestratorContextObject)):
                    if (orchestratorContextObject[index][0] == context and orchestratorContextObject[index][1].exposedURI() == myURI):
                        self.performTransactionPoolPBFTConsensus(context)
                        # time.sleep(0.02)
                    # else:
                # time.sleep(0.1)

        if (consensus == "dBFT"):
            while (True):
                for index in range(len(orchestratorContextObject)):
                    if (orchestratorContextObject[index][0] == context and orchestratorContextObject[index][1].exposedURI() == myURI):
                        self.performTransactionPooldBFTConsensus(context)
                        # time.sleep(0.01)
                    # else:
                    time.sleep(0.1)
                # print("PBFT for transactions not implemented yet")

    #  it should verify context
    def performTransactionConsensus(self):
        # print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")

        candidateTransaction = self.getTransactionFromSyncList(blockContext)
        # print(candidateTransaction)
        if(candidateTransaction != False):
            # print("AAAAAAAAAAAAAAAA passed the if")
            devPublicKey = candidateTransaction[0]
            deviceInfo= candidateTransaction[1]
            context = candidateTransaction[2]
            blk = ChainFunctions.findBlock(devPublicKey)
            # print("passed the blk")
            nextInt = blk.transactions[len(
                blk.transactions) - 1].index + 1
            signData = CryptoFunctions.signInfo(gwPvt, str(deviceInfo))
            # print("BBBBBBBBBBBBB passed the devinfo")
            gwTime = "{:.0f}".format(((time.time() * 1000) * 1000))
            # code responsible to create the hash between Info nodes.
            prevInfoHash = CryptoFunctions.calculateTransactionHash(
                ChainFunctions.getLatestBlockTransaction(blk))

            transaction = Transaction.Transaction(
                nextInt, prevInfoHash, gwTime, deviceInfo, signData, 0)

            ChainFunctions.addBlockTransaction(blk, transaction)
            # logger.debug("Block #" + str(blk.index) + " added locally")
            # logger.debug("Sending block #" +
            #             str(blk.index) + " to peers...")

            # --->> this function should be run in a different thread.
            sendTransactionToPeers(devPublicKey, transaction)
        return

    def performTransactionPoolPBFTConsensus(self,context):
        global contextPeers
        global logT22
        global sizePool
        candidatePool =[]
        # sizePool = 30 # slice of transactions get from each pool
        minInterval = 10 # interval between consensus in ms
        minTransactions = 0 # minimum number of transactions to start consensus


        # for index in range(len(orchestratorContextObject)):
        #     # print("*** obj " + str(orchestratorContextObject[index][1]) + " my pyro " + str(Pyro4.Proxy(myURI)))
        #     # print("obj URI: " + str(orchestratorContextObject[index][1].exposedURI()) + "myURI " + str(myURI))
        #     # orchestratorContextObject[index][1].exposedURI()
        #     if (orchestratorContextObject[index][0] == context and orchestratorContextObject[index][1].exposedURI() == myURI):
        # print("******************I Am the PBFT Leader of context: "+context)
        while(len(candidatePool)==0):
            tcc1 = ((time.time()) * 1000) * 1000
            # just to not printing in every time that enters here, leave it only for interactive

            while(self.addContextinLockList(context)==False):
                # logger.error("I AM NOT WITH LOCK!!!!!")
                time.sleep(0.001)
            tempContextPeers = []
            for x in range(len(contextPeers)):
                # print(" ***VVVVV **** context? " +contextPeers[x][0])
                if (contextPeers[x][0] == context):
                    tempContextPeers = contextPeers[x][1]
            # use this if you want to get all elements from trpool
            # pickedCandidatePool = self.getLocalTransactionPool(context)
            # use this if you want to get first sizePool elements
            pickedCandidatePool = self.getNElementsLocalTransactionPool(context,sizePool)
            myPool = pickle.loads(pickedCandidatePool)
            if (myPool != False):
                candidatePool = myPool
                # print("I got my pool in PBFT")

            for p in tempContextPeers:
                peer = p.object
                while(peer.addContextinLockList(context)==False):
                    time.sleep(0.001)
                # pickedRemotePool = peer.getLocalTransactionPool(context)
                pickedRemotePool = peer.getNElementsLocalTransactionPool(context,sizePool)
                remoteCandidatePool = pickle.loads(pickedRemotePool)

                if(remoteCandidatePool!=False):
                    # .extend append each from another list
                    candidatePool.extend(remoteCandidatePool)
                    # while(len(remoteCandidatePool)>0):
                    #     # cant just append the remoteCandidatePool, should add each tuple
                    #     remoteTR = remoteCandidatePool.pop(0)
                    #     candidatePool.append((remoteTR[0],remoteTR[1]))

                    # candidatePool.append(remoteCandidatePool)
            candidatePoolSize = len(candidatePool)
            if (candidatePoolSize!=0):
                # logger.info("**************Inside PBFT Transaction ***************")
                self.prepareContextPBFT(context,candidatePool,tempContextPeers)

                # if you want to set a min interval between consensus
                tcc2 = ((time.time()) * 1000) * 1000

                # te2 = ((time.time()) * 1000) * 1000
                # logger.error("ELECTION; " + str((te2-te1)/1000))
                self.removeLockfromContext(context)
                for p in tempContextPeers:
                    peer = p.object
                    peer.removeLockfromContext(context)

                # if ((tcc2 - tcc1) / 1000 < minInterval):
                #     time.sleep((minInterval - ((tcc2 - tcc1) / 1000)) / 1000)
                # election for new orchestrator
                self.electNewContextOrchestrator(context)
                # orchestratorContextObject.performTransactionPoolPBFTConsensus(context)
                tcc2 = ((time.time()) * 1000) * 1000
                logT22.append("T22 CONTEXT; "+context+";PBFT CONSENSUS TIME; " + str((tcc2-tcc1)/1000) + "; SIZE; "+str(candidatePoolSize) + ";TPUT;" + str((candidatePoolSize)/(((tcc2-tcc1)/1000)/1000)))
                # call to execute the consensus for the new leader
                for index in range(len(orchestratorContextObject)):
                    if (orchestratorContextObject[index][0] == context):
                        threading.Thread(target=orchestratorContextObject[index][1].performTransactionPoolPBFTConsensus, args=[context]).start()
                # logger.error("CONTEXT "+context+" PBFT CONSENSUS; " + str((tcc2-tcc1)/1000) + "; SIZE; "+str(candidatePoolSize))
                return

            else:
                self.removeLockfromContext(context)
                for p in tempContextPeers:
                    peer = p.object
                    peer.removeLockfromContext(context)
                tcc2 = ((time.time()) * 1000) * 1000
                if((tcc2 - tcc1) / 1000 < minInterval):
                    time.sleep((minInterval - ((tcc2 - tcc1) / 1000)) / 1000)
                    # print("****** sleeping " + str((minInterval - ((tcc2 - tcc1) / 1000)) / 1000) + "ms")


    def performTransactionPooldBFTConsensus(self, context):
        global contextPeers
        candidatePool = []
        index = 0
        sizePool = 70  # slice of transactions get from each pool
        minInterval = 0  # interval between consensus in ms
        minTransactions = 0  # minimum number of transactions to start consensus

        #     if (orchestratorContextObject[index][0] == context and orchestratorContextObject[index][1].exposedURI() == myURI):
        # print("******************I Am the orchestrator leader dBFT")


        tcc1 = ((time.time()) * 1000) * 1000
        # just to not printing in every time that enters here, leave it only for interactive
        while (self.addContextinLockList(context) == False):
            # logger.error("I AM NOT WITH LOCK!!!!!")
            time.sleep(0.001)
        # use this if you want to get all elements from trpool
        # pickedCandidatePool = self.getLocalTransactionPool(context)
        # use this if you want to get first sizePool elements
        pickedCandidatePool = self.getNElementsLocalTransactionPool(context, sizePool)
        myPool = pickle.loads(pickedCandidatePool)
        if (myPool != False):
            # print("******************I Am the dBFT Leader of context: " + context)
            candidatePool = myPool
            # print("I got my pool in PBFT")
        tempContextPeers = []
        for x in range(len(contextPeers)):
            # print(" ***VVVVV **** context? " +contextPeers[x][0])
            if (contextPeers[x][0] == context):
                tempContextPeers = contextPeers[x][1]
        for p in tempContextPeers:
            peer = p.object
            while (peer.addContextinLockList(context) == False):
                time.sleep(0.001)
            # pickedRemotePool = peer.getLocalTransactionPool(context)
            pickedRemotePool = peer.getNElementsLocalTransactionPool(context, sizePool)
            remoteCandidatePool = pickle.loads(pickedRemotePool)

            if (remoteCandidatePool != False):
                # .extend append each from another list
                candidatePool.extend(remoteCandidatePool)
        candidatePoolSize = len(candidatePool)
        if (candidatePoolSize != 0):
            # print("**************Inside PBFT Transaction ***************")
            self.prepareContextPBFT(context, candidatePool, tempContextPeers)

            # if you want to set a min interval between consensus
            tcc2 = ((time.time()) * 1000) * 1000
            if ((tcc2 - tcc1) / 1000 < minInterval):
                time.sleep((minInterval - ((tcc2 - tcc1) / 1000)) / 1000)
                # print("****** sleeping " + str((minInterval - ((tcc2 - tcc1) / 1000)) / 1000) + "ms")

            # dBFT does not have election
            # self.electNewContextOrchestrator(context)
            self.removeLockfromContext(context)
            for p in tempContextPeers:
                peer = p.object
                peer.removeLockfromContext(context)
            tcc2 = ((time.time()) * 1000) * 1000
            logT22.append(
                "T22 CONTEXT; " + context + ";dBFT CONSENSUS TIME; " + str((tcc2 - tcc1) / 1000) + "; SIZE; " + str(
                    candidatePoolSize) + ";TPUT;" + str((candidatePoolSize) / (((tcc2 - tcc1) / 1000) / 1000)))
            # logger.error("CONTEXT "+context+" dBFT CONSENSUS; " + str((tcc2-tcc1)/1000) + "; SIZE; "+str(candidatePoolSize))
            return

        else:
            self.removeLockfromContext(context)
            for p in tempContextPeers:
                peer = p.object
                peer.removeLockfromContext(context)
            tcc2 = ((time.time()) * 1000) * 1000
            if ((tcc2 - tcc1) / 1000 < minInterval):
                time.sleep((minInterval - ((tcc2 - tcc1) / 1000))/1000)
                # print("****** sleeping "+str((minInterval - ((tcc2 - tcc1) / 1000))/1000) +"ms")



    def prepareContextPBFT(self, context, candidatePool, alivePeers):
        """ Send a new candidatePool for all the available peers on the network\n
            @param newBlock - BlockHeader object\n
            @param generatorGwPub - Public key from the peer who want to generate the block\n
            @param generatorDevicePub - Public key from the device who want to generate the block\n
        """
        # logger.error("-----------------------------inside prepare")
        candidateTransactionPool =[]
        votesPoolTotal = []
        validTransactionPool =[]

        while (len(candidatePool) > 0):
            # logger.error("-----------------------------inside prepare--while")
            candidateTransaction = candidatePool.pop(0)
            # print("popped element from Pool")
            # print(candidateTransaction)
            if (candidateTransaction != False):
                # logger.error("-----------------------------inside prepare--notfalse candidate")
                # print("AAAAAAAAAAAAAAAA passed the if")
                devPublicKey = candidateTransaction[0]
                deviceInfo = candidateTransaction[1]
                if(ChainFunctions.findBlock(devPublicKey)!=False):
                    blk = ChainFunctions.findBlock(devPublicKey)
                # print("passed the blk")
                    nextInt = blk.transactions[len(blk.transactions) - 1].index + 1
                    signData = CryptoFunctions.signInfo(gwPvt, str(deviceInfo))
                    # print("BBBBBBBBBBBBB passed the devinfo")
                    gwTime = "{:.0f}".format(((time.time() * 1000) * 1000))
                    # code responsible to create the hash between Info nodes.
                    prevInfoHash = CryptoFunctions.calculateTransactionHash(ChainFunctions.getLatestBlockTransaction(blk))
                    transaction = Transaction.Transaction(nextInt, prevInfoHash, gwTime, deviceInfo, signData, 0)
                    candidateTransactionPool.append((devPublicKey, transaction))
                    # logger.error("-----------------------------inside prepare--transaction appended")
                    trSign = CryptoFunctions.signInfo(gwPvt,str(transaction))
                    # votesPoolTotal.append([(devPublicKey, transaction), [trSign]])
                    votesPoolTotal.append([(devPublicKey, transaction), ["valid"]])
        if(len(candidateTransactionPool)==0):
            logger.error("!!!!!!! All tr were invalid or no tr at all")
            return

        dumpedPool = pickle.dumps(candidateTransactionPool)

        arrayPeersThreads = []
        # counter =0
        dumpedGwPub = pickle.dumps(gwPub)
        for p in alivePeers:
            # default type of thread that accepts return value in the join
            arrayPeersThreads.append(ThreadWithReturn(target=self.startRemoteVoting, args=(context, dumpedPool, dumpedGwPub, p)))
            # arrayPeersThreads.append(threading.Thread(target=self.startRemoteVoting, args=(context,dumpedPool,dumpedGwPub,p)))
            # start the last inserted thread in array
            arrayPeersThreads[-1].start()
            # counter = counter+1


        # logger.error("after start")
        for i in range(len(arrayPeersThreads)):

            # default class of thread used to have a return on join
            pickedVotes, pickedVotesSignature, remoteGwPk = arrayPeersThreads[i].join()
            # arrayPeersThreads[i].join()
            # logger.error("after join")

            # will get from a queue of returns (from votes)
            # pickedVotes, pickedVotesSignature, remoteGwPk = my_queue.get()

            # logger.error("got stuff")
            # pickedVotes, pickedVotesSignature, remoteGwPk = p.object.votePoolCandidate(context, dumpedPool, dumpedGwPub)
            votes = pickle.loads(pickedVotes)
            votesSignature = pickle.loads(pickedVotesSignature)
            # verify if list of votes are valid, i.e., peer signature in votes is correct
            if(CryptoFunctions.signVerify(str(votes),votesSignature, p.object.getGwPubkey())):
                # logger.error("!!***!!!!*** Votes Signature is valid****")
                for index in range(len(votes)):
                    # if there is a vote
                    if(votes[index][1]=="valid"):
                        # append a new vote
                        votesPoolTotal[index][1].append(votes[index][1])
                        # verify if it get the minimun number of votes
                        if (len(votesPoolTotal[index][1]) > ((2 / 3) * len(alivePeers))):
                            # verify if it was not already inserted
                            if(not(votesPoolTotal[index][0] in validTransactionPool)):
                                # insert in validated pool
                                validTransactionPool.append(votesPoolTotal[index][0])
                if (len(validTransactionPool)==len(votesPoolTotal)):
                    # logger.error("YES... breaked... reduced the time ;)")
                    break
            # get every return from the method votePoolCandidate called by each thread and count votes after joins


        # for v in range(len(votesPoolTotal)):
        #     if (len(votesPoolTotal[v][1]) > ((2 / 3) * len(alivePeers))):
        #         # logger.error("APPENDED in final pool")
        #         validTransactionPool.append(votesPoolTotal[v][0])

        # commit

        # TODO define how to update peers: all peers or only participating in consensus?
        #
        if(self.commitContextPBFT(validTransactionPool,alivePeers)):
        # if (self.commitContextPBFT(validTransactionPool, peers)):
            return True

        return False

    def commitContextPBFT(self, validTransactionPool, alivePeers):
        arrayPeersThreads = [] * len(alivePeers)

        if(len(validTransactionPool)>0):
            dumpedSetTrans = pickle.dumps(validTransactionPool)
            # addLocally
            self.updateBlockLedgerSetTrans(dumpedSetTrans,True)

            # add remote
            index = 0
            for p in alivePeers:

                obj=p.object
                # obj.updateBlockLedgerSetTrans(dumpedSetTrans,False)
                arrayPeersThreads.append(threading.Thread(target=obj.updateBlockLedgerSetTrans, args=(dumpedSetTrans,False)))
                arrayPeersThreads[index].start()
                index = index+1

            # this can be a problem for performance... trying
            # for i in range(len(arrayPeersThreads)):
            #     arrayPeersThreads[i].join()

            # logger.error("!!!! PASSED !!!")
            return True
        logger.error("!!!! Failed to commit transactions !!!")
        return False

    # @storeInQueue
    def startRemoteVoting(self, context, dumpedPool, dumpedGwPub, p):
        pickedVotes, pickedVotesSignature, remoteGwPk = p.object.votePoolCandidate(context, dumpedPool, dumpedGwPub)
        return pickedVotes, pickedVotesSignature, remoteGwPk


    def votePoolCandidate(self, context, candidatePool, pickedGwPub):
        """ Checks whether the new block has the following characteristics: \n
            * The hash of the previous block are correct in the new block data\n
            * The new block index is equals to the previous block index plus one\n
            * The generation time of the last block is smaller than the new one \n
            If the new block have it all, sign it with the peer private key\n
            @return False - The block does not have one or more of the previous characteristics\n
            @return votesPool, signature and GwPub - return a list of votes (valid), signature and gwpub
        """
        global logT23
        t1 = (time.time()*1000)
        validation = True
        votesPool =[]
        receivedPool = pickle.loads(candidatePool)
        receivedGwPub = pickle.loads(pickedGwPub)
        while(len(receivedPool) > 0):
            candidate = receivedPool.pop(0)
            receivedDevPub = candidate[0]
            candidateTr = candidate[1]
            candidateTr.__class__ = Transaction.Transaction

            # verify if device is registered and if the index and timestamp are correct
            if (ChainFunctions.findBlock(receivedDevPub) != False):
                blk = ChainFunctions.findBlock(receivedDevPub)
                # print("passed the blk")
                lastTrIndex = blk.transactions[len(blk.transactions) - 1].index
                lastTimestamp = blk.transactions[len(blk.transactions) - 1].timestamp
                if(lastTrIndex >= candidateTr.index or lastTimestamp >= candidateTr.timestamp ):
                    logger.error("***********************")
                    logger.error("***Invalid Tr time or index*")
                    logger.error("***********************")
                    validation = False

                # verify the gw of the device
                candidateDevInfo = candidateTr.data
                candidateDevInfo.__class__ = DeviceInfo.DeviceInfo
                verifyGwSign = CryptoFunctions.signVerify(str(candidateDevInfo), candidateTr.signature, receivedGwPub)
                if (verifyGwSign != True):
                    logger.error("***********************")
                    logger.error("***Invalid Gw Signature*")
                    logger.error("***********************")
                    validation = False

                # verify the signature of the device
                d = candidateDevInfo.timestamp + candidateDevInfo.data

                isSigned = CryptoFunctions.signVerify(d, candidateDevInfo.deviceSignature, receivedDevPub)
                if (isSigned != True):
                    logger.error("***********************")
                    logger.error("***Invalid Device Signature*")
                    logger.error("***********************")
                    validation = False
                # after verifications...

                # first Tr is a dummy generated data
                if(len(blk.transactions)-1 > 0):
                    lastTrDevInfo = blk.transactions[len(blk.transactions) - 1].data
                    lastTrDevInfo.__class__ = DeviceInfo.DeviceInfo

                    if(lastTrDevInfo.timestamp >= candidateDevInfo.timestamp):
                        logger.error("***********************")
                        logger.error("***Invalid device info time*")
                        logger.error("***********************")
                        validation = False

            else:
                logger.error("***********************")
                logger.error("***Invalid PubKey -> it is not in BC*")
                logger.error("***********************")
                validation = False


            if(validation==True):
                # trSign = CryptoFunctions.signInfo(gwPvt, str(candidateTr))
                # votesPool.append([(receivedDevPub, candidateTr), trSign])
                # send only de candidate Tr signature
                votesPool.append([(candidateTr.signature), "valid"])
            # if it is not valid, do not vote as valid
            else:
                votesPool.append([(candidateTr.signature), ""])
            validation = True
        votesSignature=CryptoFunctions.signInfo(gwPvt, str(votesPool))
        t2 = (time.time()*1000)
        logT23.append("T23 VOTING;CONTEXT "+context+";VOTING TIME; " + str(t2-t1))
        # logger.error("!!!!! My verification sign = " + str(CryptoFunctions.signVerify(str(votesPool),votesSignature,gwPub)))
        # logger.error("My signature is: " + votesSignature + "my votespool is: " + str(votesPool) + "my pub is" + gwPub)
        return pickle.dumps(votesPool), pickle.dumps(votesSignature), gwPub


    def performTransactionPoolPoAConsensus(self, context):
        # print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
        global contextPeers

        sizePool = 100  # slice of transactions get from each pool
        minInterval = 1  # interval between consensus in ms
        # global blockContext

        candidatePool = []


        # candidatePool = self.getLocalTransactionPool(context)
        # while (self.addContextinLockList(context) == False):
        #     # logger.error("I AM NOT WITH LOCK!!!!!")
        #     time.sleep(0.001)
        # use this if you want to get all elements from trpool
        # pickedCandidatePool = self.getLocalTransactionPool(context)
        # use this if you want to get first sizePool elements
        # logger.error("INSIDE I am the leader of Context: "+ str(context))
        # time.sleep(0.5)
        # time.sleep(0.1)
        # logger.error("Doing consensus Context")

        tempContextPeers = []

        for x in range(len(contextPeers)):
            # print(" ***VVVVV **** context? " +contextPeers[x][0])
            if (contextPeers[x][0] == context):
                tempContextPeers = contextPeers[x][1]

        candidatePooltoSend = []
        # logger.error("tamanho da pool: "+str(len(candidatePool)))
        # if(len(candidatePool) > 0):
            # logger.error("tamanho da pool: "+str(len(candidatePool)))
        if(self.lockForContextConsensus(context) != False):
            tcc1 = ((time.time()) * 1000) * 1000

            pickedCandidatePool = self.getNElementsLocalTransactionPool(context, sizePool)
            # self.removeLockfromContext(context)

            receivedCandidate = pickle.loads(pickedCandidatePool)
            if (receivedCandidate != False):
                # print("******************I Am the PoA Leader of context: " + context)
                candidatePool.extend(receivedCandidate)
            while(len(candidatePool)>0):
                candidateTransaction = candidatePool.pop(0)
               # print("popped element from Pool")
                # print(candidateTransaction)
                if(candidateTransaction != False):
                    # print("AAAAAAAAAAAAAAAA passed the if")
                    devPublicKey = candidateTransaction[0]
                    deviceInfo= candidateTransaction[1]
                    blk = ChainFunctions.findBlock(devPublicKey)
                    # print("passed the blk")
                    nextInt = blk.transactions[len(
                        blk.transactions) - 1].index + 1
                    signData = CryptoFunctions.signInfo(gwPvt, str(deviceInfo))
                    # print("BBBBBBBBBBBBB passed the devinfo")
                    gwTime = "{:.0f}".format(((time.time() * 1000) * 1000))
                    # code responsible to create the hash between Info nodes.
                    prevInfoHash = CryptoFunctions.calculateTransactionHash(
                        ChainFunctions.getLatestBlockTransaction(blk))

                    transaction = Transaction.Transaction(
                        nextInt, prevInfoHash, gwTime, deviceInfo, signData, 0)

                    ChainFunctions.addBlockTransaction(blk, transaction)
                    candidateDevInfo = deviceInfo
                    candidateDevInfo.__class__ = DeviceInfo.DeviceInfo
                    originalTimestamp = float(candidateDevInfo.timestamp)
                    currentTimestamp = float(((time.time()) * 1000) * 1000)
                    # logger.debug("Block #" + str(blk.index) + " added locally")
                    # logger.debug("Sending block #" +
                    #             str(blk.index) + " to peers...")
                    logT26.append("gateway;" + gatewayName + ";Context;" + blk.blockContext + ";T26;First Transaction Latency;" + str((currentTimestamp - originalTimestamp) / 1000))
                    # --->> this function should be run in a different thread.
                    candidatePooltoSend.append((devPublicKey, transaction))
                    # instead of sending transactions individually, it will be sent in batch
                    # sendTransactionToPeers(devPublicKey, transaction)

            if(len(candidatePooltoSend)>0):
                # print("BBBBB: "+str(candidatePooltoSend))
                # context = blockContext
                dumpedSetTrans = pickle.dumps(candidatePooltoSend)
                for index in range(len(contextPeers)):
                    if(contextPeers[index][0] == context):
                        for p in contextPeers[index][1]:
                            obj=p.object
                            obj.updateBlockLedgerSetTrans(dumpedSetTrans,False)

                tcc2 = ((time.time()) * 1000) * 1000
                logT22.append(
                    "T22 CONTEXT; " + context + ";PoA CONSENSUS TIME; " + str((tcc2 - tcc1) / 1000) + "; SIZE; " + str(
                        len(candidatePooltoSend)) + ";TPUT;" + str(
                        len((candidatePooltoSend)) / (((tcc2 - tcc1) / 1000) / 1000)))

                if ((tcc2 - tcc1) / 1000 < minInterval):
                    time.sleep((minInterval - ((tcc2 - tcc1) / 1000)) / 1000)
                    # print("****** sleeping PoA " + str((minInterval - ((tcc2 - tcc1) / 1000)) / 1000) + "ms")

            self.removeLockfromContext(context)
            for p in tempContextPeers:
                peer = p.object
                peer.removeLockfromContext(context)
        # ts1 = time.time()
        # self.selectCircularLeader(context,tempContextPeers)
        # ts2 = time.time()
        # logger.error("circular time: " + str(ts2-ts1))
        time.sleep(0.01)
        return

    def selectCircularLeader(self,context,tempContextPeers):
        global nameServerIP
        global nameServerPort
        global orchestratorContextObject

        ns = Pyro4.locateNS(host=nameServerIP, port=nameServerPort)
        i=0
        foundMyName = False
        firstGw = ""
        gwListDict = ns.list()
        # print("ESSA EH A LISTA: "+ str(gwListDict))
        # logger.error("tamanho da lista de peers: "+ str(len(ns.list())))
        for peerName in gwListDict:
            # print("ns list: "+str(ns.list()))
            # i== 0 is the name server... i==1 is the Gw
            if (i==1):
                firstGw = peerName

            if (foundMyName):
                newOrchestratorURI = ns.lookup(peerName)
                for orc in range(len(orchestratorContextObject)):
                    if (orchestratorContextObject[orc][0] == context):
                        orchestratorContextObject[orc][1] = Pyro4.Proxy(newOrchestratorURI)
                for peer in tempContextPeers:
                    obj = peer.object
                    dat = pickle.dumps(Pyro4.Proxy(newOrchestratorURI))
                    obj.loadElectedContextOrchestrator(context, dat)

                return True

            if (i== len(gwListDict)-1):
                newOrchestratorURI = ns.lookup(firstGw)
                for orc in range(len(orchestratorContextObject)):
                    if (orchestratorContextObject[orc][0] == context):
                        orchestratorContextObject[orc][1] = Pyro4.Proxy(newOrchestratorURI)

                # update current context orchestrator in each peer orchestrator variable
                for peer in tempContextPeers:
                    obj = peer.object
                    dat = pickle.dumps(Pyro4.Proxy(newOrchestratorURI))
                    obj.loadElectedContextOrchestrator(context, dat)
                return True


            if (peerName == gatewayName):
                foundMyName = True
                # print ("adding new peer:"+peerURI)
            i=i+1

        return False



        # for peerName in ns.list():
        #     if (peerName == gatewayName):
        #         # print ("adding new peer:"+peerURI)
        #         peerURI = ns.lookup(peerName)

    def lockForContextConsensus(self,context):
        """ lock the context consensus without resulting in deadlocks """

        global consensusLock

        tempContextPeers =[]
        counter = 0
        for x in range(len(contextPeers)):
            # print(" ***VVVVV **** context? " +contextPeers[x][0])
            if (contextPeers[x][0] == context):
                tempContextPeers = contextPeers[x][1]

        while (counter < len(tempContextPeers)):
            tempContextPeers = []
            counter = 0
            for x in range(len(contextPeers)):
                # print(" ***VVVVV **** context? " +contextPeers[x][0])
                if (contextPeers[x][0] == context):
                    tempContextPeers = contextPeers[x][1]

            while ((self.addContextinLockList(context) == False) ):#and i<100):  # in this mode (with False value) it will lock the execution and return true if it was locked or false if not
                # logger.info("$$$$$$$I can't lock my lock, waiting for it -> in lock for consensus")
                time.sleep(random.randrange(10,1000)/1000)
                # i=i+1
            # print("##Before for and after acquire my lock")
            for p in tempContextPeers:
                obj = p.object
                thisPeerIsNotAvailableToLock = obj.addContextinLockList(context)
                counter = counter + 1
                # print("On counter = "+str(counter)+" lock result was: "+str(thisPeerIsNotAvailableToLock))
                if (thisPeerIsNotAvailableToLock == False):
                    counter = counter - 1  # I have to unlock the locked ones, the last was not locked
                    # logger.error("$$$$$$$I can't lock REMOTE lock, waiting for it -> in lockforconsensus")
                    # logger.info("Almost got a deadlock")
                    self.removeLockfromContext(context)
                    if (counter > 0):
                        for p in tempContextPeers:
                            obj = p.object
                            obj.removeLockfromContext(context)
                            # logger.info("released lock counter: " + str(counter))
                            counter = counter - 1
                            if (counter == 0):
                                time.sleep(random.randrange(100, 1000) / 1000)
                                # logger.info("released locks")
                                break
                            # print("After first break PBFT")
                            # logger.info("After first break PBFT")
                    # logger.info("sleeping 0.01")
                    time.sleep(0.001)
                    break
            time.sleep(0.001)
        # logger.error("FFFFFFFFFFFFFFFFFFFFFOOOOOOOOOOOOOOOOOOOOOOOOOOIIIIIIIIIIIIII")
        return True

    def performTransactionOldWayPoolPoAConsensus(self, context):
        # print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
        global contextPeers
        # global blockContext

        # candidatePool = self.getLocalTransactionPool(context)
        pickedCandidatePool = self.getLocalTransactionPool(context)
        candidatePool = pickle.loads(pickedCandidatePool)

        candidatePooltoSend = []

        if(candidatePool != False):
            # lock other gw consensus
            # print("locking my context local: " + str(self.addContextinLockList(context)))
            # i = 0
            while(len(candidatePool)>0):
                # print("inside transaction pool i= ")
                # print(i)
                # i=i+1
                candidateTransaction = candidatePool.pop(0)

                # print(candidateTransaction)
                if(candidateTransaction != False):
                    # print("AAAAAAAAAAAAAAAA passed the if")
                    devPublicKey = candidateTransaction[0]
                    deviceInfo= candidateTransaction[1]
                    blk = ChainFunctions.findBlock(devPublicKey)
                    # print("passed the blk")
                    nextInt = blk.transactions[len(
                        blk.transactions) - 1].index + 1
                    signData = CryptoFunctions.signInfo(gwPvt, str(deviceInfo))
                    # print("BBBBBBBBBBBBB passed the devinfo")
                    gwTime = "{:.0f}".format(((time.time() * 1000) * 1000))
                    # code responsible to create the hash between Info nodes.
                    prevInfoHash = CryptoFunctions.calculateTransactionHash(
                        ChainFunctions.getLatestBlockTransaction(blk))

                    transaction = Transaction.Transaction(
                        nextInt, prevInfoHash, gwTime, deviceInfo, signData, 0)

                    ChainFunctions.addBlockTransaction(blk, transaction)
                    # logger.debug("Block #" + str(blk.index) + " added locally")
                    # logger.debug("Sending block #" +
                    #             str(blk.index) + " to peers...")

                    # --->> this function should be run in a different thread.
                    candidatePooltoSend.append((devPublicKey, transaction))
                    # instead of sending transactions individually, it will be sent in batch
                    # sendTransactionToPeers(devPublicKey, transaction)



            if(len(candidatePooltoSend)>0):
                # print("BBBBB: "+str(candidatePooltoSend))
                # context = blockContext
                dumpedSetTrans = pickle.dumps(candidatePooltoSend)
                for index in range(len(contextPeers)):
                    if(contextPeers[index][0] == context):
                        for p in contextPeers[index][1]:
                            obj=p.object
                            obj.updateBlockLedgerSetTrans(dumpedSetTrans,False)

        return


    def addNewTransactionToSyncList(self, devPubKey, devInfo, context):
        """ Add a new block to a syncronized list through the peers\n
            @param devPubKey - PubKey from the devices transaction
            @param devInfo - transaction sent by device
            @param context - devices context
        """
        # logger.debug("running critical stuffff......")
        # print("Inside addNewBlockToSyncLIst")
        global transactionLockList
        global transactionConsensusCandidateList
        # print("TTTTTTTTTTTT inside addNewTransactionToSyncList")
        #logger.info("Inside addNewTransactionToSyncList")
        index =0
        candidateTransactionTuple = (devPubKey, devInfo, context)
        # print ("********* adding a transaction from context: "+context)
        for x,y in transactionLockList:
            if x == context:
                i = 0
                while (not (transactionLockList[index][1].acquire(False))):
                    i = i + 1
                    # print("$$$$$$$$$ not possible to acquire a lock in addNewTransaciontosynclist")
                    time.sleep(0.001)
                    if (i == 100):
                        return False
                # if it got the lock, insert a new transaction into the list
                # candidade tuple is devPubKey, devInfo, context
                if(transactionConsensusCandidateList[index][0] == context):
                    transactionConsensusCandidateList[index][1].append(candidateTransactionTuple)
                    transactionLockList[index][1].release()
                else:
                    logger.error("something went wrong when adding transaction tuple")
                    return False
                # print("VVVVVV Lock released in addnewtransactionsynclist")
                return True
            index = index+1

        # TODO review this part -> if 2 devices try to create a new lock at same time, crazy thing can happen
        lockContext = thread.allocate_lock()
        myLockTuple = (context, lockContext)
        transactionLockList.append(myLockTuple)
        # return the attempt to lock the last inserted  [-1] context through its lock [1]
        # print("@@Context List after adding context to lock list for context: "+context)
        transactionLockList[-1][1].acquire(False)
        transactionConsensusCandidateList.append([context, [candidateTransactionTuple]])
        # transactionConsensusCandidateList.append(candidateTransactionTuple)
        transactionLockList[-1][1].release()
        # print("VVVVVV Lock released in addnewtransactionsynclist")
        logger.info("Transaction tuple added to list")
        return True
        # print("Unlocked")

    def getTransactionFromSyncList(self,context):
        """ Get the first block at a syncronized list through the peers\n
            @return devPubKey - Public key from the block
        """
        # logger.debug("running critical stuffff to get sync list......")
        global transactionLockList
        global transactionConsensusCandidateList
        # print("ENTERED in get transaction")
        if (len(transactionConsensusCandidateList)>0):
            index=0
            for x, y in transactionLockList:
                if x == context:
                    # print("X = ", x)
                    # print("context = ", context)
                    # return the attempt to lock the indexed context  [index] pubkey through its lock [1]
                    # print("@@Contextfound")
                    i = 0
                    while (not (transactionLockList[index][1].acquire(False)) and i < 10000):
                        i = i + 1
                        # print("$$$$$$$$$ not possible to acquire a lock in getTransaciontosfromynclist")
                        time.sleep(0.00001)
                        if (i == 10000 - 1):
                            return False
                    # if it got the lock, insert a new transaction into the list

                    if (len(transactionConsensusCandidateList) > 0):
                        # logger.debug("there is a candidade, pop it!!!")
                        transactionTuple = transactionConsensusCandidateList.pop(0)
                    transactionLockList[index][1].release()
                    # print("VVVVVV Transaction Tuple: ")
                    # print(transactionTuple[0])
                    # print("second part: ")
                    # print(transactionTuple[1])
                    # transaction tuple is formed by devPubKey and devInfo
                    return transactionTuple
                index = index + 1

        # print("end of get transaction")
        # logger.debug("Removing block from list :")#+srt(len(blockConsensusCandidateList)))
        return False


    def getNElementsLocalTransactionPool(self, context, nelements):
        global transactionLockList
        global transactionConsensusCandidateList
        #logger.info("ENTERED in get Pool")
        transactionPool = []
        if (len(transactionConsensusCandidateList) > 0):
            index = 0
            for x, y in transactionLockList:
                if x == context:
                    # print("X = ", x)
                    # print("context = ", context)
                    # return the attempt to lock the indexed context  [index] pubkey through its lock [1]
                    # print("@@Contextfound")
                    i = 0
                    getLockList = transactionLockList[index][1].acquire(False)
                    while (not (getLockList) and i < 1000):
                        i = i + 1
                        # print("$$$$$$$$$ not possible to acquire a lock in getTransaciontosfromynclist")
                        time.sleep(0.001)
                        getLockList = transactionLockList[index][1].acquire(False)
                    if (not (getLockList)):
                        # transactionLockList[index][1].release()
                        logger.error("tried to GET and it was not possible, returning False")
                        return pickle.dumps(False)
                    # if it got the lock, insert a new transaction into the list

                    if (len(transactionConsensusCandidateList[index][1]) > 0):
                        if (len(transactionConsensusCandidateList[index][1]) > nelements):
                            # logger.debug("there is a candidade, pop it!!!")
                            # transactionPool = transactionConsensusCandidateList[index]
                            # get only N transactions from the correct context and after clean that N transactions
                            transactionPool = transactionConsensusCandidateList[index][1][:nelements]
                            # print("there is a pool candidate, pop it!!! context: " + context)
                            transactionConsensusCandidateList[index][1] = transactionConsensusCandidateList[index][1][nelements:]
                            transactionLockList[index][1].release()
                            pickedTransactionPool = pickle.dumps(transactionPool)
                            return pickedTransactionPool

                        # if it does not have nelements, return current amount
                        transactionPool = transactionConsensusCandidateList[index][1]
                        # logger.info("there is a pool candidate, pop it!!! context: " + context)
                        transactionConsensusCandidateList[index][1] = []
                        transactionLockList[index][1].release()
                        pickedTransactionPool = pickle.dumps(transactionPool)
                        return pickedTransactionPool

                    transactionLockList[index][1].release()
                    return pickle.dumps(False)
                    # print("VVVVVV Transaction Tuple: ")
                    # print(transactionTuple[0])
                    # print("second part: ")
                    # print(transactionTuple[1])
                    # transaction tuple is formed by devPubKey and devInfo
                    # return transactionPool
                index = index + 1

        #print("end of get transaction")
        #logger.info("Removing block from list :")#+srt(len(blockConsensusCandidateList)))
        return pickle.dumps(False)

    def getLocalTransactionPool(self, context):
        """ Get the first block at a syncronized list through the peers\n
            @return devPubKey - Public key from the block
        """
        # logger.debug("running critical stuffff to get sync list......")
        global transactionLockList
        global transactionConsensusCandidateList
        # print("ENTERED in get Pool")
        transactionPool = []
        if (len(transactionConsensusCandidateList) > 0):
            index = 0
            for x, y in transactionLockList:
                if x == context:
                    # print("X = ", x)
                    # print("context = ", context)
                    # return the attempt to lock the indexed context  [index] pubkey through its lock [1]
                    # print("@@Contextfound")
                    i = 0
                    getTrPool = transactionLockList[index][1].acquire(False)
                    while (not (getTrPool) and i < 1000):
                        i = i + 1
                        # print("$$$$$$$$$ not possible to acquire a lock in getTransaciontosfromynclist")
                        time.sleep(0.001)
                        getTrPool = transactionLockList[index][1].acquire(False)
                    if (not (getTrPool)):
                        transactionLockList[index][1].release()
                        return pickle.dumps(False)
                    # if it got the lock, insert a new transaction into the list

                    if (len(transactionConsensusCandidateList[index][1]) > 0):
                        # logger.debug("there is a candidade, pop it!!!")
                        # transactionPool = transactionConsensusCandidateList[index]
                        # get only the transactions from the correct context and after clean that transactions
                        transactionPool = transactionConsensusCandidateList[index][1]
                        # print("there is a pool candidate, pop it!!! context: " + context)
                        transactionConsensusCandidateList[index][1] = []
                        transactionLockList[index][1].release()
                        pickedTransactionPool = pickle.dumps(transactionPool)
                        return pickedTransactionPool

                    transactionLockList[index][1].release()
                    # print("VVVVVV Transaction Tuple: ")
                    # print(transactionTuple[0])
                    # print("second part: ")
                    # print(transactionTuple[1])
                    # transaction tuple is formed by devPubKey and devInfo
                    # return transactionPool
                index = index + 1

        # print("end of get transaction")
        # logger.debug("Removing block from list :")#+srt(len(blockConsensusCandidateList)))
        return pickle.dumps(False)

    def addContextinLockList(self,context):
        global contextLockList
        ############# transactionLockList is a list of tuples composed by context and its lock
        # index=0
        ############# 1 lock per block -> 1 consensus per block
        lockContext = thread.allocate_lock()
        myLockTuple = (context, lockContext)

        for x,y in contextLockList:
            if x == context:
                # return the attempt to lock the indexed context  [index] pubkey through its lock [1]
                # print("@@Contextfound")
                # return contextLockList[index][1].acquire(False)
                return y.acquire(False)
            # index = index+1

        contextLockList.append(myLockTuple)
        # return the attempt to lock the last inserted  [-1] context through its lock [1]
        # print("@@Context List after adding context to lock list")
        # return contextLockList[-1][1].acquire(False)
        for x,y in contextLockList:
            if x == context:
                # return the attempt to lock the indexed context  [index] pubkey through its lock [1]
                # print("@@Contextfound")
                # return contextLockList[index][1].acquire(False)
                return y.acquire(False)

    def removeLockfromContext(self, context):
        global contextLockList
        ############# transactionLockList is a list of tuples composed by devpubkey and its lock
        # index = 0
        for x, y in contextLockList:
            if x == context:
                # return the attempt to lock the indexed devpublickley  [index] pubkey through its lock [1]
                # contextLockList[index][1].release()
                try:
                    y.release()
                except:
                    logger.error("not locked lock")
                return True
            # index = index + 1
        return False


    def addTransactionToPool(self, devPublicKey, encryptedObj):
        """ Receive a new transaction to be add to the chain, a
            send to the pool it to all peers\n
            @param devPublicKey - Public key from the sender device\n
            @param encryptedObj - Info of the transaction encrypted with AES 256\n
            @return "ok!" - all done\n
            @return "Invalid Signature" - an invalid key are found\n
            @return "Key not found" - the device's key are not found
        """
        # logger.debug("Transaction received")
        global gwPvt
        global gwPub
        global logT24
        global logT25
        t1 = time.time()

        # loading key and encryptedObj from from pickle serialization
        devPublicKey=pickle.loads(devPublicKey)
        # print("DevPubKey= " + str(devPublicKey))
        encryptedObj=pickle.loads(encryptedObj)

        blk = ChainFunctions.findBlock(devPublicKey)
        # self.addContextinLockList(devPublicKey)
        if (blk != False and blk.index > 0):
            devAESKey = findAESKey(devPublicKey)
            if (devAESKey != False):
                # logger.info("Appending transaction to block #" +
                #             str(blk.index) + "...")
                # plainObject contains [Signature + Time + Data]

                plainObject = CryptoFunctions.decryptAES(
                    encryptedObj, devAESKey)

                # retrieve the last chars, excluding timestamp - 16 bytes and signature - 172 bytes
                deviceData = plainObject[(172+16):]
                # remove the last 20 chars
                signature = plainObject[:-(16+len(deviceData))]
                # print("###Signature after receiving: "+signature)
                # print("###Device Data: "+deviceData)
                # remove the 16 char of timestamp
                devTime = plainObject[-(16+len(deviceData)):-len(deviceData)]
                # print("###devTime: "+devTime)
                t2 = time.time()
                # logger.info("gateway;" + gatewayName + ";" + consensus + ";T1;Time to add a new transaction in a block;" + '{0:.12f}'.format((t2 - t1) * 1000))

                d = devTime+deviceData
                isSigned = CryptoFunctions.signVerify(
                    d, signature, devPublicKey)

                if isSigned:
                    deviceInfo = DeviceInfo.DeviceInfo(
                        signature, devTime, deviceData)

                    # send to consensus here
                    devContext = blk.blockContext
                    # print("SSSSSSSS my Context: ")
                    # print(devContext)
                    t2=time.time()
                    logT24.append("T24 VERIFICATION TIME; " + str((t2-t1)*1000))
                    t3=time.time()
                    while ( self.addNewTransactionToSyncList(devPublicKey, deviceInfo, devContext) == False):
                        logger.error("tried to insert and it was not possible, trying again")
                        time.sleep(0.001)
                    t4=time.time()
                    logT25.append("T25 Appending TX IN POOL TIME; " + str((t4-t3)*1000))
                    # after context

                    # print("all done")
                    # self.removeLockfromContext(devPublicKey)
                    return "ok!"
                else:
                    # logger.debug("--Transaction not appended--Transaction Invalid Signature")
                    # self.removeLockfromContext(devPublicKey)
                    return "Invalid Signature"
            # logger.debug("--Transaction not appended--Key not found")
            # self.removeLockfromContext(devPublicKey)
            return "key not found"
        logger.error("key not found when adding transaction")
        # self.removeLockfromContext(devPublicKey)
        return "block false"

    def addTransaction(self, devPublicKey, encryptedObj):
        """ Receive a new transaction to be add to the chain, add the transaction
            to a block and send it to all peers\n
            @param devPublicKey - Public key from the sender device\n
            @param encryptedObj - Info of the transaction encrypted with AES 256\n
            @return "ok!" - all done\n
            @return "Invalid Signature" - an invalid key are found\n
            @return "Key not found" - the device's key are not found
        """
        # logger.debug("Transaction received")
        global gwPvt
        global gwPub

        t1 = time.time()
        blk = ChainFunctions.findBlock(devPublicKey)

        # self.addContextinLockList(devPublicKey)
        if (blk != False and blk.index > 0):
            devAESKey = findAESKey(devPublicKey)
            if (devAESKey != False):
                # logger.info("Appending transaction to block #" +
                #             str(blk.index) + "...")
                # plainObject contains [Signature + Time + Data]

                plainObject = CryptoFunctions.decryptAES(
                    encryptedObj, devAESKey)
                signature = plainObject[:-20]  # remove the last 20 chars
                # remove the 16 char of timestamp
                devTime = plainObject[-20:-4]
                # retrieve the las 4 chars which are the data
                deviceData = plainObject[-4:]

                d = devTime+deviceData
                isSigned = CryptoFunctions.signVerify(
                    d, signature, devPublicKey)

                if isSigned:
                    deviceInfo = DeviceInfo.DeviceInfo(
                        signature, devTime, deviceData)
                    nextInt = blk.transactions[len(
                        blk.transactions) - 1].index + 1
                    signData = CryptoFunctions.signInfo(gwPvt, str(deviceInfo))
                    gwTime = "{:.0f}".format(((time.time() * 1000) * 1000))
                    # code responsible to create the hash between Info nodes.
                    prevInfoHash = CryptoFunctions.calculateTransactionHash(
                        ChainFunctions.getLatestBlockTransaction(blk))

                    transaction = Transaction.Transaction(
                        nextInt, prevInfoHash, gwTime, deviceInfo, signData,0)

                    # send to consensus
                    # if not consensus(newBlockLedger, gwPub, devPublicKey):
                    #    return "Not Approved"
                    # if not PBFTConsensus(blk, gwPub, devPublicKey):
                    #     return "Consensus Not Reached"

                    ChainFunctions.addBlockTransaction(blk, transaction)
                    # logger.debug("Block #" + str(blk.index) + " added locally")
                    # logger.debug("Sending block #" +
                    #             str(blk.index) + " to peers...")
                    t2 = time.time()
                    logger.info("gateway;" + gatewayName + ";" + consensus + ";T1;Time to add a new transaction in a block;" + '{0:.12f}'.format((t2 - t1) * 1000))
                    # new data collection
                    currentTimestamp = float(((time.time()) * 1000) * 1000)
                    logger.info(
                        "gateway;" + gatewayName + ";T20;Transaction Latency;" + str(
                            (currentTimestamp - float(devTime)) / 1000))
                    logger.info(
                        "gateway;" + gatewayName  + ";T26;First Transaction Latency;" + str(
                            (currentTimestamp - float(devTime)) / 1000))

                    # --->> this function should be run in a different thread.
                    sendTransactionToPeers(devPublicKey, transaction)
                    # print("all done")
                    # self.removeLockfromContext(devPublicKey)
                    return "ok!"
                else:
                    # logger.debug("--Transaction not appended--Transaction Invalid Signature")
                    # self.removeLockfromContext(devPublicKey)
                    return "Invalid Signature"
            # logger.debug("--Transaction not appended--Key not found")
            # self.removeLockfromContext(devPublicKey)
            return "key not found"
        logger.error("key not found when adding transaction")
        # self.removeLockfromContext(devPublicKey)
        return "block false"


    def addTinLockList(self,devPublicKey):
        global transactionLockList
        print("@@Locking SC List")
        ############# transactionLockList is a list of tuples composed by devpubkey and its lock
        index=0
        ############# 1 lock per block -> 1 consensus per block
        for x,y in transactionLockList:
            if x == devPublicKey:
                # return the attempt to lock the indexed devpublickley  [index] pubkey through its lock [1]
                print("@@Keyfound")
                return transactionLockList[index][1].acquire(False)
            index = index+1
        lockSC = thread.allocate_lock()
        myLockTuple = (devPublicKey, lockSC)
        transactionLockList.append(myLockTuple)
        # return the attempt to lock the last inserted  [-1] pubkey through its lock [1]
        print("@@Locking SC List after adding key")
        return transactionLockList[-1][1].acquire(False)

    def removeLockfromT(self, devPublicKey):
        global transactionLockList
        ############# transactionLockList is a list of tuples composed by devpubkey and its lock
        index = 0
        for x, y in transactionLockList:
            if x == devPublicKey:
                # return the attempt to lock the indexed devpublickley  [index] pubkey through its lock [1]
                transactionLockList[index][1].release()
                return True
            index = index + 1
        return False

    ##############################
    ################ To add an Smart Contract transaction can be done in 2 ways
    #################### addTransaction SC2 
    #######################################################
    def addTransactionSC2(self, transactionData,signedDatabyDevice,devPublicKey,devTime):
        """ Receive a new transaction to be add to the chain, add the transaction
            to a block and send it to all peers\n
            @param devPublicKey - Public key from the sender device\n
            @param encryptedObj - Info of the transaction encrypted with AES 256\n
            @return "ok!" - all done\n
            @return "Invalid Signature" - an invalid key are found\n
            @return "Key not found" - the device's key are not found
        """
        # logger.debug("Transaction received")

        global transactionLockList
        global gwPvt
        global gwPub
        t1 = time.time()
        blk = ChainFunctions.findBlock(devPublicKey)
        self.addTinLockList(devPublicKey)

        if (blk != False and blk.index > 0):
            #wait

        # if (consensus == "dBFT" or consensus == "Witness3"):
        #     # consensusLock.acquire(1) # only 1 consensus can be running at same time
        #     # for p in peers:
        #     #     obj=p.object
        #     #     obj.acquireLockRemote()
        #     self.lockForConsensus()
        #     # print("ConsensusLocks acquired!")
        #     orchestratorObject.addBlockConsensusCandidate(pickedKey)
        #     orchestratorObject.rundBFT()
        #
        #processing....
        #
        #
        #at end...




                isSigned = True #ToDo verify device signature

                if isSigned:
                    # print("it is signed!!!")
                    deviceInfo = DeviceInfo.DeviceInfo(signedDatabyDevice, devTime, transactionData)
                    nextInt = blk.transactions[len(
                        blk.transactions) - 1].index + 1
                    signData = CryptoFunctions.signInfo(gwPvt, str(deviceInfo))
                    gwTime = "{:.0f}".format(((time.time() * 1000) * 1000))
                    # code responsible to create the hash between Info nodes.
                    prevInfoHash = CryptoFunctions.calculateTransactionHash(
                        ChainFunctions.getLatestBlockTransaction(blk))

                    transaction = Transaction.Transaction(
                        nextInt, prevInfoHash, gwTime, deviceInfo, signData, 0) #nonce = 0
                    #
                    #Set a lock for each device/sc pubkey
                    #verify lock
                    #perform consensus if it is not locked
                    # send to consensus
                    # if not consensus(newBlockLedger, gwPub, devPublicKey):
                    #    return "Not Approved"
                    # if not PBFTConsensus(blk, gwPub, devPublicKey):
                    #     return "Consensus Not Reached"

                    ChainFunctions.addBlockTransaction(blk, transaction)
                    # logger.debug("Block #" + str(blk.index) + " added locally")
                    # logger.debug("Sending block #" +
                    #              str(blk.index) + " to peers...")
                    t2 = time.time()
                    logger.info("gateway;" + gatewayName + ";" + consensus + ";T1;Time to add a new transaction in a block;" + '{0:.12f}'.format((t2 - t1) * 1000))
                    # --->> this function should be run in a different thread.
                    sendTransactionToPeers(devPublicKey, transaction)
                    # print("all done in transations")
                    # transactionLockList.remove(devPublicKey)
                    self.removeLockfromT(devPublicKey)
                    return "ok!"
                else:
                    # print("Signature is not ok")
                    # logger.debug("--Transaction not appended--Transaction Invalid Signature")
                    # transactionLockList.remove(devPublicKey)
                    self.removeLockfromT(devPublicKey)
                    return "Invalid Signature"
            # logger.debug("--Transaction not appended--Key not found")
        # transactionLockList.remove(devPublicKey)
        self.removeLockfromT(devPublicKey)
        return "key not found"

    def addTransactionSC(self, devPublicKey, encryptedObj):
        """ Receive a new transaction to be add to the chain, add the transaction
            to a block and send it to all peers\n
            @param devPublicKey - Public key from the sender device\n
            @param encryptedObj - Info of the transaction encrypted with AES 256\n
            @return "ok!" - all done\n
            @return "Invalid Signature" - an invalid key are found\n
            @return "Key not found" - the device's key are not found
        """
        # logger.debug("Transaction received")
        global gwPvt
        global gwPub
        t1 = time.time()
        blk = ChainFunctions.findBlock(devPublicKey)
        if (blk != False and blk.index > 0):
            devAESKey = findAESKey(devPublicKey)
            if (devAESKey != False):
                # logger.info("Appending transaction to block #" +
                #             str(blk.index) + "...")
                # plainObject contains [Signature + Time + Data]

                plainObject = CryptoFunctions.decryptAES(
                    encryptedObj, devAESKey)
                # retrieve the last chars, excluding timestamp and signature
                deviceData = plainObject[(172+16):]
                # remove the last 20 chars
                signature = plainObject[:-(16+len(deviceData))]
                # print("###Signature after receiving: "+signature)
                # print("###Device Data: "+deviceData)
                # remove the 16 char of timestamp
                devTime = plainObject[-(16+len(deviceData)):-len(deviceData)]
                # print("###devTime: "+devTime)

                d = devTime+deviceData
                isSigned = CryptoFunctions.signVerify(
                    d, signature, devPublicKey)

                if isSigned:
                    # print("it is signed!!!")
                    deviceInfo = DeviceInfo.DeviceInfo(
                        signature, devTime, deviceData)
                    nextInt = blk.transactions[len(
                        blk.transactions) - 1].index + 1
                    signData = CryptoFunctions.signInfo(gwPvt, str(deviceInfo))
                    gwTime = "{:.0f}".format(((time.time() * 1000) * 1000))
                    # code responsible to create the hash between Info nodes.
                    prevInfoHash = CryptoFunctions.calculateTransactionHash(
                        ChainFunctions.getLatestBlockTransaction(blk))

                    transaction = Transaction.Transaction(
                        nextInt, prevInfoHash, gwTime, deviceInfo, signData,0)#nonce=0

                    # send to consensus
                    # if not consensus(newBlockLedger, gwPub, devPublicKey):
                    #    return "Not Approved"
                    # if not PBFTConsensus(blk, gwPub, devPublicKey):
                    #     return "Consensus Not Reached"

                    ChainFunctions.addBlockTransaction(blk, transaction)
                    # logger.debug("Block #" + str(blk.index) + " added locally")
                    # logger.debug("Sending block #" +
                    #              str(blk.index) + " to peers...")
                    t2 = time.time()
                    logger.info("gateway;" + gatewayName + ";" + consensus + ";T1;Time to add a new transaction in a block;" + '{0:.12f}'.format((t2 - t1) * 1000))
                    # --->> this function should be run in a different thread.
                    sendTransactionToPeers(devPublicKey, transaction)
                    # print("all done in transations")
                    return "ok!"
                else:
                    # print("Signature is not ok")
                    # logger.debug("--Transaction not appended--Transaction Invalid Signature")
                    return "Invalid Signature"
            # logger.debug("--Transaction not appended--Key not found")
            return "key not found"

    def updateBlockLedger(self, pubKey, transaction):
        # update local bockchain adding a new transaction
        """ Receive a new transaction and add it to the chain\n
            @param pubKey - Block public key\n
            @param transaction - Data to be insert on the block\n
            @return "done" - method done (the block are not necessarily inserted)
        """
        trans = pickle.loads(transaction)
        t1 = time.time()
        # logger.info("Received transaction #" + (str(trans.index)))
        blk = ChainFunctions.findBlock(pubKey)
        if blk != False:
            # logger.debug("Transaction size in the block = " +
            #              str(len(blk.transactions)))
            if not (ChainFunctions.blockContainsTransaction(blk, trans)):
                if validatorClient:
                    isTransactionValid(trans, pubKey)
                ChainFunctions.addBlockTransaction(blk, trans)
        t2 = time.time()
        logger.info("gateway;" + gatewayName + ";" + consensus + ";T2;Time to add a transaction in block ledger;" + '{0:.12f}'.format((t2 - t1) * 1000))
        return "done"

    def updateBlockLedgerSetTrans(self, candidatePool, isFirst):
        global logT20
        global logT21
        global logT26
        # update local bockchain adding a new transaction
        """ Receive a new transaction and add it to the chain\n
            @param pubKey - Block public key\n
            @param transaction - Data to be insert on the block\n
            @return "done" - method done (the block are not necessarily inserted)
        """
        setTrans = pickle.loads(candidatePool)
        t1 = time.time()
        # print("inside updateBlockLedgerSeTrans, setTrans: " + str(setTrans))
        # logger.info("Received transaction #" + (str(trans.index)))
        originalLen = len(setTrans)
        while (len(setTrans)>0):
            candidateTransaction = setTrans.pop(0)
            # print("popped element from Pool")
            # print(candidateTransaction)
            if (candidateTransaction != False):
                # print("AAAAAAAAAAAAAAAA passed the if")
                devPublicKey = candidateTransaction[0]
                deviceTrans = candidateTransaction[1]
                blk = ChainFunctions.findBlock(devPublicKey)
                ChainFunctions.addBlockTransaction(blk, deviceTrans)
                deviceTrans.__class__ = Transaction.Transaction
                candidateDevInfo = deviceTrans.data
                candidateDevInfo.__class__ = DeviceInfo.DeviceInfo
                originalTimestamp = float (candidateDevInfo.timestamp)
                gwTimestamp = float(deviceTrans.timestamp)
                currentTimestamp = float (((time.time())*1000)*1000)
                logT20.append("gateway;" + gatewayName +";Context;" +blk.blockContext + ";T20;Transaction Latency;" + str((currentTimestamp - originalTimestamp)/1000))
                if(isFirst):
                    logT26.append("gateway;" + gatewayName + ";Context;" + blk.blockContext + ";T26;First Transaction Latency;" + str((currentTimestamp - originalTimestamp) / 1000))
                # logger.info("gateway;" + gatewayName + ";" + consensus + ";T20;Latency to generate and insert in my Gw is;" + str((currentTimestamp - originalTimestamp)/1000))
                # logger.info(
                #     "gateway;" + gatewayName + ";" + consensus + ";T21;Time to process Tr is;" + str(
                #         (currentTimestamp - gwTimestamp) / 1000))

        t2 = time.time()
        logT21.append("gateway;" + gatewayName + ";T21;Time to add a set of ;" + str(originalLen) + "; transactions in block ledger;" + '{0:.12f}'.format((t2 - t1) * 1000))
        # logger.info("gateway;" + gatewayName + ";" + consensus + ";T2;Time to add a set of ;" + str(originalLen) + "; transactions in block ledger;" + '{0:.12f}'.format((t2 - t1) * 1000))

        return "done"


    def updateIOTBlockLedger(self, iotBlock, gwName):
        # update local bockchain adding a new block
        """ Receive a block and add it to the chain\n
            @param iotBlock - Block to be add\n
            @param gwName - sender peer's name
        """
        global logT3
        # print("Updating IoT Block Ledger, in Gw: "+str(gwName))
        # logger.debug("updateIoTBlockLedger Function")
        b = pickle.loads(iotBlock)
        # print("picked....")
        t1 = time.time()
        # logger.debug("Received block #" + (str(b.index)))
        # logger.info("Received block #" + str(b.index) +
        #             " from gateway " + str(gwName))
        if isBlockValid(b):
            # print("updating is valid...")
            ChainFunctions.addBlockHeader(b)
        t2 = time.time()
        # print("updating was done")
        logT3.append(
            "gateway;" + gatewayName + ";" + consensus + ";T3;Time to add a new block in BL;" + '{0:.12f}'.format((t2 - t1) * 1000))
        # logger.info("gateway;" + gatewayName + ";" + consensus + ";T3;Time to add a new block in block ledger;" + '{0:.12f}'.format((t2 - t1) * 1000))

    def removeBlockConsensusCandidate(self, devPubKey):
        global blockConsensusCandidateList
        devKey = pickle.loads(devPubKey)
        if(devKey in blockConsensusCandidateList):
            blockConsensusCandidateList.pop()


    def addBlockConsensusCandidate(self, devPubKey):

        global blockConsensusCandidateList
        # logger.debug("================================================")
        # print("Inside addBlockConsensusCandidate, devPubKey: ")
        # print(devPubKey)
        devKey = pickle.loads(devPubKey)
        # print("Inside addBlockConsensusCandidate, devKey: ")
        # print(devPubKey)
        # logger.debug("This method is executed by orchestrator."+str(devKey))
        # logger.debug("received new block consensus candidate. Queue Size:"+srt(len(blockConsensusCandidateList)))
        addNewBlockToSyncList(devKey)
        # logger.debug("added to the sync list")
        # logger.debug("================================================")

    def acquireLockRemote(self):
        global consensusLock
        # with False argument, it will return true if it was locked or false if it could not be locked
        return consensusLock.acquire(False)
        # consensusLock.acquire(1)
        # return True

    def releaseLockRemote(self):
        global consensusLock
        consensusLock.release()

    def addBlock(self, devPubKey, lifecycleDeviceName):
        """ Receive a device public key from a device and link it to a block on the chain\n
            @param devPubKey - request's device public key\n
            @return encKey - RSA encrypted key for the device be able to communicate with the peers
        """
        global gwPub
        global consensusLock
        global orchestratorObject
        # print("addingblock... DevPubKey:" + devPubKey)
        # logger.debug("|---------------------------------------------------------------------|")
        # logger.info("Block received from device")
        aesKey = ''
        encKey = ''
        t1 = time.time()
        # print("Adding block, PubKey= " + str(devPubKey))
        blk = ChainFunctions.findBlock(devPubKey)

        if (blk != False and blk.index > 0):
            # print("inside first if")
            logger.error("It may be already be registered, generating another aeskey")
            aesKey = findAESKey(devPubKey)
            logger.error("passed by findAESKEY")
            if ((aesKey == False) or (len(aesKey) != 32)):
                logger.error("aeskey had a problem...")
                removeAESKey(aesKey)
                aesKey = generateAESKey(blk.publicKey)
                encKey = CryptoFunctions.encryptRSA2(devPubKey, aesKey)
                return encKey
                # t2 = time.time()
            logger.error("actually it didn't had problem with the key")
            logger.error("publick key received was: " + str(devPubKey) + "blk key was: " + str(blk.publicKey) + " ...")
            removeAESKey(aesKey)
            aesKey = generateAESKey(blk.publicKey)
            encKey = CryptoFunctions.encryptRSA2(devPubKey, aesKey)
            return encKey
            # t2 = time.time()
        else:
            # print("inside else")
            # logger.debug("***** New Block: Chain size:" +
            #              str(ChainFunctions.getBlockchainSize()))
            pickedKey = pickle.dumps(devPubKey)
            aesKey = generateAESKey(devPubKey)
            while(len(aesKey) != 32):
                logger.error("Badly generated aesKey")
                aesKey = generateAESKey(devPubKey)
            # print("pickedKey: ")
            # print(pickedKey)

            encKey = CryptoFunctions.encryptRSA2(devPubKey, aesKey)
            # t2 = time.time()
            # Old No Consensus
            # bl = ChainFunctions.createNewBlock(devPubKey, gwPvt)
            # sendBlockToPeers(bl)
            # logger.debug("starting block consensus")
            #############LockCONSENSUS STARTS HERE###############
            if(consensus == "PBFT"):
                # PBFT elect new orchestator every time that a new block should be inserted
                # allPeersAreLocked = False
                self.lockForConsensus()
                # print("ConsensusLocks acquired!")
                self.electNewOrchestrator()
                # print("New Orchestrator URI: " + str(orchestratorObject.exposedURI()))
                orchestratorObject.addBlockConsensusCandidate(pickedKey)
                counter_fails = 0
                while(orchestratorObject.runPBFT(lifecycleDeviceName)==False):
                    # logger.info("##### second attmept for a block")
                    orchestratorObject.removeBlockConsensusCandidate(pickedKey)
                    # print("$$$$$$$second trial")
                    self.electNewOrchestrator()
                    orchestratorObject.addBlockConsensusCandidate(pickedKey)
                    counter_fails = counter_fails + 1
                    if (counter_fails > 200):
                        return -1

            if(consensus == "dBFT" or consensus == "Witness3"):
                # print("indo pro dbft")
                # consensusLock.acquire(1) # only 1 consensus can be running at same time
                # for p in peers:
                #     obj=p.object
                #     obj.acquireLockRemote()
                self.lockForConsensus()

                orchestratorObject.addBlockConsensusCandidate(pickedKey)
                # print("blockadded!")
                counter_fails = 0
                while (orchestratorObject.rundBFT() == False):
                    # logger.info("##### second attempt for a block")
                    orchestratorObject.removeBlockConsensusCandidate(pickedKey)
                    logger.error("Consensus not achieved, trying another one")
                    self.electNewOrchestrator()
                    orchestratorObject.addBlockConsensusCandidate(pickedKey)
                    counter_fails = counter_fails +1
                    if (counter_fails > 200):
                        return -1
                # print("after rundbft")
            if(consensus == "PoW"):
                # consensusLock.acquire(1) # only 1 consensus can be running at same time
                # for p in peers:
                #     obj=p.object
                #     obj.acquireLockRemote()
                self.lockForConsensus()
                # print("ConsensusLocks acquired!")
                self.addBlockConsensusCandidate(pickedKey)
                self.runPoW()
            if(consensus == "None"):
                self.addBlockConsensusCandidate(pickedKey)
                self.runNoConsesus(lifecycleDeviceName)
            if(consensus == "PoA"):
                self.lockForConsensus()
                self.addBlockConsensusCandidate(pickedKey)
                self.runPoA()

            # print("after orchestratorObject.addBlockConsensusCandidate")
            # try:
            # PBFTConsensus(bl, gwPub, devPubKey)
            # except KeyboardInterrupt:
            #     sys.exit()
            # except:
            #     print("failed to execute:")
            #     logger.error("failed to execute:")
            #     exc_type, exc_value, exc_traceback = sys.exc_info()
            #     print "*** print_exception:"    l
            #     traceback.print_exception(exc_type, exc_value, exc_traceback,
            #                           limit=6, file=sys.stdout)
            #
            # logger.debug("end block consensus")
            # try:
            #     #thread.start_new_thread(sendBlockToPeers,(bl))
            #     t1 = sendBlks(1, bl)
            #     t1.start()
            # except:
            #     print "thread not working..."

            if(consensus == "PBFT" or consensus == "dBFT" or consensus == "Witness3" or consensus == "PoW" or consensus == "PoA"):
                self.releaseLockForConsensus()
                for p in peers:
                    obj = p.object
                    obj.releaseLockRemote()
                # print("ConsensusLocks released!")
            ######end of lock consensus################

            # print("Before encryption of rsa2")

            t3 = time.time()
            # logger.info("gateway;" + gatewayName + ";" + consensus + ";T1;Time to generate key;" + '{0:.12f}'.format((t2 - t1) * 1000))
            logT6.append("gateway;" + gatewayName + ";" + consensus + ";T6;Time to add and replicate a new block in blockchain;" + '{0:.12f}'.format((t3 - t1) * 1000))
            # logger.debug("|---------------------------------------------------------------------|")
            # print("block added")
        return encKey


    def getRemoteContext(self):
        global blockContext
        return blockContext

    def getRemoteContexts(self):
        global gwContextConsensus
        return gwContextConsensus


    def addPeer(self, peerURI, isFirst, contexts):
        """ Receive a peer URI add it to a list of peers.\n
            the var isFirst is used to ensure that the peer will only be added once.\n
            @param peerURI - peer URI\n
            @param isFirst - Boolean condition to add only one time a peer\n
            @return True - peer successfully added\n
            @return False - peer is already on the list
        """
        global peers
        global contextPeers

        if not (findPeer(peerURI)):
            newPeer = PeerInfo.PeerInfo(peerURI, Pyro4.Proxy(peerURI))
            peers.append(newPeer)

            # print("running add peer in addPeer in contextPeers")
            obj = newPeer.object
            # print("After creating obj in ADDpeer")
            newPeerContext = contexts
            # newPeerContext = obj.getRemoteContext()
            # print("after getting remote context")
            for x, y in newPeerContext:
                foundContextPeer = False
                for index in range(len(contextPeers)):
                    if (contextPeers[index][0] == x):
                        print("Context found: " + x)
                        contextPeers[index][1].append(newPeer)
                        print("Peer added2 to context Peer" + str(contextPeers))
                        foundContextPeer = True
                if (foundContextPeer == False):
                    # print("2did not find context in contextPeers, creating and appending")
                    contextPeers.append([x, [newPeer]])
                    # print("2CONTEXT and PEER added to context Peer" + str(contextPeers))
            # foundContextPeer = False
            # for index in range(len(contextPeers)):
            #     if (contextPeers[index][0] == newPeerContext):
            #         print("Context found: " + newPeerContext)
            #         contextPeers[index][1].append(newPeer)
            #         print("Peer added to context Peer" + str(contextPeers))
            #         foundContextPeer = True
            # if (foundContextPeer == False):
            #     # print("did not find context in contextPeers, creating and appending")
            #     contextPeers.append([newPeerContext, [newPeer]])
            #     print("CONTEXT and PEER added to context Peer" + str(contextPeers))

            if isFirst:
                # after adding the original peer, send false to avoid loop
                addBack(newPeer, False)
            syncChain(newPeer)


            return True
        else:
            # print("peer is already on the list")
            return False

    def showIoTLedger(self):
        """ Log all chain \n
            @return "ok" - done
        """
        # logger.info("Showing Block Header data for peer: " + myURI)
        print("Showing Block Header data for peer: " + myURI)
        size = ChainFunctions.getBlockchainSize()
        # logger.info("IoT Ledger size: " + str(size))
        # logger.info("|-----------------------------------------|")
        print("IoT Ledger size: " + str(size))
        print("|-----------------------------------------|")
        theChain = ChainFunctions.getFullChain()
        for b in theChain:
        # logger.info(b.strBlock())
        # logger.info("|-----------------------------------------|")
            print(b.strBlock())
            print("|-----------------------------------------|")
        return "ok"

    def showLastTransactionData(self, blockIndex):
        #print("Showing Data from Last Transaction from block #: " + str(blockIndex))
        blk = ChainFunctions.getBlockByIndex(blockIndex)
        lastTransactionInfo = ChainFunctions.getLatestBlockTransaction(blk).data
        transactionData = lastTransactionInfo.strInfoData()

        # print("My data is: "+str(transactionData))

        return transactionData

    def saveLog(self):
        self.remoteSaveLog()
        for p in peers:
            p.object.remoteSaveLog()
        return

    def remoteSaveLog(self):
        global logT3
        global logT5
        global logT6
        global logT20
        global logT21
        global logT22
        global logT23
        global logT24
        global logT25
        global logT26

        for i in range(len(logT3)):
            logger.info(logT3[i])
        print("Log T3 saved")
        logT3 = []

        for i in range(len(logT5)):
            logger.info(logT5[i])
        print("Log T5 saved")
        logT5 = []

        for i in range(len(logT6)):
            logger.info(logT6[i])
        print("Log T6 saved")
        logT6 = []

        for i in range(len(logT20)):
            logger.info(logT20[i])
        print("Log T20 saved")
        logT20 = []

        for i in range(len(logT21)):
            logger.info(logT21[i])
        print("Log T21 saved")
        logT21 = []

        for i in range(len(logT22)):
            logger.info(logT22[i])
        print("Log T22 saved")
        logT22 = []


        for i in range(len(logT23)):
            logger.info(logT23[i])
        print("Log T23 saved")
        logT23 = []

        for i in range(len(logT24)):
            logger.info(logT24[i])
        print("Log T24 saved")
        logT24 = []

        for i in range(len(logT25)):
            logger.info(logT25[i])
        print("Log T25 saved")
        logT25 = []

        for i in range(len(logT26)):
            logger.info(logT26[i])
        print("Log T26 saved")
        logT26 = []


        return



    def showBlockLedger(self, index):
        """ Log all transactions of a block\n
            @param index - index of the block\n
            @return "ok" - done
        """
        print("Showing Transactions data for peer: " + myURI)
        # logger.info("Showing Trasactions data for peer: " + myURI)
        blk = ChainFunctions.getBlockByIndex(index)
        print("Block for index"+str(index))
        if blk == False:
            return "Block does not exist"
        size = len(blk.transactions)
        # logger.info("Block Ledger size: " + str(size))
        # logger.info("-------")
        print("Block Ledger size: " + str(size))
        print("-------")
        for b in blk.transactions:
            # logger.info(b.strBlock())
            # logger.info("-------")
            print(b.strBlock())
            print("-------")
        return "ok"

    def listPeer(self):
        """ Log all peers in the network\n
            @return "ok" - done
        """
        global peers
        # logger.info("|--------------------------------------|")
        # for p in peers:
        # logger.info("PEER URI: "+p.peerURI)
        # logger.info("|--------------------------------------|")
        return "ok"

    def calcMerkleTree(self, blockToCalculate):
        # print ("received: "+str(blockToCalculate))
        t1 = time.time()
        blk = ChainFunctions.getBlockByIndex(blockToCalculate)
        trans = blk.transactions
        size = len(blk.transactions)
        mt = merkle.MerkleTools()
        mt.add_leaf(trans, True)
        mt.make_tree()
        t2 = time.time()
        logger.info("gateway;" + gatewayName + ";" + consensus + ";T4;Time to compute merkle tree root (size = " + str(size) + ");" + '{0:.12f}'.format((t2 - t1) * 1000))
        return "ok"

    def getRemotePeerBlockChain(self):
        pickledChain = pickle.dumps(ChainFunctions.getFullChain())
        return pickledChain

    def getLastChainBlocks(self, peerURI, lastBlockIndex):
        # Get the missing blocks from orchestrator
        # print("Inside get last chain block...")
        chainSize = ChainFunctions.getBlockchainSize()
        # print("Chainsized: " + str(chainSize))
        if(chainSize > 1):
            newBlock = ChainFunctions.getBlockByIndex(1)
            # print("My Key is: "+ str(newBlock.publicKey) + "My index is" + str(newBlock.index))
        # destinationURI = pickle.loads(peerURI)
        # peerUri= getPeerbyPK(destinationPK)
            sendBlockToPeers(newBlock)
        # print("Inside get last chain block... requested by URI: "+destinationURI)
        # #peer=Pyro4.Proxy(destinationURI)
        # peer = PeerInfo.PeerInfo(destinationURI, Pyro4.Proxy(destinationURI))
        # obj = peer.object
        # print("After creating obj in getlastchain")
        # for index in range(lastBlockIndex+1, chainSize-1):
        #     # logger.debug("sending IoT Block to: " + str(peer.peerURI))
        #     print("Sending to peer"+ str(destinationURI) + "Block Index: "+ str(index) + "chainsize: "+ str(chainSize))
        #     newBlock=ChainFunctions.getBlockByIndex(index)
        #     #dat = pickle.dumps(ChainFunctions.getBlockByIndex(index))
        #     #obj.updateIOTBlockLedger(dat, myName)
        #     obj.ChainFunctions.addBlockHeader(newBlock)

        # print("For finished")

    def getMyOrchestrator(self):
        dat = pickle.dumps(orchestratorObject)
        return dat

    def addVoteOrchestrator(self, sentVote):
        global votesForNewOrchestrator
        dat = pickle.loads(sentVote)
        # print("adding vote in remote peer"+str(dat))
        votesForNewOrchestrator.append(dat)
        # print("finished adding vote for orchetrator")
        return True

    def peerVoteNewOrchestrator(self):
        global myVoteForNewOrchestrator
        global votesForNewOrchestrator
        global peers

        randomGw = random.randint(0, len(peers) - 1)
        # print("random GW??????? : "+ str(randomGw))
        # randomGw=1
        votedURI = peers[randomGw].peerURI
        # print("VotedURI: " + str(votedURI))
        # myVoteForNewOrchestrator = [gwPub, votedURI, CryptoFunctions.signInfo(gwPvt, votedURI)]  # not safe sign, just for test
        myVoteForNewOrchestrator = votedURI
        votesForNewOrchestrator.append(myVoteForNewOrchestrator)
        pickedVote = pickle.dumps(myVoteForNewOrchestrator)
        return pickedVote


    def electNewOrchestrator(self):
        global votesForNewOrchestrator
        global orchestratorObject
        t1 = time.time()
        votesForNewOrchestrator =[]
        for peer in peers:
            obj = peer.object
            # print("objeto criado")
            receivedVote = obj.peerVoteNewOrchestrator()

            votesForNewOrchestrator.append(pickle.loads(receivedVote))
            # logger.info("remote vote for: " + str(pickle.loads(receivedVote)))
        voteNewOrchestrator()
        # newOrchestratorURI = mode(votesForNewOrchestrator)
        newOrchestratorURI = max(
            set(votesForNewOrchestrator), key=votesForNewOrchestrator.count)
        # logger.info("Elected node was" + str(newOrchestratorURI))
        orchestratorObject = Pyro4.Proxy(newOrchestratorURI)
        for peer in peers:
            obj = peer.object
            dat = pickle.dumps(orchestratorObject)
            obj.loadElectedOrchestrator(dat)
        t2 = time.time()
        # logger.info("gateway;" + gatewayName + ";" + consensus + ";T7;Time to execute new election block consensus;" + '{0:.12f}'.format((t2 - t1) * 1000))
        # logger.info("New Orchestator loaded is: " + str(newOrchestratorURI))
        # orchestratorObject

    def loadElectedOrchestrator(self, data):
        global orchestratorObject
        newOrchestrator = pickle.loads(data)
        orchestratorObject = newOrchestrator
        # logger.info("New Orchestator loaded is: " + str(orchestratorObject.exposedURI()))
        # print("new loaded orchestrator: " + str(orchestratorObject.exposedURI()))
        return True


    # Orchestrator voting and election considering contexts
    def peerVoteNewContextOrchestrator(self,context):
        global myVoteForNewContextOrchestrator
        global votesForNewContextOrchestrator
        global contextPeers

        for x in range(len(contextPeers)):
            # print(" ***VVVVV **** context? " +contextPeers[x][0])
            if (contextPeers[x][0] == context):
                tempContextPeers = contextPeers[x][1]

        randomGw = random.randint(0, len(tempContextPeers) - 1)
        # print("random GW??????? : "+ str(randomGw))
        # randomGw=1

        votedURI = tempContextPeers[randomGw].peerURI
        # print("VotedURI: " + str(votedURI))
        contextFound = False
        for i in range(len(myVoteForNewContextOrchestrator)):
            if(context == myVoteForNewContextOrchestrator[i][0]):
                myVoteForNewContextOrchestrator[i][1]= votedURI
                contextFound = True

        if(contextFound == False):
                myVoteForNewContextOrchestrator.append([context, [votedURI]])

        contextFound = False
        for index in range(len(votesForNewContextOrchestrator)):
            if(context == votesForNewContextOrchestrator[index][0]):
                votesForNewContextOrchestrator[index][1].append(votedURI)
                contextFound = True
        if (contextFound == False):
            votesForNewContextOrchestrator.append([context, [votedURI]])

        pickedVote = pickle.dumps(votedURI)
        return pickedVote

    def startCleanVotesContextOrchestrator(self, context):
        global votesForNewContextOrchestrator

        contextFound = False

        for index in range(len(votesForNewContextOrchestrator)):
            if(context == votesForNewContextOrchestrator[index][0]):
                # clean votes
                votesForNewContextOrchestrator[index][1] = []
                contextFound = True
                return True
        if (contextFound == False):

            votesForNewContextOrchestrator.append([context, []])
            return True
        return False

    def loadElectedContextOrchestrator(self, context, data):
        global orchestratorContextObject
        newOrchestrator = pickle.loads(data)
        for orc in range(len(orchestratorContextObject)):
            if (orchestratorContextObject[orc][0] == context):
                orchestratorContextObject[orc][1] = newOrchestrator
        return True

    def electNewContextOrchestrator(self,  context):
        global votesForNewContextOrchestrator
        global orchestratorContextObject
        global contextPeers
        t1 = time.time()
        # print("electing new context orchestrator")
        # votesForNewContextOrchestrator = []
        index = 0
        tempContextPeers = []
        for x in range(len(contextPeers)):
            # print(" ***VVVVV **** context? " +contextPeers[x][0])
            if (contextPeers[x][0] == context):
                tempContextPeers = contextPeers[x][1]

        if(self.startCleanVotesContextOrchestrator(context) == False):
            logger.error("Problem initializing votes for context orchestrator")
        contextFound = False
        index=0
        for index in range(len(votesForNewContextOrchestrator)):
            if(context == votesForNewContextOrchestrator[index][0]):
                # clean votes
                # votesForNewContextOrchestrator[index][1] = []
                contextFound = True
                break
        if (contextFound == False):
            votesForNewContextOrchestrator.append([context, []])
            index=len(votesForNewContextOrchestrator)-1
            logger.error("It should had already been initialized in startClean...")

        for peer in tempContextPeers:
            obj = peer.object
            # print("objeto criado")
            obj.startCleanVotesContextOrchestrator(context)
            receivedVote = obj.peerVoteNewContextOrchestrator(context)

            votesForNewContextOrchestrator[index][1].append(pickle.loads(receivedVote))
            # logger.info("remote vote for: " + str(pickle.loads(receivedVote)))

        self.peerVoteNewContextOrchestrator(context)

        # newOrchestratorURI = mode(votesForNewOrchestrator)
        # print("verifying votes for index: "+str(index) + " ")
        # print(votesForNewContextOrchestrator[index][1])
        newOrchestratorURI = max(set(votesForNewContextOrchestrator[index][1]), key=votesForNewContextOrchestrator[index][1].count)
        # logger.info("Elected node was" + str(newOrchestratorURI))

        # update current context orchestrator in local orchestrator variable
        for orc in range(len(orchestratorContextObject)):
            if(orchestratorContextObject[orc][0]==context):
                orchestratorContextObject[orc][1] = Pyro4.Proxy(newOrchestratorURI)

        # update current context orchestrator in each peer orchestrator variable
        for peer in tempContextPeers:
            obj = peer.object
            dat = pickle.dumps(Pyro4.Proxy(newOrchestratorURI))
            obj.loadElectedContextOrchestrator(context, dat)
        # print("****** Orchestrator for context was elected successfully")


    def exposedURI(self):
        return myURI

    # set context and consensus list for each gateway
    def setContexts(self, receivedContexts):
        global gwContextConsensus
	
	# receivedContexts = pickle.loads(dumpedContexts)
        
	        # @TODO change how contexts are updated
        if (receivedContexts != gwContextConsensus):
             print("Contexts CHANGED!!!!!!!!!!!!!!!!!!!!!!!!!!!")
             gwContextConsensus = receivedContexts
        
        #     # print("Changed my consensus to " + consensus)
             for p in peers:
                 obj = p.object
        
                 dumpedContexts = pickle.dumps(receivedContexts)
                 obj.setContextsRemote(dumpedContexts)

        print("Contexts set: "+ str(gwContextConsensus))
        return True

    def setContextsRemote(self, dumpedContexts):
        global gwContextConsensus

        receivedContexts = pickle.loads(dumpedContexts)
        if (receivedContexts != gwContextConsensus):

            gwContextConsensus = receivedContexts

        # print("Contexts set: " + str(gwContextConsensus))
        return

    def setConsensus(self, receivedConsensus):
        global consensus
        if (receivedConsensus != consensus):
            consensus = receivedConsensus
            # print("######")
            # print("Changed my consensus to " + consensus)
            for p in peers:
                obj = p.object
                obj.setConsensus(receivedConsensus)
        return True

    def runPBFT(self, lifecycleDeviceName):
        """ Run the PBFT consensus to add a new block on the chain """
        # print("I am in runPBFT")
        t1 = float(((time.time()) * 1000) * 1000)
        global gwPvt
        global blockContext
        global gwContextConsensus
        global blkCounter
        global logT5
        devPubKey = getBlockFromSyncList()
        #verififyKeyContext()
        #vblockContext = "0001"
        # set each block with a different context, e.g., based on the rest of division of bc size by number of contexts
        # @TODO define somehow a device is in a context
        # randomContext = random.randrange(0,len(gwContextConsensus))
        # if(len(gwContextConsensus==0)):
        #     logger.error("no contexts" + " My gw name is: " + gatewayName)
        #     blockContext = "9999"
        # else:
        blockContext = gwContextConsensus[(blkCounter % len(gwContextConsensus))][0]
        blkCounter = blkCounter+1
        # if(random.randrange(1,3) == 1):
        #     blockContext = "0001"
        # else:
        #     blockContext = "0002"
            # logger.error("******************Changed to 2****************")
        # blockContext = "0002"

        blk = ChainFunctions.createNewBlock(devPubKey, gwPvt, blockContext, consensus, lifecycleDeviceName)
        # logger.debug("Running PBFT function to block(" + str(blk.index) + ")")

        if ((PBFTConsensus(blk, gwPub, devPubKey, lifecycleDeviceName)) == False):
            logger.error("Consensus not finished")
            return False
        t2 = float(((time.time()) * 1000) * 1000)
        logT5.append("gateway;" + gatewayName + ";" + consensus + ";T5;Time to add a new block with pBFT consensus;" +  str((t2 - t1) / 1000))
        # logT5.append("gateway;" + gatewayName + ";" + consensus + ";T5;Time to add a new block with pBFT consensus;" + '{0:.12f}'.format((t2 - t1) * 1000))
        return True
        # print("Finish PBFT consensus in: "+ '{0:.12f}'.format((t2 - t1) * 1000))

    def rundBFT(self):
        """ Run the dBFT consensus to add a new block on the chain """
        # print("I am in rundBFT")
        t1 = float(((time.time()) * 1000) * 1000)
        global gwPvt
        global blockContext
        global logT5
        global blkCounter
        devPubKey = getBlockFromSyncList()
        #verififyKeyContext()
        #vblockContext = "0001"

        #@TODO define somehow a device is in a context
        blockContext = gwContextConsensus[(blkCounter % len(gwContextConsensus))][0]
        blkCounter = blkCounter+1
        blk = ChainFunctions.createNewBlock(devPubKey, gwPvt, blockContext, consensus)
        # logger.info("after blk, before consensus")
        # logger.debug("Running dBFT function to block(" + str(blk.index) + ")")
        if((PBFTConsensus(blk, gwPub, devPubKey)) == False):
            logger.error("Consensus not finished")
            return False
        # logger.info("Consensus finished")
        t2 = float(((time.time()) * 1000) * 1000)
        logT5.append("gateway;" + gatewayName + ";" + consensus + ";T5;Time to add a new block with dBFT consensus;" + str((t2 - t1) / 1000))
        # logT5.append("gateway;" + gatewayName + ";" + consensus + ";T5;Time to add a new block with dBFT consensus;" + '{0:.12f}'.format((t2 - t1) * 1000))
        return True
        # print("Finish dBFT consensus in: "+ '{0:.12f}'.format((t2 - t1) * 1000))

    def runPoW(self):
        # Consensus PoW
        """ Run the PoW consensus to add a new block on the chain """
        # print("I am in runPoW")
        t1 = float(((time.time()) * 1000) * 1000)
        global gwPvt
        global blockContext
        global logT5
        global blkCounter
        devPubKey = getBlockFromSyncList()
        #verififyKeyContext()
        #vblockContext = "0001"
        #@TODO define somehow a device is in a context
        blockContext = gwContextConsensus[(blkCounter % len(gwContextConsensus))][0]
        blkCounter = blkCounter+1
        blk = ChainFunctions.createNewBlock(devPubKey, gwPvt, blockContext, consensus)
        # print("Device PubKey (insire runPoW): " + str(devPubKey))

        if (PoWConsensus(blk, gwPub, devPubKey)):
            t2 = float(((time.time()) * 1000) * 1000)
            logT5.append("gateway;" + gatewayName + ";" + consensus + ";T5;Time to add a new block with PoW consensus;" + str((t2 - t1) / 1000))
            # logT5.append("gateway;" + gatewayName + ";" + consensus + ";T5;Time to add a new block with PoW consensus;" + '{0:.12f}'.format((t2 - t1) * 1000))
            # # print("Finish PoW consensus in: "+ '{0:.12f}'.format((t2 - t1) * 1000))
        else:
            t2 = float(((time.time()) * 1000) * 1000)
            logger.error("(Something went wrong) time to execute PoW Block Consensus = " +
                         '{0:.12f}'.format((t2 - t1) * 1000))
            # print("I finished runPoW - Wrong")

    def runNoConsesus(self, lifecycleDeviceName):
        # print("Running without consensus")
        t1 = float(((time.time()) * 1000) * 1000)
        global peers
        global blockContext
        global logT5
        global blkCounter
        devPubKey = getBlockFromSyncList()
        #verififyKeyContext()
        #vblockContext = "0001"
        #@TODO define somehow a device is in a context
        blockContext = gwContextConsensus[(blkCounter % len(gwContextConsensus))][0]
        blkCounter = blkCounter+1
        newBlock = ChainFunctions.createNewBlock(devPubKey, gwPvt, blockContext, consensus, lifecycleDeviceName)
        signature = verifyBlockCandidate(newBlock, gwPub, devPubKey, peers)
        if (signature == False):
            logger.info("Consesus was not achieved: block #" +
                        str(newBlock.index) + " will not be added")
            return False
        ChainFunctions.addBlockHeader(newBlock)
        sendBlockToPeers(newBlock)
        t2 = float(((time.time()) * 1000) * 1000)
        logT5.append(
            "gateway;" + gatewayName + ";" + consensus + ";T5;Time to add a new block with no consensus;" + str(
                (t2 - t1) / 1000))
        # logT5.append("gateway;" + gatewayName + ";" + consensus + ";T5;Time to add a new block with none consensus algorithm;" + '{0:.12f}'.format((t2 - t1) * 1000))
        # print("Finish adding Block without consensus in: "+ '{0:.12f}'.format((t2 - t1) * 1000))
        return True

    def runPoA(self):
        # print("Running without consensus")
        t1 = float(((time.time()) * 1000) * 1000)
        global peers
        global blockContext
        global logT5
        global blkCounter
        devPubKey = getBlockFromSyncList()
        #verififyKeyContext()
        #vblockContext = "0001"
        #@TODO define somehow a device is in a context
        blockContext = gwContextConsensus[(blkCounter % len(gwContextConsensus))][0]
        blkCounter = blkCounter+1
        newBlock = ChainFunctions.createNewBlock(devPubKey, gwPvt, blockContext, consensus)
        signature = verifyBlockCandidate(newBlock, gwPub, devPubKey, peers)
        if (signature == False):
            logger.info("Consesus was not achieved: block #" +
                        str(newBlock.index) + " will not be added")
            return False
        ChainFunctions.addBlockHeader(newBlock)
        sendBlockToPeers(newBlock)
        t2 = float(((time.time()) * 1000) * 1000)
        logT5.append(
            "gateway;" + gatewayName + ";" + consensus + ";T5;Time to add a new block with PoA consensus;" + str(
                (t2 - t1) / 1000))
        # logT5.append("gateway;" + gatewayName + ";" + consensus + ";T5;Time to add a new block with none consensus algorithm;" + '{0:.12f}'.format((t2 - t1) * 1000))
        # print("Finish adding Block without consensus in: "+ '{0:.12f}'.format((t2 - t1) * 1000))
        return True

    def lockForConsensus(self):
        """ lock the consensusLock without resulting in deadlocks """

        global consensusLock
        global peers

        counter = 0
        i =0
        while (counter < len(peers)):
            while ((consensusLock.acquire(
                    False) == False)):  # in this mode (with False value) it will lock the execution and return true if it was locked or false if not
                # logger.info("$$$$$$$I can't lock my lock, waiting for it -> in lock for consensus")
                time.sleep(0.01)
            # print("##Before for and after acquire my lock")
                if (i==1000):
                    return False
            for p in peers:
                obj = p.object
                thisPeerIsNotAvailableToLock = obj.acquireLockRemote()
                counter = counter + 1
                # print("On counter = "+str(counter)+" lock result was: "+str(thisPeerIsNotAvailableToLock))
                if (thisPeerIsNotAvailableToLock == False):
                    counter = counter - 1  # I have to unlock the locked ones, the last was not locked
                    # logger.info("$$$$$$$I can't lock REMOTE lock, waiting for it -> in lockforconsensus")
                    # logger.info("Almost got a deadlock")
                    consensusLock.release()
                    if (counter > 0):
                        for p in peers:
                            obj = p.object
                            obj.releaseLockRemote()
                            # logger.info("released lock counter: " + str(counter))
                            counter = counter - 1
                            if (counter == 0):
                                # logger.info("released locks")
                                break
                            # print("After first break PBFT")
                            # logger.info("After first break PBFT")
                    # logger.info("sleeping 0.01")
                    time.sleep(0.01)
                    break
        return True

    def releaseLockForConsensus(self):
        """ lock the consensusLock without resulting in deadlocks """

        global consensusLock
        consensusLock.release()


    # def voteNewOrchestratorExposed(self):
    #     global myVoteForNewOrchestrator
    #     global votesForNewOrchestrator
    #
    #     randomGw = random.randint(0, len(peers) - 1)
    #     votedpubKey = peers[randomGw].object.getGwPubkey()
    #     # print("Selected Gw is: " + str(randomGw))
    #     # print("My pubKey:"+ str(gwPub))
    #     print("VotedpubKey: " + str(votedpubKey))
    #     myVoteForNewOrchestrator = [gwPub, votedpubKey,
    #                                 CryptoFunctions.signInfo(gwPvt, votedpubKey)]  # not safe sign, just for test
    #     votesForNewOrchestrator.append(myVoteForNewOrchestrator)
    #     pickedVote = pickle.dumps(myVoteForNewOrchestrator)
    #     for count in range(0, (len(peers))):
    #         # print("testing range of peers: "+ str(count))
    #         # if(peer != peers[0]):
    #         obj = peers[count].object
    #         obj.addVoteOrchestrator(pickedVote)
    #     return True
    #     # print(str(myVoteForNewOrchestrator))

    # NEW CONSENSUS @Roben

    def verifyBlockCandidateRemote(self, newBlock, askerPubKey, isMulti):
        """ Receive a new block and verify if it's authentic\n
            @param newBlock - BlockHeader object\n
            @param askerPubKey - Public from the requesting peer\n
            @return True - the block is valid\n
            @return False - the block is not valid
        """
        global peers
        newBlock = pickle.loads(newBlock)
        isMulti = pickle.loads(isMulti)
        # logger.debug("|---------------------------------------------------------------------|")
        # logger.debug("Verify for newBlock asked - index:"+str(newBlock.index))
        ret = verifyBlockCandidate(
            newBlock, askerPubKey, newBlock.publicKey, peers, isMulti)
        # logger.debug("validation reulsts:"+str(ret))
        # logger.debug("|---------------------------------------------------------------------|")
        # pi = pickle.dumps(ret)
        return ret

    def addVoteBlockPBFTRemote(self, newBlock, voterPub, voterSign):
        """ add the signature of a peer into the newBlockCandidate,
            using a list to all gw for a single hash,
            if the block is valid put the signature\n

            @param newBlock - BlockHeader object\n
            @param voterPub - Public key from the voting peer\n
            @param voterSign - new block sign key\n
            @return True - addVoteBlockPFDT only return
        """
        # logger.debug("Received remote add vote...")
        return addVoteBlockPBFT(newBlock, voterPub, voterSign)

    def calcBlockPBFTRemote(self, newBlock):
        """ Calculates if PBFT consensus are achived for the block\n
            @param newBlock - BlockHeader object\n
            @return boolean - True for consensus achived, False if it's not.
        """
        # logger.debug("Received remote calcBlock called...")
        global peers
        return calcBlockPBFT(newBlock, peers)

    def getGwPubkey(self):
        """ Return the peer's public key\n
            @return str - public key
        """
        global gwPub
        return gwPub

    def isBlockInTheChain(self, devPubKey):
        """ Verify if a block is on the chain\n
            @param devPubKey - block pub key\n
            @return boolean - True: block found, False: block not found
        """
        blk = ChainFunctions.findBlock(devPubKey)
        # print("Inside inBlockInTheChain, devPumyVoteForNewOrchestratorbKey= " + str(devPubKey))
        if(blk == False):
            # logger.debug("Block is false="+str(devPubKey))
            return False
        else:
            return True


##############################Smart Contracts####################
    def callEVM(self, dumpedType, dumpedData, dumpedFrom, dumpedDest,dumedSignedDatabyDevice,dumpedDevPubKey):
        """ Call a Ethereum Virtual Machine and use a pre-defined set of parameters\n
            @param tipo - type of the call, can be Execute, Create or Call\n
            @param data - It is the binary data of the contract\n
            @param origin - from account\n
            @param dest - destination account\n
            @signedDatabyDevice - device signature for concat tipo,data,origin and dest
            @devPubKey - to verify signature
        """
        # Create a TCP
        # IP socket

        tipo = pickle.loads(dumpedType)
        data = pickle.loads(dumpedData)
        origin = pickle.loads(dumpedFrom)
        dest = pickle.loads(dumpedDest)
        signedDatabyDevice=pickle.loads(dumedSignedDatabyDevice)
        devPubKey = pickle.loads(dumpedDevPubKey)


        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Coleta o data da ultima transacao um json
        scBlock = ChainFunctions.findBlock(devPubKey)
        ultimaTrans = ChainFunctions.getLatestBlockTransaction(scBlock).data.strInfoData()
        ultimaTransJSON = json.loads(ultimaTrans)
        transAtual = json.loads(
            '{"Tipo":"%s","Data":"%s","From":"%s","To":"%s"}' % (tipo, data, origin, dest))

        chamada = '{"Tipo":"%s","Data":"%s","From":"%s","To":"%s","Root":"%s"}' % (
            transAtual['Tipo'], transAtual['Data'], transAtual['From'], transAtual['To'], ultimaTransJSON['Root'])
        # chamada =  '{"Tipo":"%s","Data":"%s","From":null,"To":null,"Root":"%s"}' % (transAtual['Tipo'], transAtual['Data'], ultimaTransJSON['Root'])
        chamadaJSON = json.loads(chamada)
        # print("antes do try")
        # chamada = '{"Tipo":"Exec","Data":"YAFgQFNgAWBA8w==","From":null,"To":null,"Root":null}'  # Comentar
        # chamadaJSON = json.loads(chamada)  # Comentar
        try:
            # Tamanho maximo do JSON 6 caracteres
            # print("AQUI 00001")
            s.connect(('localhost', 6666))
            #print("AQUI 000016666")
            tamanhoSmartContract = str(len(chamada))
            for i in range(6 - len(tamanhoSmartContract)):
                tamanhoSmartContract = '0' + tamanhoSmartContract
            # print("Enviando tamanho " + tamanhoSmartContract + "\n")
            # Envia o SC
            # print("AQUI 00002")
            s.send(tamanhoSmartContract)
            time.sleep(1)
            # print(json.dumps(chamadaJSON))
            s.send(chamada)
            # print("AQUI 000003")
            # Recebe tamanho da resposta
            tamanhoResposta = s.recv(6)
            # print("Tamanho da resposta: " + tamanhoResposta)
            # Recebe resposta
            resposta = s.recv(int(tamanhoResposta))
            # print(resposta + "\n")
            # print("AQUI 1")
            # Decodifica resposta
            respostaJSON = json.loads(resposta)
            # print(respsotaJSON['Ret'])
            if respostaJSON['Erro'] != "":
                logger.Exception("Transaction not inserted")
            elif chamadaJSON['Tipo'] == "Exec":
                # print("AQUI 2")
                logger.info("Execution, without data insertion on blockchain")
            else:
                transacao = '{ "Tipo" : "%s", "Data": "%s", "From": "%s", "To" : "%s", "Root" : "%s" }' % (
                    chamadaJSON['Tipo'], chamadaJSON['Data'], chamadaJSON['From'], chamadaJSON['To'],
                    respostaJSON['Root'])
                logger.info("Trasaction being inserted: %s \n" % transacao)
                t = ((time.time() * 1000) * 1000)
                timeStr = "{:.0f}".format(t)
                data = timeStr + transacao+signedDatabyDevice
                signedData = CryptoFunctions.signInfo(gwPvt, data)
                logger.debug("###Printing Signing Smart Contract Data before sending: " + signedData)
                #print("I am Here before SC")
                self.addTransactionSC2(transacao, signedDatabyDevice, devPubKey, timeStr)
            # pass

        finally:
            # print("fim\n")
            s.close()
        return True

#############################################################################
#############################################################################
##############         INIT Lifecycle Events (Rodrigo)         ##############
#############################################################################
#############################################################################

    def getDeviceName(self):
        global deviceName
        return deviceName
    
    def storeChainToFile(self):
        """ Store the entire chain to a text file
            The gateway keys from all peers
            The blocks and the transactions\n
        """
        self.storeNormalChainToFile()
        self.storeMultiChainToFile()

    def storeNormalChainToFile(self):
        open(chainFile, 'w').close()
        f = open(chainFile, "a")
        storeKeysFromPeers(f)

        f.write("\n")

        theChain = ChainFunctions.getFullChain()
        for b in theChain[1:]:
            block = b.strBlockToSave()
            #print("block= " + block)
            f.write("block= " + block + "\n")
            for t in b.transactions[1:]:
                transaction = t.strTransactionToSave()
                #print("transaction= " + transaction)
                f.write("transaction= " + transaction + "\n")
        f.close()
        return True

    def storeMultiChainToFile(self):
        open(chainFileMulti, 'w').close()
        f = open(chainFileMulti, "a")

        theChain = ChainFunctionsMulti.getFullChain()
        for b in theChain[1:]:
            block = b.strBlockToSave()
            #print("block= " + block)
            f.write("block= " + block + "\n")
            for i in range(b.numTransactionChains):
                for t in b.transactions[i][1:]:
                    transaction = t.strTransactionToSave()
                    #print("transaction " + str(i) + "= " + transaction)
                    f.write("transaction " + str(i) + "= " + transaction + "\n")
        f.close()
        return True

    def restoreChainFromFile(self):
        """ Store the entire chain to a text file
            The gateway keys from all peers
            The blocks and the transactions\n
        """
        t1 = time.time()
        self.restoreNormalChainFromFile()
        self.restoreMultiChainFromFile()
        t2 = time.time()
        timeDiff = '{0:.12f}'.format((t2 - t1) * 1000)
        return timeDiff
    
    def restoreNormalChainFromFile(self):
        """ Restore the entire chain from a text file
            The gateway keys from all peers
            The blocks and the transactions\n
        """
        keys = []
        f = open(chainFile, "r")

        # Gets public and private key from each gateway
        for line in f:
            stripped_line = line.rstrip('\n')
            #print("line = " + str(stripped_line))
            if (str(stripped_line) == ""):
                #print("BREAK!")
                break
            split = stripped_line.split('  ')
            publicKey = split[0].replace('\\n', '\n')
            privateKey = split[1].replace('\\n', '\n')
            key = [publicKey, privateKey]
            #print("Public Key = " + str(publicKey))
            #print("Private Key = " + str(privateKey))
            keys.append(key)
        
        #print (keys)
        # Get how many peers from file
        # Get gw private/public keys, send them to each peer
            # Each peer updates its keys and restart the chain (ChainFunctions.restartChain())
        restartChains(keys)
        
        # Gets the blocks/transations
        devPubKey = ""
        for line in f:
            #print ("")
            stripped_line = line.rstrip('\n')
            split_aux = stripped_line.split('= ', 1)
            split = split_aux[1].split('  ')
            #print(str(stripped_line))
            if (stripped_line.startswith('block')):
                devPubKey = split[0].replace('\\n', '\n')
                #print("Dev Public Key = " + str(devPubKey))
                blockContext = split[1]
                timestamp = split[2]
                nonce = split[3]
                signature = split[4]
                blockData = split[5]
                index = int(split[6])
                device = split[7]
                previousExpiredBlockHash = split[8]
                previousBlockSignature = split[9]
                newBlock = ChainFunctions.generateNextBlock2(blockData, devPubKey, signature, blockContext, 
                                                             timestamp, nonce, index, device, 
                                                             previousExpiredBlockHash, previousBlockSignature)
                ChainFunctions.addBlockHeader(newBlock)
                #print(newBlock.strBlock())
                sendBlockToPeers(newBlock)
            if (stripped_line.startswith('transaction')):
                blk = ChainFunctions.findBlock(devPubKey)        
                if (blk != False and blk.index > 0):
                    #print("Block found!")
                    nextInt = blk.transactions[len(blk.transactions) - 1].index + 1
                    prevInfoHash = (ChainFunctions.getLatestBlockTransaction(blk)).hash
                    #print("Timestamp = " + str(split[0]))
                    #print("Device info = " + str(split[1]))
                    #print("Sign data = " + str(split[2]))
                    #print("Nonce = " + str(split[3]))

                    deviceInfoSplit = split[1].split(", ")
                    deviceInfo = ""
                    if (deviceInfoSplit.count == 1):
                        deviceInfo = split[1]
                    else:
                        deviceInfo = LifecycleEvent.LifecycleEvent(
                            deviceInfoSplit[1], deviceInfoSplit[2],  deviceInfoSplit[3], deviceInfoSplit[0])
                    transaction = Transaction.Transaction(
                        nextInt, prevInfoHash, split[0], deviceInfo, split[2], split[3], split[4])

                    ChainFunctions.addBlockTransaction(blk, transaction)
                    #print(transaction.strBlock())
                    sendTransactionToPeers(devPubKey, transaction)

        f.close()
        return True
    
    def restoreMultiChainFromFile(self):
        """ Restore the entire chain from a text file
            The gateway keys from all peers
            The blocks and the transactions\n
        """
        f = open(chainFileMulti, "r")
        
        # Gets the blocks/transations
        devPubKey = ""
        for line in f:
            #print ("")
            stripped_line = line.rstrip('\n')
            split_aux = stripped_line.split('= ', 1)
            split = split_aux[1].split('  ')
            #print(str(stripped_line))
            if (stripped_line.startswith('block')):
                devPubKey = split[0].replace('\\n', '\n')
                #print("Dev Public Key = " + str(devPubKey))
                blockContext = split[1]
                timestamp = split[2]
                nonce = split[3]
                signature = split[4]
                blockData = split[5]
                numTransactionChains = split[6]
                index = int(split[7])
                device = split[8]
                previousExpiredBlockHash = split[9]
                previousBlockSignature = split[10]
                newBlock = ChainFunctionsMulti.generateNextBlock2(blockData, devPubKey, signature, blockContext, 
                                                timestamp, nonce, numTransactionChains, index, device, 
                                                previousExpiredBlockHash, previousBlockSignature)
                ChainFunctionsMulti.addBlockHeader(newBlock)
                #print("NewBlock: " + newBlock.strBlock())
                sendBlockToPeersMulti(newBlock)
            if (stripped_line.startswith('transaction')):
                chainIndexList = [int(x) for x in split_aux[0].split() if x.isdigit()]
                chainIndex = chainIndexList[0]
                #print("ChainIndex = " + str(chainIndex))
                blk = ChainFunctionsMulti.findBlock(devPubKey)      
                if (blk != False and blk.index > 0):
                    #print("Block found!")
                    lastBlk = (ChainFunctionsMulti.getLatestBlockTransaction(blk, chainIndex))
                    nextInt = lastBlk.index + 1
                    prevInfoHash = lastBlk.hash
                    #print("Timestamp = " + str(split[0]))
                    #print("Device info = " + str(split[1]))
                    #print("Sign data = " + str(split[2]))
                    #print("Nonce = " + str(split[3]))
                    transaction = Transaction.Transaction(
                        nextInt, prevInfoHash, split[0], split[1], split[2], split[3], split[4])

                    ChainFunctionsMulti.addBlockTransaction(blk, transaction, chainIndex)
                    #print(transaction.strBlock())
                    sendTransactionToPeersMulti(devPubKey, transaction, chainIndex)

        f.close()
        return True

    def updateGatewayKeys(self, pubKey, privKey, gwName):
        """ Update the gateway private and public keys, receiving it on restore from file\n
            @param pubKey - the public key to be added\n
            @param privKey - the private key to be added\n
            @param gwName - the name of the gateway that sent the keys\n
        """
        global gwPub
        global gwPvt

        #print("Received from = "+ str(gwName))
        pubKey = pickle.loads(pubKey)
        privKey = pickle.loads(privKey)
        #print("Public Key = "+ str(pubKey))
        #print("Private Key = "+ str(privKey))
        t1 = time.time()
        
        gwPub = pubKey
        gwPvt = privKey
        #print("gwPub = "+ str(gwPub))
        #print("gwPvt = "+ str(gwPvt))
        ChainFunctions.restartChain()
        ChainFunctionsMulti.restartChain()
        #blk = ChainFunctions.getLatestBlock()
        #print("BlockGenesis = "+ str(blk.strBlock()))
        #blk = ChainFunctionsMulti.getLatestBlock()
        #print("BlockGenesis = "+ str(blk.strBlock()))

        t2 = time.time()
        # print("updating was done")
        logger.info("gateway;" + gatewayName + ";" + consensus + ";T3;Time to update keys;" + '{0:.12f}'.format((t2 - t1) * 1000))

    def storeGatewayKeys(self, gwName):
        """ Store the gateway keys to the text file\n
            @param gwName - the name of the gateway that will store the keys\n
        """
        # print("Received from = "+ str(gwName))

        f = open(chainFile, "a")
        
        #print("gwPub = "+ str(gwPub))
        #print("gwPvt = "+ str(gwPvt))

        pub = gwPub.replace('\n', '\\n')
        pvt = gwPvt.replace('\n', '\\n')

        f.write(pub + "  " + pvt + "\n")

        f.close()
    
    def addLifecycleEvent(self, devPublicKey, encryptedObj):
        """ Receive a new transaction to be add to the chain, add the transaction
            to a block and send it to all peers\n
            @param devPublicKey - Public key from the sender device\n
            @param encryptedObj - Info of the transaction encrypted with AES 256\n
            @return "ok!" - all done\n
            @return "Invalid Signature" - an invalid key are found\n
            @return "Key not found" - the device's key are not found
        """
        # logger.debug("Transaction received")
        global gwPvt
        global gwPub
        t1 = time.time()
        blk = ChainFunctions.findBlock(devPublicKey)
        
        if (blk != False and blk.index > 0):
            devAESKey = findAESKey(devPublicKey)
            if (devAESKey != False):
                #logger.info("Appending transaction to block #" + str(blk.index) + "...")
                print("Appending transaction to block #" + str(blk.index) + "...")
                # plainObject contains [Signature + Time + Data]

                plainObject = CryptoFunctions.decryptAES(
                    encryptedObj, devAESKey)
                #print("plainObject = " + str(plainObject))
                split = plainObject.split()
                signature = split[0]  #plainObject[:88] # get first 88 chars      #signature = plainObject[:-20]  # remove the last 20 chars
                #print("signature = " + str(signature))
                # remove the 16 char of timestamp
                devTime = split[1]  # plainObject[88:104]
                #print("devTime = " + str(devTime))
                # retrieve the last chars which are the data
                deviceData = split[2]  # plainObject[104:]
                #print("deviceData = " + str(deviceData))

                d = " "+devTime+" "+deviceData
                isSigned = CryptoFunctions.signVerify(
                    d, signature, devPublicKey)

                if isSigned:
                    deviceInfo = DeviceInfo.DeviceInfo(
                        signature, devTime, deviceData)
                    nextInt = blk.transactions[len(
                        blk.transactions) - 1].index + 1
                    signData = CryptoFunctions.signInfo(gwPvt, str(deviceInfo))
                    gwTime = "{:.0f}".format(((time.time() * 1000) * 1000))
                    # code responsible to create the hash between Info nodes.
                    prevInfoHash = (ChainFunctions.getLatestBlockTransaction(blk)).hash
                    
                    transaction = Transaction.Transaction(
                        nextInt, prevInfoHash, gwTime, deviceInfo, signData,0)
                    #transaction.setHash(CryptoFunctions.calculateTransactionHash(transaction))
                    # send to consensus
                    # if not consensus(newBlockLedger, gwPub, devPublicKey):
                    #    return "Not Approved"
                    # if not PBFTConsensus(blk, gwPub, devPublicKey):
                    #     return "Consensus Not Reached"

                    ChainFunctions.addBlockTransaction(blk, transaction)
                    # logger.debug("Block #" + str(blk.index) + " added locally")
                    # logger.debug("Sending block #" +
                    #             str(blk.index) + " to peers...")
                    t2 = time.time()
                    logger.info("gateway;" + gatewayName + ";" + consensus + ";T1;Time to add a new transaction in a block;" + '{0:.12f}'.format((t2 - t1) * 1000))
                    currentTimestamp = float(((time.time()) * 1000) * 1000)
                    logger.info(
                        "gateway;" + gatewayName + ";T20;Transaction Latency;" + str(
                            (currentTimestamp - float(devTime)) / 1000))
                    logger.info(
                        "gateway;" + gatewayName  + ";T26;First Transaction Latency;" + str(
                            (currentTimestamp - float(devTime)) / 1000))
                    
                    # --->> this function should be run in a different thread.
                    sendTransactionToPeers(devPublicKey, transaction)
                    # print("all done")
                    return "ok!"
                else:
                    # logger.debug("--Transaction not appended--Transaction Invalid Signature")
                    return "Invalid Signature"
            # logger.debug("--Transaction not appended--Key not found")
            return "key not found"
        logger.error("key not found when adding transaction")
        # self.removeLockfromContext(devPublicKey)
        return "block false"

    def addLifecycleEventStructure(self, devPublicKey, encryptedObj, type):
        """ Receive a new transaction to be add to the chain, 
            the data will be created as a LifecycleEvent structure
            add the transaction to a block and send it to all peers\n
            @param devPublicKey - Public key from the sender device\n
            @param encryptedObj - Info of the transaction encrypted with AES 256\n
            @return "ok!" - all done\n
            @return "Invalid Signature" - an invalid key are found\n
            @return "Key not found" - the device's key are not found
        """
        # logger.debug("Transaction received")
        global gwPvt
        global gwPub
        t1 = time.time()
        blk = ChainFunctions.findBlock(devPublicKey)
        
        if (blk != False and blk.index > 0):
            devAESKey = findAESKey(devPublicKey)
            if (devAESKey != False):
                #logger.info("Appending transaction to block #" + str(blk.index) + "...")
                # print("Appending transaction to block #" + str(blk.index) + "...")
                # plainObject contains [Signature + Time + Data]

                plainObject = CryptoFunctions.decryptAES(
                    encryptedObj, devAESKey)
                #print("plainObject = " + str(plainObject))
                split = plainObject.split()
                signature = split[0]  #plainObject[:88] # get first 88 chars
                #print("signature = " + str(signature))
                # remove the 16 char of timestamp
                devTime = split[1]  # plainObject[88:104]
                #print("devTime = " + str(devTime))
                #print(devTime)
                # retrieve the last chars which are the data
                deviceData = split[2]  # plainObject[104:]
                #print("deviceData = " + str(deviceData))

                d = " "+devTime+" "+deviceData
                isSigned = CryptoFunctions.signVerify(
                    d, signature, devPublicKey)

                if isSigned:
                    deviceInfo = DeviceInfo.DeviceInfo(
                        signature, devTime, deviceData)
                    #print("DeviceInfo: "+str(deviceInfo))
                    #print(deviceInfo)
                    matching = [s for s in componentsId if type in s]
                    lifecycleEvent = LifecycleEvent.LifecycleEvent(type, matching[0], deviceInfo)
                    #print("LifecycleEvent: "+str(lifecycleEvent.strEvent()))
                    #print(lifecycleEvent)

                    nextInt = blk.transactions[len(
                        blk.transactions) - 1].index + 1
                    signData = CryptoFunctions.signInfo(gwPvt, str(deviceInfo))
                    gwTime = "{:.0f}".format(((time.time() * 1000) * 1000))
                    #print("gwTime: "+str(gwTime))
                    #print(gwTime)
                    # code responsible to create the hash between Info nodes.
                    prevInfoHash = (ChainFunctions.getLatestBlockTransaction(blk)).hash
                    
                    transaction = Transaction.Transaction(
                        nextInt, prevInfoHash, gwTime, lifecycleEvent, signData, 0, matching[0])
                    #print("Transaction: "+str(transaction.strBlock()))
                    #print(transaction)
                    #transaction.setHash(CryptoFunctions.calculateTransactionHash(transaction))
                    # send to consensus
                    # if not consensus(newBlockLedger, gwPub, devPublicKey):
                    #    return "Not Approved"
                    # if not PBFTConsensus(blk, gwPub, devPublicKey):
                    #     return "Consensus Not Reached"

                    ChainFunctions.addBlockTransaction(blk, transaction)
                    # logger.debug("Block #" + str(blk.index) + " added locally")
                    # logger.debug("Sending block #" +
                    #             str(blk.index) + " to peers...")
                    t2 = time.time()
                    logger.info("gateway;" + gatewayName + ";" + consensus + ";T1;Time to add a new transaction in a block;" + '{0:.12f}'.format((t2 - t1) * 1000))
                    currentTimestamp = float(((time.time()) * 1000) * 1000)
                    logger.info("gateway;" + gatewayName + ";T20;Transaction Latency;" + str(
                            (currentTimestamp - float(devTime)) / 1000))
                    logger.info("gateway;" + gatewayName  + ";T26;First Transaction Latency;" + str(
                            (currentTimestamp - float(devTime)) / 1000))
                    # --->> this function should be run in a different thread.
                    sendTransactionToPeers(devPublicKey, transaction)
                    #print("all done")
                    return "ok!"
                else:
                    # logger.debug("--Transaction not appended--Transaction Invalid Signature")
                    return "Invalid Signature"
            # logger.debug("--Transaction not appended--Key not found")
            return "key not found"
        logger.error("key not found when adding transaction")
        # self.removeLockfromContext(devPublicKey)
        return "block false"
    
    def addLifecycleEventMulti(self, devPublicKey, encryptedObj, type, index):
        """ Receive a new transaction to be add to the chain, 
            the data will be created as a LifecycleEvent structure
            add the transaction to a block and send it to all peers\n
            @param devPublicKey - Public key from the sender device\n
            @param encryptedObj - Info of the transaction encrypted with AES 256\n
            @param type - Type of the transaction\n
            @param index - Transaction chain index\n
            @return "ok!" - all done\n
            @return "Invalid Signature" - an invalid key are found\n
            @return "Key not found" - the device's key are not found
        """
        # logger.debug("Transaction received")
        #print("Transaction received on addLifecycleEventMulti")
        global gwPvt
        global gwPub
        t1 = time.time()
        blk = ChainFunctionsMulti.findBlock(devPublicKey)
        
        if (blk != False and blk.index > 0):
            devAESKey = findAESKey(devPublicKey)
            if (devAESKey != False):
                #logger.info("Appending transaction to block #" + str(blk.index) + "...")
                # print("Appending transaction to block #" + str(blk.index) + "...")
                # plainObject contains [Signature + Time + Data]

                plainObject = CryptoFunctions.decryptAES(
                    encryptedObj, devAESKey)
                # print("plainObject = " + str(plainObject))
                split = plainObject.split()
                signature = split[0]  #plainObject[:88] # get first 88 chars
                # print("signature = " + str(signature))
                # remove the 16 char of timestamp
                devTime = split[1]  # plainObject[88:104]
                # print("devTime = " + str(devTime))
                # retrieve the last chars which are the data
                deviceData = split[2]  # plainObject[104:]
                # print("deviceData = " + str(deviceData))
                d = " "+devTime+" "+deviceData
                isSigned = CryptoFunctions.signVerify(
                    d, signature, devPublicKey)
                
                if isSigned:
                    deviceInfo = DeviceInfo.DeviceInfo(
                        signature, devTime, deviceData)
                    matching = [s for s in componentsId if type in s]
                    lifecycleEvent = LifecycleEvent.LifecycleEvent(type, matching[0], deviceInfo)
                    # print("LifecycleEvent: "+str(lifecycleEvent.strEvent()))

                    nextInt = (ChainFunctionsMulti.getLatestBlockTransaction(blk, index)).index + 1
                    signData = CryptoFunctions.signInfo(gwPvt, str(deviceInfo))
                    gwTime = "{:.0f}".format(((time.time() * 1000) * 1000))
                    # code responsible to create the hash between Info nodes.
                    prevInfoHash = (ChainFunctionsMulti.getLatestBlockTransaction(blk, index)).hash
                    
                    transaction = Transaction.Transaction(
                        nextInt, prevInfoHash, gwTime, lifecycleEvent, signData, 0, matching[0])
                    # print("Transaction: "+str(transaction.strBlock()))
                    #transaction.setHash(CryptoFunctions.calculateTransactionHash(transaction))
                    # send to consensus
                    # if not consensus(newBlockLedger, gwPub, devPublicKey):
                    #    return "Not Approved"
                    # if not PBFTConsensus(blk, gwPub, devPublicKey):
                    #     return "Consensus Not Reached"

                    ChainFunctionsMulti.addBlockTransaction(blk, transaction, index)
                    # logger.debug("Block #" + str(blk.index) + " added locally")
                    # logger.debug("Sending block #" +
                    #             str(blk.index) + " to peers...")
                    t2 = time.time()
                    logger.info("gateway;" + gatewayName + ";" + consensus + ";T1;Time to add a new transaction in a block;" + '{0:.12f}'.format((t2 - t1) * 1000))
                    currentTimestamp = float(((time.time()) * 1000) * 1000)
                    logger.info("gateway;" + gatewayName + ";T20;Transaction Latency;" + str(
                            (currentTimestamp - float(devTime)) / 1000))
                    logger.info("gateway;" + gatewayName  + ";T26;First Transaction Latency;" + str(
                            (currentTimestamp - float(devTime)) / 1000))
                    # --->> this function should be run in a different thread.
                    sendTransactionToPeersMulti(devPublicKey, transaction, index)
                    # print("all done")
                    return "ok!"
                else:
                    # logger.debug("--Transaction not appended--Transaction Invalid Signature")
                    return "Invalid Signature"
            # logger.debug("--Transaction not appended--Key not found")
            return "key not found"
        logger.error("key not found when adding transaction")
        # self.removeLockfromContext(devPublicKey)
        return "block false"

    def addLifecycleEventSingle(self, devPublicKey, encryptedObjs, types):
        """ Receive a new transaction to be add to the chain, 
            the data will be created as a LifecycleEvent structure
            add the transaction to a block and send it to all peers\n
            @param devPublicKey - Public key from the sender device\n
            @param encryptedObj - Info of the transaction encrypted with AES 256\n
            @return "ok!" - all done\n
            @return "Invalid Signature" - an invalid key are found\n
            @return "Key not found" - the device's key are not found
        """
        # logger.debug("Transaction received")
        global gwPvt
        global gwPub
        t1 = time.time()
        blk = ChainFunctions.findBlock(devPublicKey)
        lifecycleEvents = []
        if (blk != False and blk.index > 0):
            devAESKey = findAESKey(devPublicKey)
            if (devAESKey != False):
                #logger.info("Appending transaction to block #" + str(blk.index) + "...")
                print("Appending transaction to block #" + str(blk.index) + "...")
                for i in range(4):
                    # plainObject contains [Signature + Time + Data]

                    plainObject = CryptoFunctions.decryptAES(
                        encryptedObjs[i], devAESKey)
                    #print("plainObject = " + str(plainObject))
                    split = plainObject.split()
                    signature = split[0]  #plainObject[:88] # get first 88 chars
                    #print("signature = " + str(signature))
                    # remove the 16 char of timestamp
                    devTime = split[1]  # plainObject[88:104]
                    #print("devTime = " + str(devTime))
                    #print(devTime)
                    # retrieve the last chars which are the data
                    deviceData = split[2]  # plainObject[104:]
                    #print("deviceData = " + str(deviceData))

                    d = " "+devTime+" "+deviceData
                    isSigned = CryptoFunctions.signVerify(
                        d, signature, devPublicKey)

                    if isSigned:
                        deviceInfo = DeviceInfo.DeviceInfo(
                            signature, devTime, deviceData)
                        #print("DeviceInfo: "+str(deviceInfo))
                        matching = [s for s in componentsId if types[i] in s]
                        lifecycleEvents.append(LifecycleEvent.LifecycleEvent(types[i], matching[0], deviceInfo))
                        #print("LifecycleEvent: "+str(lifecycleEvents[i].strEvent()))
                            
                    else:
                        # logger.debug("--Transaction not appended--Transaction Invalid Signature")
                        return "Invalid Signature"
                
                if isSigned:
                    nextInt = blk.transactions[len(
                        blk.transactions) - 1].index + 1
                    signData = CryptoFunctions.signInfo(gwPvt, str(lifecycleEvents))
                    gwTime = "{:.0f}".format(((time.time() * 1000) * 1000))
                    #print("gwTime: "+str(gwTime))
                    #print(gwTime)
                    # code responsible to create the hash between Info nodes.
                    prevInfoHash = (ChainFunctions.getLatestBlockTransaction(blk)).hash
                    transaction = Transaction.Transaction(
                        nextInt, prevInfoHash, gwTime, lifecycleEvents, signData, 0, "")
                    #print("Transaction: "+str(transaction.strBlock()))
                    #transaction.setHash(CryptoFunctions.calculateTransactionHash(transaction))
                    # send to consensus
                    # if not consensus(newBlockLedger, gwPub, devPublicKey):
                    #    return "Not Approved"
                    # if not PBFTConsensus(blk, gwPub, devPublicKey):
                    #     return "Consensus Not Reached"

                    ChainFunctions.addBlockTransaction(blk, transaction)
                    # logger.debug("Block #" + str(blk.index) + " added locally")
                    # logger.debug("Sending block #" +
                    #             str(blk.index) + " to peers...")
                    t2 = time.time()
                    logger.info("gateway;" + gatewayName + ";" + consensus + ";T1;Time to add a new transaction in a block;" + '{0:.12f}'.format((t2 - t1) * 1000))
                    currentTimestamp = float(((time.time()) * 1000) * 1000)
                    logger.info("gateway;" + gatewayName + ";T20;Transaction Latency;" + str(
                            (currentTimestamp - float(devTime)) / 1000))
                    logger.info("gateway;" + gatewayName  + ";T26;First Transaction Latency;" + str(
                            (currentTimestamp - float(devTime)) / 1000))
                    # --->> this function should be run in a different thread.
                    sendTransactionToPeers(devPublicKey, transaction)
                    #print("all done")
                    return "ok!"      
            # logger.debug("--Transaction not appended--Key not found")
            return "key not found"
        logger.error("key not found when adding transaction")
        # self.removeLockfromContext(devPublicKey)
        return "block false"

    def addBlockMulti(self, devPubKey, lifecycleDeviceName):
        """ Receive a device public key from a device and link it to a block on the chain\n
            @param devPubKey - request's device public key\n
            @param deviceName - Name of the device that created the block\n
            @return encKey - RSA encrypted key for the device be able to communicate with the peers
        """
        global gwPub
        global consensusLock
        global orchestratorObject
        #print("addingblock... DevPubKey:" + devPubKey)
        # logger.debug("|---------------------------------------------------------------------|")
        # logger.info("Block received from device")
        aesKey = ''
        encKey = ''
        t1 = time.time()
        blk = ChainFunctionsMulti.findBlock(devPubKey)
        #print("consensus:" + str(consensus))
        if (blk != False and blk.index > 0):
            #print("blk:" + str(blk.index))
            #print("inside first if")
            logger.error("It may be already be registered, generating another aeskey")
            aesKey = findAESKey(devPubKey)
            logger.error("passed by findAESKEY")
            if ((aesKey == False) or (len(aesKey) != 32)):
                logger.error("aeskey had a problem...")
                removeAESKey(aesKey)
                aesKey = generateAESKey(blk.publicKey)
                encKey = CryptoFunctions.encryptRSA2(devPubKey, aesKey)
                return encKey
                # t2 = time.time()
            logger.error("actually it didn't had problem with the key")
            logger.error("publick key received was: " + str(devPubKey) + "blk key was: " + str(blk.publicKey) + " ...")
            removeAESKey(aesKey)
            aesKey = generateAESKey(blk.publicKey)
            encKey = CryptoFunctions.encryptRSA2(devPubKey, aesKey)
            return encKey
            # t2 = time.time()
        else:
            #print("inside else")
            # logger.debug("***** New Block: Chain size:" +
            #              str(ChainFunctions.getBlockchainSize()))
            pickedKey = pickle.dumps(devPubKey)
            aesKey = generateAESKey(devPubKey)
            # print("pickedKey: ")
            # print(pickedKey)

            encKey = CryptoFunctions.encryptRSA2(devPubKey, aesKey)
            # t2 = time.time()
            # Old No Consensus
            # bl = ChainFunctions.createNewBlock(devPubKey, gwPvt)
            # sendBlockToPeers(bl)
            # logger.debug("starting block consensus")
            #############LockCONSENSUS STARTS HERE###############
            if(consensus == "PBFT"):
                #print("Running PBFT consensus for MULTI")
                # PBFT elect new orchestator every time that a new block should be inserted
                # allPeersAreLocked = False
                self.lockForConsensus()
                # print("ConsensusLocks acquired!")
                self.electNewOrchestrator()
                # print("New Orchestrator URI: " + str(orchestratorObject.exposedURI()))
                orchestratorObject.addBlockConsensusCandidate(pickedKey)
                counter_fails = 0
                while(orchestratorObject.runPBFTMulti(lifecycleDeviceName)==False):
                    # logger.info("##### second attmept for a block")
                    orchestratorObject.removeBlockConsensusCandidate(pickedKey)
                    # print("$$$$$$$second trial")
                    self.electNewOrchestrator()
                    orchestratorObject.addBlockConsensusCandidate(pickedKey)
                    counter_fails = counter_fails + 1
                    if (counter_fails > 200):
                        return -1
            if(consensus == "dBFT" or consensus == "Witness3"):
                # print("indo pro dbft")
                # consensusLock.acquire(1) # only 1 consensus can be running at same time
                # for p in peers:
                #     obj=p.object
                #     obj.acquireLockRemote()
                self.lockForConsensus()

                orchestratorObject.addBlockConsensusCandidate(pickedKey)
                # print("blockadded!")
                counter_fails = 0
                while (orchestratorObject.rundBFT() == False):
                    # logger.info("##### second attempt for a block")
                    orchestratorObject.removeBlockConsensusCandidate(pickedKey)
                    logger.error("Consensus not achieved, trying another one")
                    self.electNewOrchestrator()
                    orchestratorObject.addBlockConsensusCandidate(pickedKey)
                    counter_fails = counter_fails +1
                    if (counter_fails > 200):
                        return -1
                # print("after rundbft")
            if(consensus == "PoW"):
                # consensusLock.acquire(1) # only 1 consensus can be running at same time
                # for p in peers:
                #     obj=p.object
                #     obj.acquireLockRemote()
                self.lockForConsensus()
                # print("ConsensusLocks acquired!")
                self.addBlockConsensusCandidate(pickedKey)
                self.runPoW()
            if(consensus == "None"):
                #print("inside NONE consensus")
                self.addBlockConsensusCandidate(pickedKey)
                self.runNoConsesusMulti(lifecycleDeviceName)
            if(consensus == "PoA"):
                self.lockForConsensus()
                self.addBlockConsensusCandidate(pickedKey)
                self.runPoA()

            # print("after orchestratorObject.addBlockConsensusCandidate")
            # try:
            # PBFTConsensus(bl, gwPub, devPubKey)
            # except KeyboardInterrupt:
            #     sys.exit()
            # except:
            #     print("failed to execute:")
            #     logger.error("failed to execute:")
            #     exc_type, exc_value, exc_traceback = sys.exc_info()
            #     print "*** print_exception:"    l
            #     traceback.print_exception(exc_type, exc_value, exc_traceback,
            #                           limit=6, file=sys.stdout)
            #
            # logger.debug("end block consensus")
            # try:
            #     #thread.start_new_thread(sendBlockToPeers,(bl))
            #     t1 = sendBlks(1, bl)
            #     t1.start()
            # except:
            #     print "thread not working..."

            if(consensus == "PBFT" or consensus == "dBFT" or consensus == "Witness3" or consensus == "PoW"):
                self.releaseLockForConsensus()
                for p in peers:
                    obj = p.object
                    obj.releaseLockRemote()
                # print("ConsensusLocks released!")
            ######end of lock consensus################

        # print("Before encription of rsa2")

        t3 = time.time()
        # logger.info("gateway;" + gatewayName + ";" + consensus + ";T1;Time to generate key;" + '{0:.12f}'.format((t2 - t1) * 1000))
        logT6.append("gateway;" + gatewayName + ";" + consensus + ";T6;Time to add and replicate a new block in blockchain;" + '{0:.12f}'.format((t3 - t1) * 1000))
        # logger.debug("|---------------------------------------------------------------------|")
        # print("block added")
        return encKey

    def runNoConsesusMulti(self):
        # print("Running without consensus")
        t1 = float(((time.time()) * 1000) * 1000)
        global peers
        global blockContext
        global logT5
        global blkCounter
        devPubKey = getBlockFromSyncList()
        #verififyKeyContext()
        #blockContext = "0001"
        #@TODO define somehow a device is in a context
        blockContext = gwContextConsensus[(blkCounter % len(gwContextConsensus))][0]
        blkCounter = blkCounter+1
        newBlock = ChainFunctionsMulti.createNewBlock(devPubKey, gwPvt, blockContext, consensus, deviceName)
        signature = verifyBlockCandidate(newBlock, gwPub, devPubKey, peers, True)
        if (signature == False):
            logger.info("Consesus was not achieved: block #" +
                        str(newBlock.index) + " will not be added")
            return False
        ChainFunctionsMulti.addBlockHeader(newBlock)
        sendBlockToPeersMulti(newBlock)
        t2 = float(((time.time()) * 1000) * 1000)
        logT5.append(
            "gateway;" + gatewayName + ";" + consensus + ";T5;Time to add a new block with no consensus;" + str(
                (t2 - t1) / 1000))
        # logT5.append("gateway;" + gatewayName + ";" + consensus + ";T5;Time to add a new block with none consensus algorithm;" + '{0:.12f}'.format((t2 - t1) * 1000))
        # print("Finish adding Block without consensus in: "+ '{0:.12f}'.format((t2 - t1) * 1000))
        return True

    def runPBFTMulti(self, lifecycleDeviceName):
        """ Run the PBFT consensus to add a new block on the chain """
        # print("I am in runPBFT")
        t1 = float(((time.time()) * 1000) * 1000)
        global gwPvt
        global blockContext
        global gwContextConsensus
        global blkCounter
        global logT5
        devPubKey = getBlockFromSyncList()
        #verififyKeyContext()
        #vblockContext = "0001"
        # set each block with a different context, e.g., based on the rest of division of bc size by number of contexts
        # @TODO define somehow a device is in a context
        # randomContext = random.randrange(0,len(gwContextConsensus))
        # if(len(gwContextConsensus==0)):
        #     logger.error("no contexts" + " My gw name is: " + gatewayName)
        #     blockContext = "9999"
        # else:
        blockContext = gwContextConsensus[(blkCounter % len(gwContextConsensus))][0]
        blkCounter = blkCounter+1
        # if(random.randrange(1,3) == 1):
        #     blockContext = "0001"
        # else:
        #     blockContext = "0002"
            # logger.error("******************Changed to 2****************")
        # blockContext = "0002"

        blk = ChainFunctionsMulti.createNewBlock(devPubKey, gwPvt, blockContext, consensus, lifecycleDeviceName)
        # logger.debug("Running PBFT function to block(" + str(blk.index) + ")")

        if ((PBFTConsensus(blk, gwPub, devPubKey, lifecycleDeviceName, True)) == False):
            logger.error("Consensus not finished")
            return False
        t2 = float(((time.time()) * 1000) * 1000)
        logT5.append("gateway;" + gatewayName + ";" + consensus + ";T5;Time to add a new block with pBFT consensus;" +  str((t2 - t1) / 1000))
        # logT5.append("gateway;" + gatewayName + ";" + consensus + ";T5;Time to add a new block with pBFT consensus;" + '{0:.12f}'.format((t2 - t1) * 1000))
        return True
        # print("Finish PBFT consensus in: "+ '{0:.12f}'.format((t2 - t1) * 1000))

    def updateBlockLedgerMulti(self, pubKey, transaction, index):
        # update local bockchain adding a new transaction
        """ Receive a new transaction and add it to the chain\n
            @param pubKey - Block public key\n
            @param transaction - Data to be insert on the block\n
            @param index - index of chain of transactions\n
            @return "done" - method done (the block are not necessarily inserted)
        """
        trans = pickle.loads(transaction)
        idx = pickle.loads(index)
        t1 = time.time()
        # logger.info("Received transaction #" + (str(trans.index)))
        blk = ChainFunctionsMulti.findBlock(pubKey)
        if blk != False:
            # logger.debug("Transaction size in the block = " +
            #              str(len(blk.transactions)))
            if not (ChainFunctionsMulti.blockContainsTransaction(blk, trans, idx)):
                if validatorClient:
                    isTransactionValid(trans, pubKey)
                ChainFunctionsMulti.addBlockTransaction(blk, trans, idx)
        t2 = time.time()
        logger.info("gateway;" + gatewayName + ";" + consensus + ";T2;Time to add a transaction in block ledger;" + '{0:.12f}'.format((t2 - t1) * 1000))
        return "done"

    def updateIOTBlockLedgerMulti(self, iotBlock, gwName):
        # update local bockchain adding a new block
        """ Receive a block and add it to the chain\n
            @param iotBlock - Block to be add\n
            @param gwName - sender peer's name
        """
        global logT3
        # print("Updating IoT Block Ledger, in Gw: "+str(gwName))
        # logger.debug("updateIoTBlockLedger Function")
        b = pickle.loads(iotBlock)
        # print("picked....")
        t1 = time.time()
        # logger.debug("Received block #" + (str(b.index)))
        # logger.info("Received block #" + str(b.index) +
        #             " from gateway " + str(gwName))
        if isBlockValidMulti(b):
            # print("updating is valid...")
            ChainFunctionsMulti.addBlockHeader(b)
        t2 = time.time()
        # print("updating was done")
        logT3.append(
            "gateway;" + gatewayName + ";" + consensus + ";T3;Time to add a new block in BL;" + '{0:.12f}'.format((t2 - t1) * 1000))
        # logger.info("gateway;" + gatewayName + ";" + consensus + ";T3;Time to add a new block in block ledger;" + '{0:.12f}'.format((t2 - t1) * 1000))

    def showIoTLedgerMulti(self):
        """ Log all chain \n
            @return "ok" - done
        """
        # logger.info("Showing Block Header data for peer: " + myURI)
        print("Showing Block Header data for peer: " + myURI)
        size = ChainFunctionsMulti.getBlockchainSize()
        # logger.info("IoT Ledger size: " + str(size))
        # logger.info("|-----------------------------------------|")
        print("IoT Ledger size: " + str(size))
        print("|-----------------------------------------|")
        theChain = ChainFunctionsMulti.getFullChain()
        for b in theChain:
        # logger.info(b.strBlock())
        # logger.info("|-----------------------------------------|")
            print(b.strBlock())
            print("|-----------------------------------------|")
        return "ok"
    
    def showBlockLedgerMulti(self, index):
        """ Log all transactions of a block\n
            @param index - index of the block\n
            @return "ok" - done
        """
        print("Showing Transactions data for peer: " + myURI)
        # logger.info("Showing Trasactions data for peer: " + myURI)
        blk = ChainFunctionsMulti.getBlockByIndex(index)
        print("Block for index"+str(index))
        if blk == False:
            return "Block does not exist"
        #print("Block for index: "+str(index))
        sizeChains = len(blk.transactions)
        # logger.info("Block Ledger size: " + str(size))
        # logger.info("-------")
        print("Transactions chains size: " + str(sizeChains))
        print("-------")
        i = 0
        for tranChain in blk.transactions:
            print("Transactions inside chain " + str(i) + ": " + str(len(tranChain)))
            for t in tranChain:
                print(t.strBlock())
                print("-------")
            i = i + 1
        return "ok"
    
    def showBlockWithId(self, deviceId):
        """ Log blocks with specific ID \n
            @param deviceId - Device ID to get blocks\n
            @return "ok" - done
        """
        # logger.info("Showing Block Header data for peer: " + myURI)
        print("Showing Block Headers with ID: " + deviceId)
        t1 = time.time()
        blocks = ChainFunctions.getBlocksById(deviceId)
        t2 = time.time()
        print("Time to get blocks: " + '{0:.12f}'.format((t2 - t1) * 1000))
        print("Device blocks count: " + str(len(blocks)))
        print("|-----------------------------------------|")
        for b in blocks:
            print(b.strBlock())
            print("|-----------------------------------------|")
        return "ok"
    
    def showBlockWithIdMulti(self, deviceId):
        """ Log blocks with multiple chains with specific ID \n
            @param deviceId - Device ID to get blocks\n
            @return "ok" - done
        """
        # logger.info("Showing Block Header data for peer: " + myURI)   
        print("")     
        print("Showing Block Headers with ID (for MULTI transactions): " + deviceId)
        t1 = time.time()
        blocks = ChainFunctionsMulti.getBlocksById(deviceId)
        t2 = time.time()
        print("Time to get blocks: " + '{0:.12f}'.format((t2 - t1) * 1000))
        print("Device blocks count: " + str(len(blocks)))
        print("|-----------------------------------------|")
        for b in blocks:
            print(b.strBlock())
            print("|-----------------------------------------|")
        return "ok"
        
    def showTransactionWithId(self, componentId, showTransactions):
        """ Log transactions with specific ID \n
            @param componentId - Component ID to get blocks\n
            @param showTransactions - Flag to show or not the transactions\n
            @return the time to get all transactions
        """
        # logger.info("Showing Block Header data for peer: " + myURI)
        print("Showing transactions Headers with ID: " + componentId)
        t1 = time.time()
        transactions = ChainFunctions.getTransactionsWithId(componentId)
        t2 = time.time()
        timeDiff = '{0:.12f}'.format((t2 - t1) * 1000)
        print("Time to get transactions: " + timeDiff)
        # logger.info("IoT Ledger size: " + str(size))
        # logger.info("|-----------------------------------------|")
        print("Components transactions count: " + str(len(transactions)))
        if showTransactions:
            print("|-----------------------------------------|")
            for t in transactions:
                print(t.strBlock())
                print("|-----------------------------------------|")
        
        return timeDiff, str(len(transactions))
    
    def showTransactionWithIdMulti(self, componentId, showTransactions):
        """ Log transactions for multi chains with specific ID \n
            @param componentId - Component ID to get blocks\n
            @param showTransactions - Flag to show or not the transactions\n
            @return the time to get all transactions
        """
        # logger.info("Showing Block Header data for peer: " + myURI)   
        print("")     
        print("Showing transactions Headers with ID (for MULTI transactions): " + componentId)
        t1 = time.time()
        transactions = ChainFunctionsMulti.getTransactionsWithId(componentId)
        t2 = time.time()
        timeDiff = '{0:.12f}'.format((t2 - t1) * 1000)
        print("Time to get transactions MULTI: " + timeDiff)
        # logger.info("IoT Ledger size: " + str(size))
        # logger.info("|-----------------------------------------|")
        print("Components transactions count: " + str(len(transactions)))
        if showTransactions:
            print("|-----------------------------------------|")
            for t in transactions:
                print(t.strBlock())
                print("|-----------------------------------------|")
        
        return timeDiff, str(len(transactions))
    
    def startTransactionsConsThreadsMulti(self):
        for x,y in gwContextConsensus:
            threading.Thread(target=self.threadTransactionConsensusMulti, args=(x,y)).start()
            # if (gwContextConsensus[0]) [("0001", "PoA"),("0002", "PBFT")]

    def threadTransactionConsensusMulti(self, context, consensus):
        # a sleep time to give time to all gateways connect and etc
        # time.sleep(5)
        # the other sleep times in this method is due to bad parallelism of Python... without any sleep, this thread can leave others in starvation
        if(consensus=="PBFT"):
            # while(True):
                for index in range(len(orchestratorContextObject)):
                    if (orchestratorContextObject[index][0] == context and orchestratorContextObject[index][1].exposedURI() == myURI):
                        self.performTransactionPoolPBFTConsensusMulti(context)
                        # time.sleep(0.02)
                    # else:
                # time.sleep(0.1)

    def performTransactionPoolPBFTConsensusMulti(self,context):
        global contextPeers
        global logT22
        global sizePool
        candidatePool =[]
        # sizePool = 30 # slice of transactions get from each pool
        minInterval = 10 # interval between consensus in ms
        minTransactions = 0 # minimum number of transactions to start consensus

        # for index in range(len(orchestratorContextObject)):
        #     # print("*** obj " + str(orchestratorContextObject[index][1]) + " my pyro " + str(Pyro4.Proxy(myURI)))
        #     # print("obj URI: " + str(orchestratorContextObject[index][1].exposedURI()) + "myURI " + str(myURI))
        #     # orchestratorContextObject[index][1].exposedURI()
        #     if (orchestratorContextObject[index][0] == context and orchestratorContextObject[index][1].exposedURI() == myURI):
        # print("******************I Am the PBFT Leader of context: "+context)
        while(len(candidatePool)==0):
            tcc1 = ((time.time()) * 1000) * 1000
            # just to not printing in every time that enters here, leave it only for interactive

            while(self.addContextinLockList(context)==False):
                # logger.error("I AM NOT WITH LOCK!!!!!")
                time.sleep(0.001)
            tempContextPeers = []
            for x in range(len(contextPeers)):
                # print(" ***VVVVV **** context? " +contextPeers[x][0])
                if (contextPeers[x][0] == context):
                    tempContextPeers = contextPeers[x][1]
            # use this if you want to get all elements from trpool
            # pickedCandidatePool = self.getLocalTransactionPool(context)
            # use this if you want to get first sizePool elements
            pickedCandidatePool = self.getNElementsLocalTransactionPool(context,sizePool)
            myPool = pickle.loads(pickedCandidatePool)
            if (myPool != False):
                candidatePool = myPool
                # print("I got my pool in PBFT")

            for p in tempContextPeers:
                peer = p.object
                while(peer.addContextinLockList(context)==False):
                    time.sleep(0.001)
                # pickedRemotePool = peer.getLocalTransactionPool(context)
                pickedRemotePool = peer.getNElementsLocalTransactionPool(context,sizePool)
                remoteCandidatePool = pickle.loads(pickedRemotePool)

                if(remoteCandidatePool!=False):
                    # .extend append each from another list
                    candidatePool.extend(remoteCandidatePool)
                    # while(len(remoteCandidatePool)>0):
                    #     # cant just append the remoteCandidatePool, should add each tuple
                    #     remoteTR = remoteCandidatePool.pop(0)
                    #     candidatePool.append((remoteTR[0],remoteTR[1]))

                    # candidatePool.append(remoteCandidatePool)
            candidatePoolSize = len(candidatePool)
            if (candidatePoolSize!=0):
                # logger.info("**************Inside PBFT Transaction ***************")
                self.prepareContextPBFTMulti(context,candidatePool,tempContextPeers)

                # if you want to set a min interval between consensus
                tcc2 = ((time.time()) * 1000) * 1000

                # te2 = ((time.time()) * 1000) * 1000
                # logger.error("ELECTION; " + str((te2-te1)/1000))
                self.removeLockfromContext(context)
                for p in tempContextPeers:
                    peer = p.object
                    peer.removeLockfromContext(context)

                # if ((tcc2 - tcc1) / 1000 < minInterval):
                #     time.sleep((minInterval - ((tcc2 - tcc1) / 1000)) / 1000)
                # election for new orchestrator
                self.electNewContextOrchestrator(context)
                # orchestratorContextObject.performTransactionPoolPBFTConsensusMulti(context)
                tcc2 = ((time.time()) * 1000) * 1000
                logT22.append("T22 CONTEXT; "+context+";PBFT CONSENSUS TIME; " + str((tcc2-tcc1)/1000) + "; SIZE; "+str(candidatePoolSize) + ";TPUT;" + str((candidatePoolSize)/(((tcc2-tcc1)/1000)/1000)))
                # call to execute the consensus for the new leader
                for index in range(len(orchestratorContextObject)):
                    if (orchestratorContextObject[index][0] == context):
                        threading.Thread(target=orchestratorContextObject[index][1].performTransactionPoolPBFTConsensusMulti, args=[context]).start()
                # logger.info("CONTEXT "+context+" PBFT CONSENSUS; " + str((tcc2-tcc1)/1000) + "; SIZE; "+str(candidatePoolSize))
                return

            else:
                self.removeLockfromContext(context)
                for p in tempContextPeers:
                    peer = p.object
                    peer.removeLockfromContext(context)
                tcc2 = ((time.time()) * 1000) * 1000
                if((tcc2 - tcc1) / 1000 < minInterval):
                    time.sleep((minInterval - ((tcc2 - tcc1) / 1000)) / 1000)
                    # print("****** sleeping " + str((minInterval - ((tcc2 - tcc1) / 1000)) / 1000) + "ms")

    def prepareContextPBFTMulti(self, context, candidatePool, alivePeers):
        """ Send a new candidatePool for all the available peers on the network\n
            @param newBlock - BlockHeader object\n
            @param generatorGwPub - Public key from the peer who want to generate the block\n
            @param generatorDevicePub - Public key from the device who want to generate the block\n
        """
        # logger.info("prepareContextPBFTMulti: inside prepare")
        candidateTransactionPool =[]
        votesPoolTotal = []
        validTransactionPool =[]

        while (len(candidatePool) > 0):
            # logger.info("prepareContextPBFTMulti: inside prepare--while")
            candidateTransaction = candidatePool.pop(0)
            if (candidateTransaction != False):
                # logger.info("prepareContextPBFTMulti: inside prepare--notfalse candidate")
                devPublicKey = candidateTransaction[0]
                lifecycleEvent = candidateTransaction[1]
                if(ChainFunctionsMulti.findBlock(devPublicKey)!=False):
                    blk = ChainFunctionsMulti.findBlock(devPublicKey)
                    lastBlk = (ChainFunctionsMulti.getLatestBlockTransaction(blk, lifecycleEvent.index))
                    nextInt = lastBlk.index + 1
                    signData = CryptoFunctions.signInfo(gwPvt, str(lifecycleEvent.data))
                    gwTime = "{:.0f}".format(((time.time() * 1000) * 1000))
                    # code responsible to create the hash between Info nodes.
                    prevInfoHash = (ChainFunctionsMulti.getLatestBlockTransaction(blk, lifecycleEvent.index)).hash
                    transaction = Transaction.Transaction(nextInt, prevInfoHash, gwTime, lifecycleEvent, signData, lifecycleEvent.index, lifecycleEvent.id)
                    
                    #verifyGwSign = CryptoFunctions.signVerify(str(candidateDevInfo), candidateTr.signature, receivedGwPub)
                    
                    candidateTransactionPool.append((devPublicKey, transaction))
                    # logger.info("-----------------------------inside prepare--transaction appended")
                    #trSign = CryptoFunctions.signInfo(gwPvt,str(transaction))
                    # votesPoolTotal.append([(devPublicKey, transaction), [trSign]])
                    votesPoolTotal.append([(devPublicKey, transaction), ["valid"]])
        if(len(candidateTransactionPool)==0):
            # logger.info("prepareContextPBFTMulti: All tr were invalid or no tr at all (Multi)")
            return

        dumpedPool = pickle.dumps(candidateTransactionPool)

        arrayPeersThreads = []
        # counter =0
        dumpedGwPub = pickle.dumps(gwPub)
        for p in alivePeers:
            # default type of thread that accepts return value in the join
            arrayPeersThreads.append(ThreadWithReturn(target=self.startRemoteVotingMulti, args=(context, dumpedPool, dumpedGwPub, p)))
            # arrayPeersThreads.append(threading.Thread(target=self.startRemoteVotingMulti, args=(context,dumpedPool,dumpedGwPub,p)))
            # start the last inserted thread in array
            arrayPeersThreads[-1].start()
            # counter = counter+1

        #logger.info("after start")
        for i in range(len(arrayPeersThreads)):

            # default class of thread used to have a return on join
            pickedVotes, pickedVotesSignature, remoteGwPk = arrayPeersThreads[i].join()
            # arrayPeersThreads[i].join()
            # logger.error("after join")

            # will get from a queue of returns (from votes)
            # pickedVotes, pickedVotesSignature, remoteGwPk = my_queue.get()

            # logger.error("got stuff")
            # pickedVotes, pickedVotesSignature, remoteGwPk = p.object.votePoolCandidate(context, dumpedPool, dumpedGwPub)
            votes = pickle.loads(pickedVotes)
            votesSignature = pickle.loads(pickedVotesSignature)
            # verify if list of votes are valid, i.e., peer signature in votes is correct
            if(CryptoFunctions.signVerify(str(votes),votesSignature, p.object.getGwPubkey())):
                # logger.info("prepareContextPBFTMulti: Votes Signature is valid")
                for index in range(len(votes)):
                    # if there is a vote
                    if(votes[index][1]=="valid"):
                        # append a new vote
                        votesPoolTotal[index][1].append(votes[index][1])
                        # verify if it get the minimun number of votes
                        if (len(votesPoolTotal[index][1]) > ((2 / 3) * len(alivePeers))):
                            # verify if it was not already inserted
                            if(not(votesPoolTotal[index][0] in validTransactionPool)):
                                # insert in validated pool
                                validTransactionPool.append(votesPoolTotal[index][0])
                                # logger.info("prepareContextPBFTMulti: Valid vote appended")
                if (len(validTransactionPool)==len(votesPoolTotal)):
                    # logger.error("YES... breaked... reduced the time ;)")
                    break
            # get every return from the method votePoolCandidate called by each thread and count votes after joins


        # for v in range(len(votesPoolTotal)):
        #     if (len(votesPoolTotal[v][1]) > ((2 / 3) * len(alivePeers))):
        #         # logger.error("APPENDED in final pool")
        #         validTransactionPool.append(votesPoolTotal[v][0])

        # commit

        # TODO define how to update peers: all peers or only participating in consensus?
        #
        if(self.commitContextPBFTMulti(validTransactionPool,alivePeers)):
        # if (self.commitContextPBFTMulti(validTransactionPool, peers)):
            return True

        return False

    def commitContextPBFTMulti(self, validTransactionPool, alivePeers):
        arrayPeersThreads = [] * len(alivePeers)

        if(len(validTransactionPool)>0):
            dumpedSetTrans = pickle.dumps(validTransactionPool)
            # addLocally
            # logger.info("commitContextPBFTMulti: Adding locally")
            self.updateBlockLedgerSetTransMulti(dumpedSetTrans,True)

            # add remote
            index = 0
            for p in alivePeers:

                obj=p.object
                # obj.updateBlockLedgerSetTransMulti(dumpedSetTrans,False)
                arrayPeersThreads.append(threading.Thread(target=obj.updateBlockLedgerSetTransMulti, args=(dumpedSetTrans,False)))
                arrayPeersThreads[index].start()
                index = index+1

            # this can be a problem for performance... trying
            # for i in range(len(arrayPeersThreads)):
            #     arrayPeersThreads[i].join()

            # logger.info("commitContextPBFTMulti: PASSED")
            return True
        logger.error("!!!! Failed to commit transactions !!!")
        return False

    def updateBlockLedgerSetTransMulti(self, candidatePool, isFirst):
        global logT20
        global logT21
        global logT26
        # update local bockchain adding a new transaction
        """ Receive a new transaction and add it to the chain\n
            @param pubKey - Block public key\n
            @param transaction - Data to be insert on the block\n
            @return "done" - method done (the block are not necessarily inserted)
        """
        setTrans = pickle.loads(candidatePool)
        t1 = time.time()
        # print("inside updateBlockLedgerSeTrans, setTrans: " + str(setTrans))
        # logger.info("updateBlockLedgerSetTransMulti: Received transaction #" + (str(setTrans.index)))
        originalLen = len(setTrans)
        while (len(setTrans)>0):
            candidateTransaction = setTrans.pop(0)
            # print("popped element from Pool")
            # print(candidateTransaction)
            # logger.info("updateBlockLedgerSetTransMulti: popped element from Pool")
            if (candidateTransaction != False):
                # print("AAAAAAAAAAAAAAAA passed the if")
                devPublicKey = candidateTransaction[0]
                deviceTrans = candidateTransaction[1]
                blk = ChainFunctionsMulti.findBlock(devPublicKey)
                # logger.info("updateBlockLedgerSetTransMulti: add transaction to chain")
                ChainFunctionsMulti.addBlockTransaction(blk, deviceTrans, deviceTrans.nonce)
                deviceTrans.__class__ = Transaction.Transaction
                candidateLifecycleEvent = deviceTrans.data
                candidateLifecycleEvent.__class__ = LifecycleEvent.LifecycleEvent
                candidateDevInfo = candidateLifecycleEvent.data
                candidateDevInfo.__class__ = DeviceInfo.DeviceInfo
                originalTimestamp = float (candidateDevInfo.timestamp)
                gwTimestamp = float(deviceTrans.timestamp)
                currentTimestamp = float (((time.time())*1000)*1000)
                logT20.append("gateway;" + gatewayName +";Context;" +blk.blockContext + ";T20;Transaction Latency;" + str((currentTimestamp - originalTimestamp)/1000))
                if(isFirst):
                    logT26.append("gateway;" + gatewayName + ";Context;" + blk.blockContext + ";T26;First Transaction Latency;" + str((currentTimestamp - originalTimestamp) / 1000))
                # logger.info("gateway;" + gatewayName + ";" + consensus + ";T20;Latency to generate and insert in my Gw is;" + str((currentTimestamp - originalTimestamp)/1000))
                # logger.info(
                #     "gateway;" + gatewayName + ";" + consensus + ";T21;Time to process Tr is;" + str(
                #         (currentTimestamp - gwTimestamp) / 1000))

        t2 = time.time()
        logT21.append("gateway;" + gatewayName + ";T21;Time to add a set of ;" + str(originalLen) + "; transactions in block ledger;" + '{0:.12f}'.format((t2 - t1) * 1000))
        logger.info("gateway;" + gatewayName + ";" + consensus + ";T2;Time to add a set of ;" + str(originalLen) + "; transactions in block ledger;" + '{0:.12f}'.format((t2 - t1) * 1000))

        return "done"

    def startRemoteVotingMulti(self, context, dumpedPool, dumpedGwPub, p):
        pickedVotes, pickedVotesSignature, remoteGwPk = p.object.votePoolCandidateMulti(context, dumpedPool, dumpedGwPub)
        return pickedVotes, pickedVotesSignature, remoteGwPk


    def votePoolCandidateMulti(self, context, candidatePool, pickedGwPub):
        """ Checks whether the new block has the following characteristics: \n
            * The hash of the previous block are correct in the new block data\n
            * The new block index is equals to the previous block index plus one\n
            * The generation time of the last block is smaller than the new one \n
            If the new block have it all, sign it with the peer private key\n
            @return False - The block does not have one or more of the previous characteristics\n
            @return votesPool, signature and GwPub - return a list of votes (valid), signature and gwpub
        """
        global logT23
        t1 = (time.time()*1000)
        validation = True
        votesPool =[]
        receivedPool = pickle.loads(candidatePool)
        receivedGwPub = pickle.loads(pickedGwPub)
        while(len(receivedPool) > 0):
            candidate = receivedPool.pop(0)
            receivedDevPub = candidate[0]
            candidateTr = candidate[1]
            candidateTr.__class__ = Transaction.Transaction
            candidateLifecycle = candidateTr.data
            candidateLifecycle.__class__ = LifecycleEvent.LifecycleEvent

            # verify if device is registered and if the index and timestamp are correct
            if (ChainFunctionsMulti.findBlock(receivedDevPub) != False):
                blk = ChainFunctionsMulti.findBlock(receivedDevPub)
                # print("passed the blk")
                lastBlk = (ChainFunctionsMulti.getLatestBlockTransaction(blk, candidateLifecycle.index))
                lastTrIndex = lastBlk.index
                lastTimestamp = lastBlk.timestamp
                if(lastTrIndex >= candidateTr.index or lastTimestamp >= candidateTr.timestamp ):
                    logger.error("***********************")
                    logger.error("***Invalid Tr time or index*")
                    logger.error("***********************")
                    validation = False

                # verify the gw of the device
                candidateDevInfo = candidateLifecycle.data
                candidateDevInfo.__class__ = DeviceInfo.DeviceInfo
                verifyGwSign = CryptoFunctions.signVerify(str(candidateDevInfo), candidateTr.signature, receivedGwPub)
                if (verifyGwSign != True):
                    logger.error("***********************")
                    logger.error("***Invalid Gw Signature*")
                    logger.error("***********************")
                    validation = False

                # verify the signature of the device
                d = " "+candidateDevInfo.timestamp+" "+candidateDevInfo.data

                isSigned = CryptoFunctions.signVerify(d, candidateDevInfo.deviceSignature, receivedDevPub)
                if (isSigned != True):
                    logger.error("***********************")
                    logger.error("***Invalid Device Signature*")
                    logger.error("***********************")
                    validation = False
                # after verifications...

                # first Tr is a dummy generated data
                if(len(blk.transactions[candidateLifecycle.index])-1 > 0):
                    lastTrLifecycle = lastBlk.data
                    lastTrLifecycle.__class__ = LifecycleEvent.LifecycleEvent
                    lastTrDevInfo = lastTrLifecycle.data
                    lastTrDevInfo.__class__ = DeviceInfo.DeviceInfo

                    if(lastTrDevInfo.timestamp >= candidateDevInfo.timestamp):
                        logger.error("***********************")
                        logger.error("***Invalid device info time*")
                        logger.error("***********************")
                        validation = False

            else:
                logger.error("***********************")
                logger.error("***Invalid PubKey -> it is not in BC*")
                logger.error("***********************")
                validation = False


            if(validation==True):
            #     # trSign = CryptoFunctions.signInfo(gwPvt, str(candidateTr))
            #     # votesPool.append([(receivedDevPub, candidateTr), trSign])
            #     # send only de candidate Tr signature
                votesPool.append([(candidateTr.signature), "valid"])
            # # if it is not valid, do not vote as valid
            else:
                votesPool.append([(candidateTr.signature), ""])
            validation = True
        votesSignature=CryptoFunctions.signInfo(gwPvt, str(votesPool))
        t2 = (time.time()*1000)
        logT23.append("T23 VOTING;CONTEXT "+context+";VOTING TIME; " + str(t2-t1))
        # logger.error("!!!!! My verification sign = " + str(CryptoFunctions.signVerify(str(votesPool),votesSignature,gwPub)))
        # logger.error("My signature is: " + votesSignature + "my votespool is: " + str(votesPool) + "my pub is" + gwPub)
        return pickle.dumps(votesPool), pickle.dumps(votesSignature), gwPub

    def isBlockInTheChainMulti(self, devPubKey):
        """ Verify if a block is on the chain\n
            @param devPubKey - block pub key\n
            @return boolean - True: block found, False: block not found
        """
        blk = ChainFunctionsMulti.findBlock(devPubKey)
        # print("Inside inBlockInTheChain, devPumyVoteForNewOrchestratorbKey= " + str(devPubKey))
        if(blk == False):
            # logger.debug("Block is false="+str(devPubKey))
            return False
        else:
            return True
        
    def addTransactionToPoolMulti(self, devPublicKey, encryptedObj, type, index):
        """ Receive a new transaction to be add to the chain, a
            send to the pool it to all peers\n
            @param devPublicKey - Public key from the sender device\n
            @param encryptedObj - Info of the transaction encrypted with AES 256\n
            @return "ok!" - all done\n
            @return "Invalid Signature" - an invalid key are found\n
            @return "Key not found" - the device's key are not found
        """
        # logger.debug("Transaction received")
        global gwPvt
        global gwPub
        global logT24
        global logT25
        t1 = time.time()

        # loading key and encryptedObj from from pickle serialization
        devPublicKey=pickle.loads(devPublicKey)
        # print("DevPubKey= " + str(devPublicKey))
        encryptedObj=pickle.loads(encryptedObj)
        type=pickle.loads(type)
        index=pickle.loads(index)
        blk = ChainFunctionsMulti.findBlock(devPublicKey)
        # self.addContextinLockList(devPublicKey)
        if (blk != False and blk.index > 0):
            devAESKey = findAESKey(devPublicKey)
            if (devAESKey != False):
                # plainObject contains [Signature + Time + Data]

                plainObject = CryptoFunctions.decryptAES(
                    encryptedObj, devAESKey)

                #print("plainObject = " + str(plainObject))
                split = plainObject.split()
                signature = split[0]  #plainObject[:88] # get first 88 chars
                #print("signature = " + str(signature))
                # remove the 16 char of timestamp
                devTime = split[1]  # plainObject[88:104]
                #print("devTime = " + str(devTime))
                # retrieve the last chars which are the data
                deviceData = split[2]  # plainObject[104:]
                #print("deviceData = " + str(deviceData))
                t2 = time.time()
                #logger.info("gateway;" + gatewayName + ";" + consensus + ";T1;Time to add a new transaction in a block;" + '{0:.12f}'.format((t2 - t1) * 1000))
                # logger.info("gateway;" + gatewayName + ";" + consensus + ";T1;Transaction data received")

                d = " "+devTime+" "+deviceData
                isSigned = CryptoFunctions.signVerify(
                    d, signature, devPublicKey)

                if isSigned:
                    deviceInfo = DeviceInfo.DeviceInfo(
                        signature, devTime, deviceData)
                    matching = [s for s in componentsId if type in s]   
                    lifecycleEvent = LifecycleEvent.LifecycleEvent(type, matching[0], deviceInfo, index)
                    # send to consensus here
                    devContext = blk.blockContext
                    t2=time.time()
                    logT24.append("T24 VERIFICATION TIME; " + str((t2-t1)*1000))
                    nextInt = (ChainFunctionsMulti.getLatestBlockTransaction(blk, index)).index + 1
                    signData = CryptoFunctions.signInfo(gwPvt, str(deviceInfo))
                    gwTime = "{:.0f}".format(((time.time() * 1000) * 1000))
                    prevInfoHash = (ChainFunctionsMulti.getLatestBlockTransaction(blk, index)).hash
                    transaction = Transaction.Transaction(
                        nextInt, prevInfoHash, gwTime, lifecycleEvent, signData, index, matching[0])
                    #ChainFunctionsMulti.addBlockTransaction(blk, transaction, index)
                    t3=time.time()
                    # logger.info("gateway;" + gatewayName + ";" + consensus + ";T1;Transaction created")
                    while ( self.addNewTransactionToSyncList(devPublicKey, lifecycleEvent, devContext) == False):
                        logger.error("tried to insert and it was not possible, trying again")
                        time.sleep(0.001)
                    t4=time.time()
                    logT25.append("T25 Appending TX IN POOL TIME; " + str((t4-t3)*1000))
                    # after context

                    # print("all done")
                    # self.removeLockfromContext(devPublicKey)
                    return "ok!"
                else:
                    # logger.debug("--Transaction not appended--Transaction Invalid Signature")
                    # self.removeLockfromContext(devPublicKey)
                    return "Invalid Signature"
            # logger.debug("--Transaction not appended--Key not found")
            # self.removeLockfromContext(devPublicKey)
            return "key not found"
        logger.error("key not found when adding transaction")
        # self.removeLockfromContext(devPublicKey)
        return "block false"

def sendTransactionToPeersMulti(devPublicKey, transaction, index):
    """ Send a transaction received to all peers connected.\n
        @param devPublickey - public key from the sending device\n
        @param transaction - info to be add to a block
    """
    global peers
    for peer in peers:
        obj = peer.object
        # logger.debug("Sending transaction to peer " + peer.peerURI)
        trans = pickle.dumps(transaction)
        idx = pickle.dumps(index)
        obj.updateBlockLedgerMulti(devPublicKey, trans, idx)
        # trans.__class__ = Transaction.Transaction
        # candidateDevInfo = trans.data
        # candidateDevInfo.__class__ = DeviceInfo.DeviceInfo
        # originalTimestamp = float(candidateDevInfo.timestamp)

        # currentTimestamp = float(((time.time()) * 1000) * 1000)
        # logT20.append("gateway;" + gatewayName + ";T20;Transaction Latency;" + str(
        #     (currentTimestamp - originalTimestamp) / 1000))

def sendBlockToPeersMulti(IoTBlock):
    """
    Receive a block and send it to all peers connected.\n
    @param IoTBlock - BlockHeader object
    """
    global peers
    # print("sending block to peers")
    # logger.debug("Running through peers")
    for peer in peers:
        # print ("Inside for in peers")
        obj = peer.object
        # print("sending IoT Block to: " + str(peer.peerURI))
        # logger.debug("Sending block to peer " + str(peer.peerURI))
        dat = pickle.dumps(IoTBlock)
        obj.updateIOTBlockLedgerMulti(dat, myName)
    # print("block sent to all peers")

def restartChains(keys):
    """ Store the gateway keys to the text file\n
        @param keys - all the gateways keys read from file to start the chain\n
    """
    global peers
    global gwPub
    global gwPvt

    # Update the local keys
    key = keys[0]
    gwPub = key[0]
    gwPvt = key[1]
    #print ("public = " + str(gwPub) + ", private = " + str(gwPvt))

    ChainFunctions.restartChain()
    ChainFunctionsMulti.restartChain()
    #blk = ChainFunctionsMulti.getLatestBlock()
    #print("BlockGenesis = "+ str(blk.strBlock()))
    # print("sending block to peers")
    # logger.debug("Running through peers")
    i = 1
    for peer in peers:
        # Send each key pair to each peer
        key = keys[i]
        #print ("public = " + str(key[0]) + ", private = " + str(key[1]))
        obj = peer.object
        #print("sending KEY to: " + str(peer.peerURI))
        # logger.debug("Sending block to peer " + str(peer.peerURI))
        pubKey = pickle.dumps(key[0])
        privKey = pickle.dumps(key[1])
        obj.updateGatewayKeys(pubKey, privKey, myName)
        i = i + 1

def storeKeysFromPeers(f):
    """ Store the gateway keys to the text file\n
        @param f - the file to store the local keys\n
    """

    #print("gwPub = "+ str(gwPub))
    #print("gwPvt = "+ str(gwPvt))

    pub = gwPub.replace('\n', '\\n')
    pvt = gwPvt.replace('\n', '\\n')

    f.write(pub + "  " + pvt + "\n")

    for peer in peers:
        obj = peer.object
        #print("sending request to: " + str(peer.peerURI))
        obj.storeGatewayKeys(myName)

def isBlockValidMulti(block):
    # Todo Fix the comparison between the hashes... for now is just a mater to simulate the time spend calculating the hashes...
    # global BlockHeaderChain
    # print(str(len(BlockHeaderChain)))
    lastBlk = ChainFunctionsMulti.getLatestBlock()
    # print("Index:"+str(lastBlk.index)+" prevHash:"+str(lastBlk.previousHash)+ " time:"+str(lastBlk.timestamp)+ " pubKey:")
    # lastBlkHash = CryptoFunctions.calculateHash(lastBlk)

    lastBlkHash = CryptoFunctions.calculateHash(lastBlk.index, lastBlk.previousHash, lastBlk.timestamp, 
                        lastBlk.nonce, lastBlk.publicKey, lastBlk.blockContext, lastBlk.device)

    # print ("This Hash:"+str(lastBlkHash))
    # print ("Last Hash:"+str(block.previousHash))
    if(lastBlkHash == block.previousHash):
        # logger.info("isBlockValid == true")
        return True
    else:
        logger.error("isBlockValid == false")
        logger.error("lastBlkHash = " + str(lastBlkHash))
        logger.error("block.previous = " + str(block.previousHash))
        logger.error("lastBlk Index = " + str(lastBlk.index))
        logger.error("block.index = " + str(block.index))
        # return False
        return True

#############################################################################
#############################################################################
##############          END Lifecycle Events (Rodrigo)         ##############
#############################################################################
#############################################################################

def addNewBlockToSyncList(devPubKey):
    """ Add a new block to a syncronized list through the peers\n
        @param devPubKey - Public key of the block
    """
    # logger.debug("running critical stuffff......")
    # print("Inside addNewBlockToSyncLIst")
    global lock
    global blockConsensusCandidateList
    i=0
    while(not(lock.acquire(False)) and i<30):
        i=i+1
        # logger.info("$$$$$$$$$ not possible to acquire a lock in addNewblocktosynclist")
        time.sleep(0.01)
    if (i==30):
        return False
    # logger.debug("running critical was acquire")

    # logger.debug("Appending block to list :")#+srt(len(blockConsensusCandidateList)))
    # print("Inside Lock")
    blockConsensusCandidateList.append(devPubKey)
    lock.release()
    # print("Unlocked")

def getBlockFromSyncList():
    """ Get the first block at a syncronized list through the peers\n
        @return devPubKey - Public key from the block
    """
    # logger.debug("running critical stuffff to get sync list......")
    global lock
    # lock.acquire(1)
    i=0
    while (not(lock.acquire(False)) and i < 30):
        i = i + 1
        # logger.info("$$$$$$$$$ not possible to acquire a lock in getblockfromsynclist")
        time.sleep(0.01)
    if (i == 30):
        return False
    # logger.debug("lock aquired by get method......")
    global blockConsensusCandidateList
    if(len(blockConsensusCandidateList) > 0):
        # logger.debug("there is a candidade, pop it!!!")
        devPubKey = blockConsensusCandidateList.pop(0)
    lock.release()
    # logger.debug("Removing block from list :")#+srt(len(blockConsensusCandidateList)))
    return devPubKey

# @Roben returning the peer that has a specified PK

def getPeerbyPK(gwPubKey):
    """ Receive the peer URI generated automatically by pyro4 and return the peer object\n
        @param publicKey publicKey from the peer wanted\n
        @return p - peer object \n
        @return False - peer not found
    """
    global peers
    for p in peers:
        obj = p.object
        # print("Object GW PUB KEY: " + obj.getGwPubkey())
        if obj.getGwPubkey() == gwPubKey:
            return p.peerURI
    return False

###########
# Consensus PBFT @Roben
###########
# the idea newBlockCandidate[newBlockHash][gwPubKey] = signature, if the gateway put its signature, it is voting for YES
newBlockCandidate = {}
newTransactionCandidate = {}  # same as block, for transaction

# def runPBFT():
#     """ Run the PBFT consensus to add a new block on the chain """
#     # print("I am in runPBFT")
#     t1 = time.time()
#     global gwPvt
#     devPubKey = getBlockFromSyncList()
#
#     blk = ChainFunctions.createNewBlock(devPubKey, gwPvt,consensus)
#     # logger.debug("Running PBFT function to block("+str(blk.index)+")")
#
#     PBFTConsensus(blk, gwPub, devPubKey)
#     t2 = time.time()
#     logger.info("=====6=====>time to execute block consensus: " + '{0:.12f}'.format((t2 - t1) * 1000))
#     print("I finished runPBFT")

# def rundBFT():
#     """ Run the PBFT consensus to add a new block on the chain """
#     # print("I am in rundBFT")
#     t1 = time.time()
#     global gwPvt
#     devPubKey = getBlockFromSyncList()
#
#     blk = ChainFunctions.createNewBlock(devPubKey, gwPvt,consensus)
#     # logger.debug("Running PBFT function to block("+str(blk.index)+")")
#     PBFTConsensus(blk, gwPub, devPubKey)
#     t2 = time.time()
#     logger.info("=====6=====>time to execute block consensus: " + '{0:.12f}'.format((t2 - t1) * 1000))
#     print("I finished rundBFT")

# improve threads to return value when joins

def preparePBFTConsensus():
    """ verify all alive peers that will particpate in consensus\n
        @return list of available peers
    """
    alivePeers = []
    global peers
    for p in peers:
        # if p.peerURI._pyroBind(): #verify if peer is alive
        alivePeers.append(p.peerURI)
    # return alivePeers
    return peers

######PBFT Consensus for blocks########

def PBFTConsensus(newBlock, generatorGwPub, generatorDevicePub, lifecycleDeviceName, isMulti = False):
    """ Make the configurations needed to run consensus and call the method runPBFT()\n
        @param newBlock - BlockHeader object\n
        @param generatorGwPub - Public key from the peer who want to generate the block\n
        @param generatorDevicePub - Public key from the device who want to generate the block\n
    """
    global peers
    threads = []
    # logger.debug("newBlock received for PBFT Consensus")
    # connectedPeers = preparePBFTConsensus() #verify who will participate in consensus
    connectedPeers = peers
    # send the new block to the peers in order to get theirs vote.
    # commitBlockPBFT(newBlock, generatorGwPub,generatorDevicePub,connectedPeers) #send to all peers and for it self the result of validation

    # t = threading.Thread(target=commitBlockPBFT, args=(newBlock,generatorGwPub,generatorDevicePub,connectedPeers))
    # t.start()
    # print("inside PBFTConsensus, before commitblockpbft")
    if(commitBlockPBFT(newBlock, generatorGwPub,
                    generatorDevicePub, connectedPeers, lifecycleDeviceName, isMulti)):
        return True

    return False
    # print("inside PBFTConsensus, after commitblockpbft")
    # threads.append(t)
    # for t in threads:
    #     t.join()

    # if calcBlockPBFT(newBlock,connectedPeers):  # calculate, and if it is good, insert new block and call other peers to do the same
    #     for p in connectedPeers:
    #         # logger.debug("calling to:"+str(p.peerURI))
    #         x = p.object.calcBlockPBFTRemote(newBlock)
    #         # logger.debug("return from peer:"+str(x))
    #     #     t = threading.Thread(target=p.object.calcBlockPBFTRemote, args=(newBlock, connectedPeers))
    #     #     t.start()
    #     #     threads.append(t)
    #     # for t in threads:
    #     #     t.join()
    #     blkHash = CryptoFunctions.calculateHashForBlock(newBlock)
    #     if(blkHash in newBlockCandidate):
    #         del newBlockCandidate[blkHash]
    #     #del newBlockCandidate[CryptoFunctions.calculateHashForBlock(newBlock)]
    #         return True
    # return False

def commitBlockPBFT(newBlock, generatorGwPub, generatorDevicePub, alivePeers, lifecycleDeviceName, isMulti):
    """ Send a new block for all the available peers on the network\n
        @param newBlock - BlockHeader object\n
        @param generatorGwPub - Public key from the peer who want to generate the block\n
        @param generatorDevicePub - Public key from the device who want to generate the block\n
    """
    global blockContext
    threads = []
    nbc = ""
    pbftFinished = True
    i = 0
    # print("inside commitblockpbft")
    while (pbftFinished and i < 30):
        # print("inside commitblockpbft, inside while")
        pbftAchieved = handlePBFT(newBlock, generatorGwPub, generatorGwPub, alivePeers, isMulti)
        if(not pbftAchieved):
            oldId = newBlock.index
            # logger.info("PBFT not achieve, Recreating block="+ str(ChainFunctions.getBlockchainSize()))
            if isMulti:
                newBlock = ChainFunctionsMulti.createNewBlock(generatorDevicePub, gwPvt, 
                                                              blockContext, consensus, lifecycleDeviceName)
            else:
                newBlock = ChainFunctions.createNewBlock(generatorDevicePub, gwPvt, 
                                                         blockContext, consensus, lifecycleDeviceName)
            # logger.info("Block Recriated ID was:("+str(oldId)+") new:("+str(newBlock.index)+")")
            i = i + 1
            time.sleep(0.01)
            # print("####not pbftAchieved")
        else:
            pbftFinished = False
            # print("####pbftFinished")
    if i == 30:
        return False
    else:
        return True
    # if (hashblk in newBlockCandidate) and (newBlockCandidate[hashblk] == CryptoFunctions.signInfo(gwPvt, newBlock)):
        # if newBlockCandidate[CryptoFunctions.calculateHashForBlock(newBlock)][gwPub] == CryptoFunctions.signInfo(gwPvt, newBlock):#if it was already inserted a validation for the candidade block, abort
    #    print ("block already in consensus")
    #    return
        # newBlock,generatorGwPub,generatorDevicePub,alivePeers
    # if verifyBlockCandidate(newBlock, generatorGwPub, generatorDevicePub, alivePeers):#verify if the block is valid
    #     for p in alivePeers: #call all peers to verify if block is valid
    #         t = threading.Thread(target=p.object.verifyBlockCandidateRemote, args=(pickle.dumps(newBlock),generatorGwPub,generatorDevicePub))
    #         #### @Regio -> would it be better to use "pickle.dumps(newBlock)"  instead of newBlock?
    #         threads.append(t)
    #     #  join threads
    #     for t in threads:
    #         t.join()

def handlePBFT(newBlock, generatorGwPub, generatorDevicePub, alivePeers, isMulti):
    """ Send the new block to all the peers available to be verified\n
        @param newBlock - BlockHeader object\n
        @param generatorGwPub - Public key from the peer who want to generate the block\n
        @param generatorDevicePub - Public key from the device who want to generate the block\n
        @param alivePeers - list of available peers\n
        @return boolean - True: block sended to all peers, False: fail to send the block
    """
    hashblk = CryptoFunctions.calculateHashForBlock(newBlock)
    # print("inside handlepbft")
    # logger.debug("Running commit function to block: "+str(hashblk))
    # print("######before handlePBFT first for")
    picked = pickle.dumps(newBlock)
    picked2 = pickle.dumps(isMulti)
    for p in alivePeers:
        # logger.debug("Asking for block verification from: "+str(p.peerURI))
        # verifyRet = p.object.verifyBlockCandidateRemote(pickle.dumps(newBlock), generatorGwPub, generatorDevicePub)

        verifyRet = p.object.verifyBlockCandidateRemote(picked, generatorGwPub, picked2)
        # logger.debug("Answer received: "+str(verifyRet))
        # print("######inside handlePBFT first for")
        if(verifyRet):
            peerPubKey = p.object.getGwPubkey()
            # logger.info("Pub Key from gateway that voted: "+str(peerPubKey))
            # logger.info("Running the add vote to block")
            addVoteBlockPBFT(newBlock, peerPubKey, verifyRet)
            calcRet = calcBlockPBFT(newBlock, alivePeers, isMulti)
            # logger.info("Result from calcBlockPBFT:"+str(calcRet))
            if(calcRet):
                # logger.info("Consensus was achieve, updating peers and finishing operation")
                if isMulti:
                    sendBlockToPeersMulti(newBlock)
                else:
                    sendBlockToPeers(newBlock)
                # print("handlePBFT = true")
                return True
    # logger.info("Consesus was not Achieved!!! Block(" +
    #             str(newBlock.index)+") will not added")
    # print("handlePBFT = false")
    return False

# @Roben dbft
# def handledBFT(newBlock,generatorGwPub,generatorDevicePub,alivePeers):
#     """ Send the new block to all the peers available to be verified\n
#         @param newBlock - BlockHeader object\n
#         @param generatorGwPub - Public key from the peer who want to generate the block\n
#         @param generatorDevicePub - Public key from the device who want to generate the block\n
#         @param alivePeers - list of available peers\n
#         @return boolean - True: block sended to all peers, False: fail to send the block
#     """
#     hashblk = CryptoFunctions.calculateHashForBlock(newBlock)
#     # logger.debug("Running commit function to block: "+str(hashblk))
#     #@Roben for p in aliverPeers and p is a delegate
#     for p in alivePeers:
#         # logger.debug("Asking for block verification from: "+str(p.peerURI))
#         #verifyRet = p.object.verifyBlockCandidateRemote(pickle.dumps(newBlock), generatorGwPub, generatorDevicePub)
#         picked = pickle.dumps(newBlock)
#         verifyRet = p.object.verifyBlockCandidateRemote(picked, generatorGwPub)
#         # logger.debug("Answer received: "+str(verifyRet))
#         if(verifyRet):
#             peerPubKey = p.object.getGwPubkey()
#             # logger.debug("Pub Key from gateway that voted: "+str(peerPubKey))
#             # logger.debug("Running the add vote to block")
#             addVoteBlockPBFT(newBlock, peerPubKey, verifyRet)
#             calcRet = calcBlockPBFT(newBlock, alivePeers)
#             # logger.debug("Result from calcBlockPBFT:"+str(calcRet))
#             if(calcRet):
#                 logger.info("Consensus was achieve, updating peers and finishing operation")
#                 sendBlockToPeers(newBlock)
#                 return True
#     logger.info("Consesus was not Achieved!!! Block("+str(newBlock.index)+") will not added")
#     return False

def verifyBlockCandidate(newBlock, generatorGwPub, generatorDevicePub, alivePeers, isMulti = False):
    """ Checks whether the new block has the following characteristics: \n
        * The hash of the previous block are correct in the new block data\n
        * The new block index is equals to the previous block index plus one\n
        * The generation time of the last block is smaller than the new one \n
        If the new block have it all, sign it with the peer private key\n
        @return False - The block does not have one or more of the previous characteristics\n
        @return voteSignature - The block has been verified and approved
    """
    blockValidation = True
    if isMulti:
        #print("Inside verifyBlockCandidate, with MULTI")
        lastBlk = ChainFunctionsMulti.getLatestBlock()
    else:
        #print("Inside verifyBlockCandidate, with NORMAL")
        lastBlk = ChainFunctions.getLatestBlock()
    # logger.debug("last block:"+str(lastBlk.strBlock()))
    lastBlkHash = CryptoFunctions.calculateHashForBlock(lastBlk)
    # print("Index:"+str(lastBlk.index)+" prevHash:"+str(lastBlk.previousHash)+ " time:"+str(lastBlk.timestamp)+ " pubKey:")
    # lastBlkHash = CryptoFunctions.calculateHash(lastBlk.index, lastBlk.previousHash, lastBlk.timestamp,
    #                                             lastBlk.publicKey)
    # print ("Last Hash:"+str(lastBlkHash))
    # print ("Prev Hash:"+str(newBlock.previousHash))

    if (lastBlkHash != newBlock.previousHash):
        # print("validation lastblkhash")
        logger.error("Failed to validate new block(" +
                        str(newBlock.index)+") HASH value")
        # logger.debug("lastBlkHash="+str(lastBlkHash))
        # logger.debug("newBlock-previousHash="+str(newBlock.previousHash))
        blockValidation = False
        return blockValidation
    if (int(lastBlk.index+1) != int(newBlock.index)):
        # print("validation lastblkindex")
        logger.error("Failed to validate new block(" +
                        str(newBlock.index)+") INDEX value")
        # logger.debug("lastBlk Index="+str(lastBlk.index))
        # logger.debug("newBlock Index="+str(newBlock.index))
        blockValidation = False
        return blockValidation
    if (lastBlk.timestamp > newBlock.timestamp): # @TODO this timestamp contraint can be hard -> global time
        # print("validation lastblktime")
        logger.error("Failed to validate new block(" +
                        str(newBlock.index)+") TIME value")
        # logger.debug("lastBlk time:"+str(lastBlk.timestamp))
        # logger.debug("lastBlk time:"+str(newBlock.timestamp))
        blockValidation = False
        return blockValidation
    if blockValidation:
        logger.info("block successfully validated")
        voteSignature = CryptoFunctions.signInfo(
            gwPvt, newBlock.__str__())  # identify the problem in this line!!
        # logger.debug("block successfully signed")
        # addVoteBlockPBFT(newBlock, gwPub, voteSignature)
        # logger.debug("block successfully added locally")
        # print("finish verifyBlockCandidate")
        return voteSignature
        # addVoteBlockPBFT(newBlock, gwPub, voteSignature) #vote positively, signing the candidate block
        # for p in alivePeers:
        #     p.object.addVoteBlockPBFTRemote(newBlock, gwPub, voteSignature) #put its vote in the list of each peer
        # return True
    else:
        # print("Failed to validate new block")
        logger.error("Failed to validate new block")
        return False

def addVoteBlockPBFT(newBlock, voterPub, voterSign):
    """ add the signature of a peer into the newBlockCandidate,
        using a list to all gw for a single hash, if the block is valid put the signature \n
        @return True -  why not ? :P   ... TODO why return
    """
    global newBlockCandidate
    blkHash = CryptoFunctions.calculateHashForBlock(newBlock)
    # logger.debug("Adding the block to my local dictionary")
    if(blkHash not in newBlockCandidate):
        # logger.debug("Block is not in the dictionary... creating a new entry for it")
        newBlockCandidate[blkHash] = {}
    newBlockCandidate[blkHash][voterPub] = voterSign
    # print("vote added")
    # newBlockCandidate[CryptoFunctions.calculateHashForBlock(newBlock)][voterPub] = voterSign
    return True

def calcBlockPBFT(newBlock, alivePeers, isMulti):
    """ Verify if the new block achieved the consensus\n
        @param newBlock - BlockHeader object\n
        @param alivePeers - list of available peers\n
        @return boolean - True: consensus achived, False: consensus Not achieved yet
    """
    # print("Inside CalcBlockPBFT")
    # print("Consensus:   "+ consensus)
    # if (consensus=="PoW"):
    #     return True
    # logger.debug("Running the calc blockc pbft operation")
    blHash = CryptoFunctions.calculateHashForBlock(newBlock)
    locDicCount = int(len(newBlockCandidate[blHash]))
    peerCount = int(len(alivePeers))
    # logger.debug("local dictionary value:"+str(locDicCount))
    # logger.debug("alivePeers: "+str(peerCount))
    # cont=0
    if(consensus == "PBFT" or consensus == "dBFT"):
        cont = int(float(0.667)*float(peerCount))
    if(consensus == "Witness3"):
        cont = 2
    # print("##Value of cont:   "+str(cont))
    # if len(newBlockCandidate[CryptoFunctions.calculateHashForBlock(newBlock)]) > ((2/3)*len(alivePeers)):
    if (blHash in newBlockCandidate) and (locDicCount >= cont):
        # logger.debug("Consensus achieved!")
        if isMulti:
            ChainFunctionsMulti.addBlockHeader(newBlock)
        else:
            ChainFunctions.addBlockHeader(newBlock)
        # for p in alivePeers:
        #     p.object.insertBlock(blkHash)
        # print("calcBLockPBFT = True")
        return True
    else:
        # logger.debug("Consensus Not achieved yet!")
        # print("calcBLockPBFT = false")
        return False

######
# Transaction PBFT
######

# # Consensus for transactions
# def PBFTConsensusTransaction(block, newTransaction, generatorGwPub, generatorDevicePub):
#     """ Run the PBFT consensus to add a new transaction to a block\n
#         @param block - BlockHeader object where the transaction will be add\n
#         @param newTransaction - the transaction who will be add\n
#         @param generatorGwPub - Sender peer public key\n
#         @generatorDevicePub - Device how create the transaction and wants to add it to a block\n
#         @return boolean - True: Transaction approved to consensus, False: transaction not approved
#     """
#     threads = []
#     connectedPeers = preparePBFTConsensus()
#     commitTransactionPBFT(block, newTransaction,
#                             generatorGwPub, generatorDevicePub, connectedPeers)
#     # calculate, and if it is good, insert new block and call other peers to do the same
#     if calcTransactionPBFT(newTransaction, connectedPeers):
#         for p in connectedPeers:
#             t = threading.Thread(target=p.object.calcBlockPBFT, args=(
#                 block, newTransaction, connectedPeers))
#             threads.append(t)
#         for t in threads:
#             t.join()
#         del newBlockCandidate[CryptoFunctions.calculateHashForBlock(
#             newTransaction)]
#         return True
#     return False

# def commitTransactionPBFT(block, newTransaction, generatorGwPub, generatorDevicePub, alivePeers):
#     """ Send a transaction to be validated by all peers\n
#         @param block - BlockHeader object where the transaction will be add\n
#         @param newTransaction - the transaction who will be add\n
#         @param generatorGwPub - Sender peer public key\n
#         @generatorDevicePub - Device how create the transaction and wants to add it to a block\n
#         @param alivePeers - list of available peerszn\n
#         @return boolean - True: sended to validation, False: transaction are not valid or already in consensus
#     """
#     # TODO similar to what was done with block, just different verifications
#     threads = []
#     # if it was already inserted a validation for the candidade block, abort
#     if newTransactionCandidate[CryptoFunctions.calculateHash(newTransaction)][gwPub] == CryptoFunctions.signInfo(gwPvt, newTransaction):
#         # print ("transaction already in consensus")
#         return False
#     if verifyTransactionCandidate():  # verify if the transaction is valid
#         for p in alivePeers:  # call all peers to verify if block is valid
#             t = threading.Thread(target=p.object.verifyTransactionCandidate, args=(
#                 block, newTransaction, generatorGwPub, generatorDevicePub, alivePeers))
#             # @Regio -> would it be better to use "pickle.dumps(newBlock)"  instead of newBlock?
#             threads.append(t)
#         #  join threads
#         for t in threads:
#             t.join()
#         return True
#     return False

def verifyTransactionCandidate(block, newTransaction, generatorGwPub, generatorDevicePub, alivePeers):
    """ Checks whether the new transaction has the following characteristics:\n
        * The block is on the chain\n
        * The last transaction hash on the chain and the new transaction are the same\n
        * The index of the new transaction are the index of the last transaction plus one\n
        * The generation time of the last transaction is smaller than the new one \n
        * The data is sign by the TODO (generator device or gateway)
        @param block - BlockHeader object where the transaction will be add\n
        @param newTransaction - the transaction who will be add\n
        @param generatorGwPub - Sender peer public key\n
        @generatorDevicePub - Device how create the transaction and wants to add it to a block\n
        @param alivePeers - list of available peers\n
        @return boolean - True: approved, False: not approved
    """
    transactionValidation = True
    if (ChainFunctions.getBlockByIndex(block.index)) != block:
        transactionValidation = False
        return transactionValidation

    lastTransaction = ChainFunctions.getLatestBlockTransaction(block)
    # print("Index:"+str(lastBlk.index)+" prevHash:"+str(lastBlk.previousHash)+ " time:"+str(lastBlk.timestamp)+ " pubKey:")
    #lastTransactionHash = CryptoFunctions.calculateHash(lastTransaction.index, lastTransaction.previousHash, lastTransaction.timestamp, lastTransaction.data, lastTransaction.signature, lastTransaction.signature)
    lastTransactionHash = CryptoFunctions.calculateTransactionHash(ChainFunctions.getLatestBlockTransaction(block))

    # print ("This Hash:"+str(lastBlkHash))
    # print ("Last Hash:"+str(block.previousHash))
    if (lastTransactionHash != newTransaction.previousHash):
        transactionValidation = False
        return transactionValidation
    if (newTransaction.index != (lastTransactionHash.index+1)):
        transactionValidation = False
        return transactionValidation
    if (lastTransaction.timestamp <= newTransaction.timestamp):
        transactionValidation = False
        return transactionValidation
    # @Regio the publick key used below should be from device or from GW?
    if not (CryptoFunctions.signVerify(newTransaction.data, newTransaction.signature, generatorDevicePub)):
        transactionValidation = False
        return transactionValidation
    if transactionValidation:
        voteSignature = CryptoFunctions.signInfo(gwPvt, newTransaction)
        # vote positively, signing the candidate transaction
        addVoteTransactionPBFT(newTransaction, gwPub, voteSignature)
        for p in alivePeers:
            # put its vote in the list of each peer
            p.object.addVoteBlockPBFT(newTransaction, gwPub, voteSignature)
        return True
    else:
        return False

def addVoteTransactionPBFT(newTransaction, voterPub, voterSign):
    """ Add the vote of the peer to the transaction\n
        @param newTransaction - Transaction object\n
        @param voterPub - vote of the peer\n
        @param voterSing - sing of the peer\n
        @return True TODO needed?
    """
    global newTransactionCandidate
    newTransactionCandidate[CryptoFunctions.calculateHashForBlock(
        newTransaction)][voterPub] = voterSign
    return True

def calcTransactionPBFT(block, newTransaction, alivePeers):
    """ If consensus are achivied, add the transaction to the block\n
        @param block - BlockHeader object where the transaction will be add\n
        @param newTransaction - the transaction who will be add\n
        @param alivePeers - list of available peers\n
        @return True TODO needed?
    """
    if len(newTransactionCandidate[CryptoFunctions.calculateHash(newTransaction)]) > ((2/3)*len(alivePeers)):
        ChainFunctions.addBlockTransaction(block, newTransaction)
    return True
# Consensus PBFT END

# ################Consensus PoW
# def runPoW():
#     """ Run the PoW consensus to add a new block on the chain """
#     print("I am in runPoW")
#     t1 = time.time()
#     global gwPvt
#     devPubKey = getBlockFromSyncList()
#     blk = ChainFunctions.createNewBlock(devPubKey, gwPvt, consensus)
#     print("Device PubKey (insire runPoW): " + str(devPubKey))
#
#     if(PoWConsensus(blk, gwPub, devPubKey)):
#         t2 = time.time()
#         logger.info("=====6=====>time to execute PoW block consensus: " + '{0:.12f}'.format((t2 - t1) * 1000))
#         print("I finished runPoW")
#     else:
#         t2 = time.time()
#         logger.info("Something went wrong, time to execute PoW Block Consensus" + '{0:.12f}'.format((t2 - t1) * 1000))
#         print("I finished runPoW - Wrong")

def PoWConsensus(newBlock, generatorGwPub, generatorDevicePub):
    """ Make the configurations needed to run consensus trying to generate a block with a specific nonce\n
        @param newBlock - BlockHeader object\n
        @param generatorGwPub - Public key from the peer who want to generate the block\n
        @param generatorDevicePub - Public key from the device who want to generate the block\n
    """
    global peers
    # logger.debug("newBlock received for PoW Consensus")
    signature = verifyBlockCandidate(
        newBlock, generatorGwPub, generatorDevicePub, peers)
    if (signature == False):
        # logger.info("Consesus was not Achieved!!! Block(" + str(newBlock.index) + ") will not added")
        return False
    addVoteBlockPoW(newBlock, generatorGwPub, signature)
    # logger.info("Consensus was achieve, updating peers and finishing operation")
    ChainFunctions.addBlockHeader(newBlock)
    sendBlockToPeers(newBlock)

    return True

def addVoteBlockPoW(newBlock, voterPub, voterSign):
    """ add the signature of a peer into the newBlockCandidate,
        using a list to all gw for a single hash, if the block is valid put the signature \n
        @return True -  why not ? :P   ... TODO why return
    """
    global newBlockCandidate
    blkHash = CryptoFunctions.calculateHashForBlock(newBlock)
    # logger.debug("Adding the block to my local dictionary")
    if(blkHash not in newBlockCandidate):
        # logger.debug("Block is not in the dictionary... creating a new entry for it")
        newBlockCandidate[blkHash] = {}
    newBlockCandidate[blkHash][voterPub] = voterSign
    # print("PoW vote added")
    # newBlockCandidate[CryptoFunctions.calculateHashForBlock(newBlock)][voterPub] = voterSign
    return True

#############################################################################
#############################################################################
######################          Main         ################################
#############################################################################
#############################################################################

# @Roben update to load orchestrator by block index
# get first gw pkey


def loadOrchestratorIndex(index):
    global orchestratorObject
    orchestratorGWblock = ChainFunctions.getBlockByIndex(index)
    orchestratorGWpk = orchestratorGWblock.publicKey
    # print("Public Key inside loadOrchestratorINdex: " + orchestratorGWpk)
    if (orchestratorGWpk == gwPub):  # if I am the orchestrator, use my URI
        uri = myURI
    else:
        uri = getPeerbyPK(orchestratorGWpk)
    # print("loading orchestrator URI: " + uri)
    orchestratorObject = Pyro4.Proxy(uri)
    # return orchestratorObject



def loadOrchestratorContextFirstinPeers():
    global orchestratorContextObject
    global gwContextConsensus
    global peers
    global contextPeers
    uri = myURI

    for context, consensus in gwContextConsensus:
        # print("*********")
        # print("these are my contextPeers: " + str(contextPeers))
        contextFound = False
        for index in range(len(contextPeers)):
            if (contextPeers[index][0] == context):
                # print("Context: " + context + "found, I am not the first peer")
                peerObj = contextPeers[index][1][0].object
                orchestratorContextObject.append([context, peerObj])
                # print("orchestratorContextObject: " + str(orchestratorContextObject))
                contextFound = True

        if (contextFound == False):
            # in the case that it does not has any other peers in list, it is the first of that context
            # print("I am the first peer: ")
            orchestratorContextObject.append([context, Pyro4.Proxy(uri)])
            # print("orchestratorContextObject: " + str(orchestratorContextObject))



def loadOrchestratorFirstinPeers():
    global orchestratorObject
    if(len(peers) < 1):
        uri = myURI
        orchestratorObject = Pyro4.Proxy(uri)
        # logger.info("I am my own orchestrator....")
    else:
        # print("First peer is"+ peers[0].peerURI)
        # uri=peers[0].peerURI
        obj = peers[0].object
        dat = pickle.loads(obj.getMyOrchestrator())
        # print("##My Orchestrator orchestrator: "+str(dat))
        # logger.info("##My Orchestrator orchestrator: "+str(dat))
        orchestratorObject = dat
    # orchestratorObject = Pyro4.Proxy(uri)
    # if (orchestratorGWpk == gwPub): #if I am the orchestrator, use my URI
    #     uri=myURI
    # else:from Crypto import Random
    #     uri = getPeerbyPK(orchestratorGWpk)
    # print("loading orchestrator URI: " + uri)
    # orchestratorObject=Pyro4.Proxy(uri)


def voteNewOrchestrator():
    global myVoteForNewOrchestrator
    global votesForNewOrchestrator
    randomGw = random.randint(0, len(peers) - 1)
    votedURI = peers[randomGw].peerURI
    # print("Selected Gw is: " + str(randomGw))
    # print("My pubKey:"+ str(gwPub))
    # print("votedURI: " + str(votedURI))
    # myVoteForNewOrchestrator = [gwPub, votedURI, CryptoFunctions.signInfo(gwPvt, votedURI)]  # not safe sign, just for test
    myVoteForNewOrchestrator = votedURI
    votesForNewOrchestrator.append(myVoteForNewOrchestrator)
    pickedVote = pickle.dumps(myVoteForNewOrchestrator)
    for count in range(0, (len(peers))):
        # print("testing range of peers: "+ str(count))
        # if(peer != peers[0]):
        obj = peers[count].object
        obj.addVoteOrchestrator(pickedVote)
    # print(str(myVoteForNewOrchestrator))

# @Roben get the next GW PBKEYfrom Crypto import Random
# def setNextOrchestrator(consensus, newOrchestratorIndex):
#     global orchestratorObject
#     if(consensus == 'dBFT'):
#         newOrchestratorbk=ChainFunctions.getBlockByIndex(newOrchestratorIndex)
#         newOrchestratorPK=newOrchestratorbk.publickey
#         uri= getPeerbyPK(newOrchestratorbk)
#         orchestratorObject=Pyro4.Proxy(uri)
#         return orchestratorObject
# ###############################################

# This method "loadOrchestrator() is deprecated... It is not used anymore...


def loadOrchestrator():
    """ Connect the peer to the orchestrator TODO automate connection with orchestrator """
    global orchestratorObject
    # text_file = open("/home/core/nodes/Gw1.txt", "r")#it will add a file to set gw1 as first orchestrator
    text_file = open("/tmp/Gw1.txt", "r")
    uri = text_file.read()
    # print("I load the orchestrator, its URI is: "+uri)
    # print(uri)
    # logger.debug("Orchestrator address loaded")
    orchestratorObject = Pyro4.Proxy(uri)
    text_file.close()


def runMasterThread():
    """ DEPRECATED - initialize the PBFT of the peer """
    # @Roben atualizacao para definir dinamicamente quem controla a votacao - o orchestrator -
    # global currentOrchestrator
    # while(currentOrchestrator == myURI):
    # print("Inside runMasterThread")
    while(True):
        if (orchestratorObject.exposedURI() == myURI):
            if (consensus == "PoW"):
                if(len(blockConsensusCandidateList) > 0):
                    # print("going to runPoW")
                    runPoW()
            if (consensus == "PBFT"):
                if(len(blockConsensusCandidateList) > 0):
                    # print("going to runPBFT")
                    runPBFT()
            if (consensus == "dBFT" or consensus == "Witness3"):
                if(len(blockConsensusCandidateList) > 0):
                    # print("going to rundBFT")
                    rundBFT()
        time.sleep(1)


def saveOrchestratorURI(uri):
    """ save the uri of the orchestrator\n
        @param uri - orchestrator URI
    """
    # text_file = open("/home/core/nodes/Gw1.txt", "w")
    #text_file = open("/tmp/Gw1.txt", "w")
    # text_file.write(uri)
    # text_file.close()


def saveURItoFile(uri):
    """ Save the peer's URI to a file \n
        @param uri - peers URI
    """
    #fname = socket.gethostname()
    #text_file = open(fname, "w")
    # text_file.write(uri)
    # text_file.close()



""" Main function initiate the system"""


def main(nameServerIP_received, nameServerPort_received, local_gatewayName, gatewayContext, poolSize):

    global myURI
    global votesForNewOrchestrator
    global nameServerIP
    global nameServerPort
    global gatewayName
    global blockContext
    global gwContextConsensus
    global consensus
    global sizePool    
    global componentsId
    global deviceName

    gatewayName = local_gatewayName
    nameServerIP = nameServerIP_received
    nameServerPort = nameServerPort_received
    sizePool = poolSize
    deviceName = deviceName + gatewayName

    blockContext =gatewayContext
    # @TODO there is a temporary approach to set consensus of gw
    contextsToSend = []
    #
    # all gw with same contexts
    #
    for i in range(int(gatewayContext)):
        contextStr = "000" + str(i + 1)
    #
        contextConsensus = consensus # using this, it will use same consensus as for blocks for all gw
        contextTuple = (contextStr, contextConsensus)
        contextsToSend.append(contextTuple)
    gwContextConsensus=contextsToSend
    #
    ## 5 gateways in each context IEEEBLOCKCHAIN
    #
    # for i in range(int(gatewayContext)):
    #     contextStr = "000" + str(i + 1)
    #     if((gatewayName=="gwa" or gatewayName=="gwb" or gatewayName=="gwc" or gatewayName=="gwd" or gatewayName=="gwe") and ((i+1) <= (int(gatewayContext)/2))):
    #         contextConsensus = consensus # using this, it will use same consensus as for blocks for all gw
    #         contextTuple = (contextStr, contextConsensus)
    #         contextsToSend.append(contextTuple)
    #     if ((gatewayName == "gwa" or gatewayName == "gwb" or gatewayName == "gwc" or gatewayName == "gwd" or gatewayName == "gwe") and (
    #             (int(gatewayContext) == 1))):
    #         contextConsensus = consensus  # using this, it will use same consensus as for blocks for all gw
    #         contextTuple = ("9999", contextConsensus)
    #         contextsToSend.append(contextTuple)
    #
    #     if ((gatewayName == "gwf" or gatewayName == "gwg" or gatewayName == "gwh" or gatewayName == "gwi" or gatewayName == "gwj") and (
    #             (i + 1) > (int(gatewayContext) / 2))):
    #         contextConsensus = consensus  # using this, it will use same consensus as for blocks for all gw
    #         contextTuple = (contextStr, contextConsensus)
    #         contextsToSend.append(contextTuple)
    # print(gatewayName + " has this contexts: " + str(contextsToSend))
    # gwContextConsensus=contextsToSend
    # initialize Logger
    global logger
    logger = Logger.configure(gatewayName + ".log")

    # create the blockchain
    bootstrapChain2()

    # initialzie some components mocked identification
    for comp in components:
        componentsId.append("SN1234_"+comp+"_"+str(deviceName))

    # print ("Please copy the server address: PYRO:chain.server...... as shown and use it in deviceSimulator.py")
    #with Pyro4.Daemon(getMyIP()) as daemon:
    #    myURI = daemon.register(R2ac, gatewayName)
    #    with Pyro4.locateNS(host=nameServerIP, port=nameServerPort) as ns:
    #        ns.register(name=gatewayName, uri=myURI, safe=False)
    #        connectToPeers(ns)
    #        for name, uri in ns.list().items():
    #            logger.info("Peer:" + name + "(" + uri + ")")
    ns = Pyro4.locateNS(host=nameServerIP, port=nameServerPort)
    daemon = Pyro4.Daemon(getMyIP())
    uri = daemon.register(R2ac, gatewayName)
    # uri = daemon.register(R2ac)
    myURI = str(uri)
    ns.register(name=gatewayName, uri=myURI, safe=False)
    # ns.register(myURI, uri, True)
    connectToPeers(ns)
    bcSize = ChainFunctions.getBlockchainSize()
    # logger.debug("Blockchain size = "+ str(bcSize))
    numberConnectedPeers = len(peers)
    # logger.debug("Number of connecter peers = " + str(numberConnectedPeers))
    if(numberConnectedPeers < 1):
        # logger.debug("Starting the first gateway...")
        # saveOrchestratorURI(myURI)
        # logger.info("Creatin thread....")
        # print("going to master thread")
        loadOrchestratorFirstinPeers()
        loadOrchestratorContextFirstinPeers()
        # firstGwBlock = ChainFunctions.createNewBlock(gwPub, gwPvt, consensus
        # ChainFunctions.addBlockHeader(firstGwBlock)
        # R2ac.updateIOTBlockLedger(firstGwBlock, myName)
        # loadOrchestrator()
        # loadOrchestratorIndex(1)
        # threading.Thread(target=runMasterThread).start()
    else:
        loadOrchestratorFirstinPeers()
        loadOrchestratorContextFirstinPeers()
        # time.sleep(5)
        # print("inside main else")
        # pickedUri = pickle.dumps(myURI)
        # for peer in peers:
        #     obj = peer.object
        #     print("Before gettin last chain blocks")
        #     obj.getLastChainBlocks(pickedUri, ChainFunctions.getBlockchainSize())
        # # loadOrchestratorIndex(1)
        # if (len(peers)>3):
        #     electNewOrchestor()
        # loadOrchestrator()
        # threading.Thread(target=runMasterThread).start()
        # print("tamanho de todos os votos: "+str(len(votesForNewOrchestrator)))
        # print("after getting last chain blocks")

    logger.info("Running SpeedyCHAIN gateway " + gatewayName + " in " + myURI)
    logger.info("Pyro name server: " + nameServerIP + ":" + str(nameServerPort))

    daemon.requestLoop()



if __name__ == '__main__':
    if len(sys.argv[1:]) < 1:
        print("Command line syntax:")
        print("  python -m Gateway.py <name server IP> <name server port> <gateway name>")
        print("  Pyro name server must be running on <name server IP>:<name server port>")
        print("    Run Pyro4: pyro4-ns -n <name server IP> -p <name server port>")
        quit()
    else:
        main()
