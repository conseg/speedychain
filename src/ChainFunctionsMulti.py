import time

import BlockHeaderMulti
import Transaction
import CryptoFunctions

BlockHeaderChain = []

##This code manages the chain functions with multiple transaction chains
def startBlockChain(t):
    """ Add the genesis block to the chain 
    @param t - Current timestamp \n
    """
    BlockHeaderChain.append(getGenesisBlock(t))

def createNewBlock(devPubKey, gwPvt, blockContext, consensus):
    """ Receive the device public key and the gateway private key then it generates a new block \n
    @param devPubKey - Public key of the requesting device \n
    @param gwPvt - Private key of the gateway \n

    @return BlockHeader
    """
    newBlock = generateNextBlock("new block", devPubKey, getLatestBlock(), gwPvt, blockContext, consensus)
    ##@Regio addBlockHeader is done during consensus! please take it off for running pbft
    #addBlockHeader(newBlock)
    return newBlock

def addBlockHeader(newBlockHeader):
    """ Receive a new block and append it to the chain \n
    @param newBlockHeader - BlockHeader
    """
    global BlockHeaderChain
    BlockHeaderChain.append(newBlockHeader)

def addBlockTransaction(block, transaction, index):
    """ Receive a block and add to it a list of transactions \n
    @param block - BlockHeader \n
    @param transaction - list of transaction \n
    @param index - index of chain of transactions
    """
    block.transactions[index].append(transaction)

def getLatestBlock():
    """ Return the latest block on the chain \n
    @return BlockHeader
    """
    global BlockHeaderChain
    return BlockHeaderChain[len(BlockHeaderChain) - 1]

def getLatestBlockTransaction(blk, index):
    """ Return the latest transaction on a block \n
    @param blk - BlockHeader object \n
    @param index - Transaction chain index\n
    @return Transaction
    """
    return blk.transactions[index][len(blk.transactions[index]) - 1]

def blockContainsTransaction(block, transaction, index):
    """ Verify if a block contains a transaction \n
    @param block - BlockHeader object \n
    @param transaction - Transaction object\n
    @param index - Transaction chain index\n
    @return True - the transaction is on the block\n
    @return False - the transcation is not on the block
    """
    for tr in block.transactions[index]:
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

def getGenesisBlock(t):
    """ Create the genesis block\n
    @param t - current timestamp\n
    @return BlockHeaderMulti - with the genesis block
    """
    k = """-----BEGIN PUBLIC KEY-----
MFwwDQYJKoZIhvcNAQEBBQADSwAwSAJBAM39ONP614uHF5m3C7nEh6XrtEaAk2ys
LXbjx/JnbnRglOXpNHVu066t64py5xIP8133AnLjKrJgPfXwObAO5fECAwEAAQ==
-----END PUBLIC KEY-----"""
    index = 0
    previousHash = "0"
    nonce = 0
    blockContext = "0000"
    hash = CryptoFunctions.calculateHash(index, previousHash, t, nonce, k, blockContext)
    inf = Transaction.Transaction(0, hash, "0", "0", '', 0)
    blk = BlockHeaderMulti.BlockHeaderMulti(index, previousHash, t, inf, hash, nonce, k, blockContext)
    return blk

def generateNextBlock(blockData, pubKey, previousBlock, gwPvtKey, blockContext, consensus):
    """ Receive the information of a new block and create it\n
    @param blockData - information of the new block\n
    @param pubKey - public key of the device how wants to generate the new block\n
    @param previouBlock - BlockHeader object with the last block on the chain\n
    @param gwPvtKey - private key of the gateway\n
    @param consensus - it is specified current consensus adopted
    @return BlockHeader - the new block
    """
    nextIndex = previousBlock.index + 1    
    nextTimestamp = time.time()
    previousBlockHash = CryptoFunctions.calculateHashForBlock(previousBlock)
    nonce = 0
    nextHash = CryptoFunctions.calculateHash(nextIndex, previousBlockHash, nextTimestamp, nonce, pubKey, blockContext)
    if(consensus == 'PoW'):
        # PoW nonce difficulty
        difficulty_bits = 12 #2 bytes or 4 hex or 16 bits of zeros in the left of hash
        target = 2 ** (256 - difficulty_bits) #resulting value is lower when it has more 0 in the left of hash
        while ((long(nextHash,16) > target ) and (nonce < (2 ** 32))): #convert hash to long to verify when it achieve difficulty
          nonce=nonce+1
          nextHash = CryptoFunctions.calculateHash(nextIndex, previousBlockHash, nextTimestamp, nonce, pubKey, blockContext)
    # print("####nonce = " + str(nonce))
    sign = CryptoFunctions.signInfo(gwPvtKey, nextHash)
    inf = Transaction.Transaction(0, nextHash, nextTimestamp, blockData, sign, 0)

    return BlockHeaderMulti.BlockHeaderMulti(nextIndex, previousBlockHash, nextTimestamp, inf, nextHash, nonce, pubKey, blockContext)

def generateNextBlock2(blockData, pubKey, sign, blockContext, timestamp, nonce):
    """ Receive the information of a new block and create it\n
    @param blockData - information of the new block\n
    @param pubKey - public key of the device how wants to generate the new block\n
    @param gwPvtKey - private key of the gateway\n
    @param consensus - it is specified current consensus adopted
    @return BlockHeader - the new block
    """
    previousBlock = getLatestBlock()
    nextIndex = previousBlock.index + 1
    previousBlockHash = CryptoFunctions.calculateHashForBlock(previousBlock)
    nextHash = CryptoFunctions.calculateHash(nextIndex, previousBlockHash, timestamp, nonce, pubKey, blockContext)
    inf = Transaction.Transaction(0, nextHash, timestamp, blockData, sign, 0)

    return BlockHeaderMulti.BlockHeaderMulti(nextIndex, previousBlockHash, timestamp, inf, nextHash, nonce, pubKey, blockContext)

def restartChain():
    """ Clear the entire chain """
    BlockHeaderChain = []
    BlockHeaderChain.append(getGenesisBlock())
