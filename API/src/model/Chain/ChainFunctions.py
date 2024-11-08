import time

from .BlockHeader import BlockHeader
from ..Transaction import Transaction
from ...tools import CryptoFunctions

# from .block_pb2_grpc import *
# from .block_pb2 import *
# from .transaction_pb2_grpc import *
# from .transaction_pb2 import *
import transaction_pb2_grpc
import transaction_pb2
import block_pb2_grpc
import block_pb2

import time
import grpc

BlockHeaderChain = []
max_message_length = 1024 * 1024 * 1024
options = [('grpc.max_receive_message_length', max_message_length)]
channel = grpc.insecure_channel('localhost:50052', options = options)
stub_block = block_pb2_grpc.BlockServiceStub(channel)
stub_transaction = transaction_pb2_grpc.TransactionServiceStub(channel)

##@Roben inserted "consensus" to verify if PoW was selected
def startBlockChain():
    """ Add the genesis block to the chain """
    genesis = getGenesisBlock()
    try:
        request = block_pb2.findBlockRequest(public_key= genesis.publicKey)
        response = stub_block.FindBlock(request)
        if response:
            print("Genesis Block already exists")
            return
    except Exception as e:
        print("Error on startBlockChain")
        # print(e)

    addBlockHeader(genesis)
    # BlockHeaderChain.append(getGenesisBlock())

def createNewBlock(devPubKey, gwPvt, blockContext, consensus, device = "device"):
    """ Receive the device public key and the gateway private key then it generates a new block \n
    @param devPubKey - Public key of the requesting device \n
    @param gwPvt - Private key of the gateway \n

    @return BlockHeader
    """
    # print("Create New Block 1")
    previousExpiredBlockHash = "None"
    previousExpiredBlock = findLastSameBlock(device)
    # print("Create New Block 2")
    if previousExpiredBlock is not False:
        previousExpiredBlockHash = previousExpiredBlock.hash
    # print("Create New Block 3")
    previousBlockSignature = "None"
    if previousExpiredBlockHash is not "None":
        previousBlockSignature = CryptoFunctions.encryptRSA2(previousExpiredBlock.publicKey, previousExpiredBlockHash)
    # print("Create New Block 4")
    newBlock = generateNextBlock("new block", devPubKey, getLatestBlock(), gwPvt, blockContext,
                                 consensus, previousExpiredBlockHash, previousBlockSignature, device)
    ##@Regio addBlockHeader is done during consensus! please take it off for running pbft
    #addBlockHeader(newBlock)
    print("New Block ")
    return newBlock

def addBlockHeader(newBlockHeader):
    """ Receive a new block and append it to the chain \n
    @param newBlockHeader - BlockHeader
    """
    # print("Add Block Header " + str(newBlockHeader.hash))
    try :
        block = block_pb2.Block(index = int(newBlockHeader.index), previous_hash = str(newBlockHeader.previousHash),
                                timestamp = int(newBlockHeader.timestamp), hash = str(newBlockHeader.hash),
                                nonce = int(newBlockHeader.nonce), public_key = str(newBlockHeader.publicKey),
                                block_context = str(newBlockHeader.blockContext), device = str(newBlockHeader.device),
                                previous_expired_block_hash = str(newBlockHeader.previousExpiredBlockHash),
                                previous_block_signature = str(newBlockHeader.previousBlockSignature))
        start = time.time()
        response = stub_block.AddBlock(block)
        end = time.time()
        print("Time to add block: " + str((end - start ) * 1000) + " seconds")
        # print(response)
    except Exception as e:
        print("Error on addBlockHeader")
        print(e)

    # global BlockHeaderChain
    # BlockHeaderChain.append(newBlockHeader)

def addBlockTransaction(block, transaction):
    """ Receive a block and add to it a list of transactions \n
    @param block - BlockHeader \n
    @param transaction - list of transaction
    """
    # block.transactions.append(transaction)
    try:
        print("Add Block Transaction")
        transaction = transaction_pb2.Transaction(
            index = int(transaction.index), previousHash = str(transaction.previousHash), timestamp = int(transaction.timestamp),
            data= str(transaction.data), signature = str(transaction.signature), nonce = int(transaction.nonce),
            identification = str(transaction.identification),
            hash = str(transaction.hash)
        )

        request = transaction_pb2.AddTransactionRequest(block_public_key = str(block.publicKey), transaction = transaction)
        start = time.time()
        response = stub_transaction.AddTransaction(request)
        end = time.time()
        print("Time to add transaction on block: " + str((end - start ) * 1000) + "ms")
        # print(response)
    except Exception as e:
        print("Error on addBlockTransaction")
        print(e)

def getLatestBlock():
    """ Return the latest block on the chain \n
    @return BlockHeader
    """
    # global BlockHeaderChain
    # return BlockHeaderChain[len(BlockHeaderChain) - 1]
    empty = block_pb2.Empty()
    response = stub_block.GetLastBlock(empty)
    block = BlockHeader(index = response.index, previousHash = response.previous_hash, timestamp = response.timestamp,
                        transaction = [], hash = response.hash, nonce = response.nonce,
                        publicKey = response.public_key, blockContext = response.block_context, device = response.device,
                        previousExpiredBlock = response.previous_expired_block_hash, previousBlockSignature = response.previous_block_signature)
    return block

def getLatestBlockTransaction(blk):
    """ Return the latest transaction on a block \n
    @return Transaction
    """
    # return blk.transactions[len(blk.transactions) - 1]
    try:
        request = transaction_pb2.FindLastTransactionRequest(block_public_key=blk.publicKey)
        response = stub_transaction.FindLastTransaction(request)
        print("Get Latest Block Transaction")
        print(response.previousHash)
        print(response.nonce)
        print(response)
        # def __init__(self, index, previousHash, timestamp, data, signature, nonce, id = "id"): self.index = index
        print("Get Latest Block Transaction 2")
        transaction = Transaction.Transaction(index = response.index, previousHash = response.previousHash, timestamp = response.timestamp,
                                data = response.data, signature = response.signature, nonce = response.nonce,
                                id = response.identification, hash = response.hash)
        print("Get Latest Block Transaction 3")
        print(transaction)
        return transaction
    except Exception as e:
        print("Error on getLatestBlockTransaction")
        print(e)

    return None

def getTransactions(block):
    request = transaction_pb2.FindAllTransactionsRequest(block_public_key=block.publicKey)
    # print(block.publicKey)
    response = stub_transaction.FindAllTransactions(request)
    response = response.transactions
    
    # if isinstance(response, list) == False:
        
        # response = [response]
        
    # print(response)
    
    transactions = []

    for tr in response:
        previous_hash = getattr(tr, 'previous_hash', "")
        transaction = Transaction.Transaction(index = tr.index, previousHash = previous_hash,  timestamp = tr.timestamp,
                                  data = tr.data, signature = tr.signature, nonce = tr.nonce,
                                  id = tr.identification, hash = tr.hash)
        transactions.append(transaction)
        
    return transactions


def blockContainsTransaction(block, transaction):
    """ Verify if a block contains a transaction \n
    @param block - BlockHeader object \n
    @param transaction - Transaction object\n
    @return True - the transaction is on the block\n
    @return False - the transcation is not on the block
    """
    try:
        request = transaction_pb2.ExistsTransactionOnBlockRequet(block_public_key = block.publicKey, transaction_hash = transaction.hash)
        response = stub_transaction.ExistsTransactionOnBlock(request)

        return response.exists
    except Exception as e:
        print("Error on blockContainsTransaction")
        print(e)
    # for tr in block.transactions:
        # if tr == transaction:
            # return True

    return False

def findBlockByIndex(index):
    print("Find Block by index")
    print(index)
    try:
        blocks = getFullChain()
        # request = block_pb2.FindBlockRequest(public_key = key)
        # response = stub_block.FindBlock(request)
        # print("findBlock response")
        # print(response)
        # if response:
        #     print("findBlock response true")
        #     block = BlockHeader(index = response.index, previousHash = response.previous_hash, timestamp = response.timestamp,
        #                         transaction = [], hash = response.hash, nonce = response.nonce,
        #                         publicKey = response.public_key, blockContext = response.block_context, device = response.device,
        #                         previousExpiredBlock = response.previous_expired_block_hash, previousBlockSignature = response.previous_block_signature)
        #     return block
        # else:
            # print("findBlock response false")
            # return False
        for b in blocks:
            if b.index == index:
                return b
        return False
    except Exception as e:
        print("Error on findBlock")
        print(e)
        return False
    
def lengthOfBlock(block):
    """ Return the amount of transactions on a block\n
    @param block - BlockHeader object\n
    @return int - length of the block
    """
    try:
        # print("Length of Block")
        # request = block_pb2.LengthRequest(public_key = block.publicKey)
        # response = stub_block.LengthBlock(request)
        # print(response)
        # return response.length
        request = transaction_pb2.FindLastTransactionRequest(block_public_key=block.publicKey)
        response = stub_transaction.FindLastTransaction(request)
        return response.index
    
    except Exception as e:
        print("Error on lengthOfBlock")
        print(e)
        return 0
    # return len(block.transactions)

def findBlock(key):
    """ Search for a specific block in the chain\n
    @param key - Public key of a block \n
    @return BlockHeader - found the block on the chain \n
    @return False - not found the block on the chain
    """
    # global BlockHeaderChain
    # for b in BlockHeaderChain:
    #     if (b.publicKey == key):
    #         return b
    # return False
    print("Find Block with public key")
    print(key)
    try:
        request = block_pb2.FindBlockRequest(public_key = key)
        response = stub_block.FindBlock(request)
        print("findBlock response")
        print(response)
        if response:
            print("findBlock response true")
            block = BlockHeader(index = response.index, previousHash = response.previous_hash, timestamp = response.timestamp,
                                transaction = [], hash = response.hash, nonce = response.nonce,
                                publicKey = response.public_key, blockContext = response.block_context, device = response.device,
                                previousExpiredBlock = response.previous_expired_block_hash, previousBlockSignature = response.previous_block_signature)
            return block
        else:
            print("findBlock response false")
            return False
    except Exception as e:
        print("Error on findBlock")
        print(e)
        return False


def getBlockchainSize():
    """ Return the amount of blocks on the chain \n
    @return int - length of the chain
    """
    # global BlockHeaderChain
    # return len(BlockHeaderChain)
    try:
        empty = block_pb2.Empty()
        response = stub_block.Length(empty)
        return response.length
    except Exception as e:
        print("Error on getBlockchainSize")
        print(e)

def getFullChain():
    """ Return the entire chain\nShowing
    @return BlockHeader[] - list of all blocks on the chain
    """
    # return BlockHeaderChain
    try:
        empty = block_pb2.Empty()
        response = stub_block.GetFullChain(empty)
        blocks = []
        for b in response.blocks:
            
            
            block = BlockHeader(index = b.index, previousHash = b.previous_hash, timestamp = b.timestamp,
                                transaction = [], hash = b.hash, nonce = b.nonce,
                                publicKey = b.public_key, blockContext = b.block_context, device = b.device,
                                previousExpiredBlock = b.previous_expired_block_hash, previousBlockSignature = b.previous_block_signature)
            
            # length = lengthOfBlock(block)
            # block.setNumberOfTransactions(length)
            
            transactions = getTransactions(block)
            block.setTransactions(transactions)
            
            blocks.append(block)
        return blocks
    except Exception as e:
        print("Error on getFullChain")
        print(e)
    return []

def getBlockByIndex(index):
    """ Return the block on a specific position of the chain\n
    @param index - desired block position\n
    @return BlockHeader
    """
    # global BlockHeaderChain
    # for b in BlockHeaderChain:
    #     if (b.index == index):
    #         return b
    # return False
    if (len(BlockHeaderChain) > index):
        return BlockHeaderChain[index]
    else:
        return False

def getGenesisBlock():
    """ Create the genesis block\n
    @return BlockHeader - with the genesis block
    """
    k = """-----BEGIN PUBLIC KEY-----
MIIBojANBgkqhkiG9w0BAQEFAAOCAY8AMIIBigKCAYEA7pjKT5gPTH6tqV4iNB71
u9PANXGkRwl9KI2a6UZVpEF709Xt7Awdd6D1bIDouOpATOI+BKRS49CiNNm+7f2i
Y5q0PydM2kxPORTEJS3DX9CkgCmnjMkAHbqECXpnMW48C1YrzM4r/USGJPDdfpre
0bcHKm786iiAzX4ttg6KuJFZywNpQ2SQXew5oB1l5biXW2wJCHs/nwN/9T4n6Ed/
oGD/NVnBk6u+hHWXmZ8fbdAPuKaOggt3l01PMvaD6P+Rd9jhTXKLyMOK8BxEn3xv
vCShEq6qRHJt6p7KTg3LXn5WQoB5HvBdSPSHqpOgLq0XtKHUhlfBfHd5PX290BYl
f4IB37KeQ1fNji/euU44hKlHHP0pSB3jQw/sFQSQ+IfgXHZe/AlKVsZNeKxtSeKI
cugi/7D3/nCLrQufSLHIc/czJ2VyUUEgYpEc+D+1kQF8H2CmpNg8eDnGrN8D4FJs
h6+xh0H3hNBKaYvyHaSeQYAml1NgQeHlyZfy2yAuU5EFAgMBAAE=
-----END PUBLIC KEY-----"""
    index = 0
    previousHash = "0"
    nonce = 0
    blockContext = "0000"
    time = 1465154705
    device = "device"
    hash = CryptoFunctions.calculateHash(index, previousHash, time, nonce, k, blockContext, device)
    inf = Transaction.Transaction(0, hash, "0", "0", '', 0)
    blk = BlockHeader(index, previousHash, time, inf, hash, nonce, k, blockContext, "None", "None", device)
    return blk

def generateNextBlock(blockData, pubKey, previousBlock, gwPvtKey, blockContext, consensus,
                      previousExpiredBlock, previousBlockSignature, device = "device"):
    """ Receive the information of a new block and create it\n
    @param blockData - information of the new block\n
    @param pubKey - public key of the device how wants to generate the new block\n
    @param previouBlock - BlockHeader object with the last block on the chain\n
    @param gwPvtKey - private key of the gateway\n
    @param consensus - it is specified current consensus adopted
    @return BlockHeader - the new block
    """
    try:
        nextIndex = previousBlock.index + 1
        nextTimestamp = "{:.0f}".format(((time.time() * 1000) * 1000))
        previousBlockHash = CryptoFunctions.calculateHashForBlock(previousBlock)
        nonce = 0
        nextHash = CryptoFunctions.calculateHash(nextIndex, previousBlockHash, nextTimestamp,
                                                nonce, pubKey, blockContext, device)
        if(consensus == 'PoW'):
            # PoW nonce difficulty
            difficulty_bits = 12 #2 bytes or 4 hex or 16 bits of zeros in the left of hash
            target = 2 ** (256 - difficulty_bits) #resulting value is lower when it has more 0 in the left of hash
            while ((long(nextHash,16) > target ) and (nonce < (2 ** 32))): #convert hash to long to verify when it achieve difficulty
                nonce=nonce+1
                nextHash = CryptoFunctions.calculateHash(nextIndex, previousBlockHash, nextTimestamp,
                                                    nonce, pubKey, blockContext, device)
        # print("####nonce = " + str(nonce))
        sign = CryptoFunctions.signInfo(gwPvtKey, nextHash)
        inf = Transaction.Transaction(0, nextHash, nextTimestamp, blockData, sign, 0)
        print("####nonce = " + str(nonce))
        return BlockHeader(nextIndex, previousBlockHash, nextTimestamp, inf, nextHash,
                        nonce, pubKey, blockContext, previousExpiredBlock, previousBlockSignature, device)
    except Exception as e:
        print("Error on generateNextBlock")
        print(e)

def generateNextBlock2(blockData, pubKey, sign, blockContext, timestamp, nonce, index,
                       device, previousExpiredBlock, previousBlockSignature):
    """ Receive the information of a new block and create it\n
    @param blockData - information of the new block\n
    @param pubKey - public key of the device how wants to generate the new block\n
    @param gwPvtKey - private key of the gateway\n
    @param consensus - it is specified current consensus adopted
    @return BlockHeader - the new block
    """
    previousBlock = getLatestBlock()
    nextIndex = index
    previousBlockHash = CryptoFunctions.calculateHashForBlock(previousBlock)
    nextHash = CryptoFunctions.calculateHash(nextIndex, previousBlockHash, timestamp,
                                             nonce, pubKey, blockContext, device)
    inf = Transaction.Transaction(0, nextHash, timestamp, blockData, sign, 0)

    return BlockHeader(nextIndex, previousBlockHash, timestamp, inf, nextHash, nonce, pubKey,
                       blockContext, previousExpiredBlock, previousBlockSignature, device)

def restartChain():
    """ Clear the entire chain """
    global BlockHeaderChain
    BlockHeaderChain = []
    startBlockChain()

def getBlocksById(id):
    """ Return the blocks with a specific device ID\n
    @param id - Block ID name based on device ID\n
    @return Blocks
    """
    blocks = []
    global BlockHeaderChain

    for b in BlockHeaderChain:
        if (b.device in id):
            blocks.append(b)

    return blocks

def getTransactionsWithId(componentId):
    """ Return the transactions with a specific component ID\n
    @param componentId - Transaction ID name based on component ID\n
    @return Transactions
    """
    blocks = getBlocksById(componentId)
    transactions = []
    for b in blocks:
        for t in b.transactions:
            if (t.identification == componentId):
                transactions.append(t)

    return transactions

def findLastSameBlock(deviceId):
    for i in range(len(BlockHeaderChain) - 1, 0, -1):
        if BlockHeaderChain[i].device == deviceId:
            return BlockHeaderChain[i]

    return False
