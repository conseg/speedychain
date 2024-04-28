import time

from .BlockHeader import BlockHeader
from ..Transaction import Transaction
from ...tools import CryptoFunctions

import block_pb2_grpc
import block_pb2
import transaction_pb2_grpc
import transaction_pb2
import time
import grpc

BlockHeaderChain = []

channel = grpc.insecure_channel('localhost:50051')
stub_block = block_pb2_grpc.BlockServiceStub(channel)
stub_transaction = transaction_pb2_grpc.TransactionServiceStub(channel)

##@Roben inserted "consensus" to verify if PoW was selected
def startBlockChain():
    """ Add the genesis block to the chain """
    genesis = getGenesisBlock()
    try: 
        request = block_pb2.FindBlockRequest(public_key= genesis.publicKey)
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
    print("Create New Block 1")
    previousExpiredBlockHash = "None"
    previousExpiredBlock = findLastSameBlock(device)
    print("Create New Block 2")
    if previousExpiredBlock is not False:
        previousExpiredBlockHash = previousExpiredBlock.hash
    print("Create New Block 3")
    previousBlockSignature = "None"
    if previousExpiredBlockHash is not "None":
        previousBlockSignature = CryptoFunctions.encryptRSA2(previousExpiredBlock.publicKey, previousExpiredBlockHash)
    print("Create New Block 4")
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
    print("Add Block Header " + str(newBlockHeader.hash))
    try :
        block = block_pb2.Block(index = int(newBlockHeader.index), previous_hash = str(newBlockHeader.previousHash),
                                timestamp = int(newBlockHeader.timestamp), hash = str(newBlockHeader.hash),
                                nonce = int(newBlockHeader.nonce), public_key = str(newBlockHeader.publicKey),
                                block_context = str(newBlockHeader.blockContext), device = str(newBlockHeader.device),                           
                                previous_expired_block_hash = str(newBlockHeader.previousExpiredBlockHash),
                                previous_block_signature = str(newBlockHeader.previousBlockSignature))
        response = stub_block.AddBlock(block)
        print(response)
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
        transaction = transaction_pb2.Transaction(
            index = int(transaction.index), previous_hash = str(transaction.previousHash), timestamp = str(transaction.timestamp),
            data= str(transaction.data), signature = str(transaction.signature), nonce = int(transaction.nonce),
            identification = str(transaction.identification),
            hash = str(transaction.hash),
        )
        
        request = block_pb2.AddTransactionRequest(block_hash = block.publicKey, transaction = transaction)
        stub_transaction.AddTransaction(request)
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
    return blk.transactions[len(blk.transactions) - 1]

def blockContainsTransaction(block, transaction):
    """ Verify if a block contains a transaction \n
    @param block - BlockHeader object \n
    @param transaction - Transaction object\n
    @return True - the transaction is on the block\n
    @return False - the transcation is not on the block
    """
    for tr in block.transactions:
        if tr == transaction:
            return True

    return False

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
        if response:
            block = BlockHeader(index = response.index, previousHash = response.previous_hash, timestamp = response.timestamp,
                                transaction = response.transactions, hash = response.hash, nonce = response.nonce,
                                publicKey = response.public_key, blockContext = response.block_context, device = response.device,
                                previousExpiredBlock = response.previous_expired_block_hash, previousBlockSignature = response.previous_block_signature)
            return block 
        else:
            return False
    except Exception as e:
        return False
        # print("Error on findBlock")
        # print(e)

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
MFwwDQYJKoZIhvcNAQEBBQADSwAwSAJBAM39ONP614uHF5m3C7nEh6XrtEaAk2ys
LXbjx/JnbnRglOXpNHVu066t64py5xIP8133AnLjKrJgPfXwObAO5fECAwEAAQ==
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