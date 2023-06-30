import time

from .BlockHeader import BlockHeader
from ..Transaction import Transaction
from ...tools import CryptoFunctions

BlockHeaderChain = []

##@Roben inserted "consensus" to verify if PoW was selected
def startBlockChain():
    """ Add the genesis block to the chain """
    BlockHeaderChain.append(getGenesisBlock())

def createNewBlock(devPubKey, gwPvt, blockContext, consensus, device = "dev"):
    """ Receive the device public key and the gateway private key then it generates a new block \n
    @param devPubKey - Public key of the requesting device \n
    @param gwPvt - Private key of the gateway \n

    @return BlockHeader
    """
    newBlock = generateNextBlock("new block", devPubKey, getLatestBlock(), gwPvt, blockContext, 
                                 consensus, device)
    ##@Regio addBlockHeader is done during consensus! please take it off for running pbft
    #addBlockHeader(newBlock)
    return newBlock

def addBlockHeader(newBlockHeader):
    """ Receive a new block and append it to the chain \n
    @param newBlockHeader - BlockHeader
    """
    global BlockHeaderChain
    BlockHeaderChain.append(newBlockHeader)

def addBlockTransaction(block, transaction):
    """ Receive a block and add to it a list of transactions \n
    @param block - BlockHeader \n
    @param transaction - list of transaction
    """
    block.transactions.append(transaction)

def getLatestBlock():
    """ Return the latest block on the chain \n
    @return BlockHeader
    """
    global BlockHeaderChain
    return BlockHeaderChain[len(BlockHeaderChain) - 1]

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
    global BlockHeaderChain
    for b in BlockHeaderChain:
        if (b.publicKey == key):
            return b
    return False

def getBlockchainSize():
    """ Return the amount of blocks on the chain \n
    @return int - length of the chain
    """
    global BlockHeaderChain
    return len(BlockHeaderChain)

def getFullChain():
    """ Return the entire chain\nShowing
    @return BlockHeader[] - list of all blocks on the chain
    """
    return BlockHeaderChain

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
    device = "dev"
    hash = CryptoFunctions.calculateHash(index, previousHash, time, nonce, k, blockContext, device)
    inf = Transaction.Transaction(0, hash, "0", "0", '', 0)
    blk = BlockHeader(index, previousHash, time, inf, hash, nonce, k, blockContext, device)
    return blk

def generateNextBlock(blockData, pubKey, previousBlock, gwPvtKey, blockContext, consensus, device = "dev"):
    """ Receive the information of a new block and create it\n
    @param blockData - information of the new block\n
    @param pubKey - public key of the device how wants to generate the new block\n
    @param previouBlock - BlockHeader object with the last block on the chain\n
    @param gwPvtKey - private key of the gateway\n
    @param consensus - it is specified current consensus adopted
    @return BlockHeader - the new block
    """
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

    return BlockHeader(nextIndex, previousBlockHash, nextTimestamp, inf, nextHash, 
                       nonce, pubKey, blockContext, device)

def generateNextBlock2(blockData, pubKey, sign, blockContext, timestamp, nonce, index, device):
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

    return BlockHeader(nextIndex, previousBlockHash, timestamp, inf, nextHash, 
                       nonce, pubKey, blockContext, device)

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
        if (b.blockContext in id):
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