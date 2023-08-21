class BlockHeader:
    #Nonce field added for PoW
    def __init__(self, index, previousHash, timestamp, transaction, hash, nonce, publicKey, blockContext, 
                 previousExpiredBlock, previousBlockSignature, device = "device"):
        self.index = index
        self.previousHash = previousHash
        self.timestamp = timestamp
        self.transactions = []
        self.transactions.append(transaction)
        self.hash = hash
        self.nonce = nonce
        self.publicKey = publicKey
        self.blockContext = blockContext
        self.device = device
        self.previousExpiredBlockHash = previousExpiredBlock
        self.previousBlockSignature = previousBlockSignature

    def __str__(self):
        return "%s,%s,%s,%s,%s,%s,%s,%s,%s" % (
            str(self.index), str(self.previousHash), str(self.timestamp), str(self.transactions), str(self.hash), str(self.nonce),
            str(self.publicKey), str(self.blockContext), str(self.device))

    def __repr__(self):
        return "<%s, %s, %s, %s, %s, %s, %s, %s>" % (
            str(self.index), str(self.previousHash), str(self.timestamp), str(self.transactions), str(self.hash), str(self.nonce),
            str(self.publicKey), str(self.blockContext))

    def strBlock(self):
        txt = " Index: " + str(self.index) + "\n Previous Hash: " + str(self.previousHash) + "\n Time Stamp: " + str(
            self.timestamp) + "\n Hash: " + str(self.hash) + "\n Nonce:" + str(self.nonce) + "\n Public Key: " + str(
            self.publicKey) + "\n Block Context: " + str(self.blockContext) + "\n Device: " + str(
            self.device) + "\n Number of transactions: " + str(len(
            self.transactions)) + "\n Previous expired block hash: " + str(
            self.previousExpiredBlockHash) + "\n Previous block signature: " + str(
            self.previousBlockSignature) + "\n"

        return txt
    
    def strBlockToSave(self):
        transaction = self.transactions[0]
        txt = str(self.publicKey).replace('\n', '\\n') + "  " + str(self.blockContext) + "  " + str(
            self.timestamp) + "  " + str(self.nonce) + "  " + str(transaction.signature) + "  " + str(
            transaction.data) + "  " + str(self.index) + "  " + str(self.device) + "  " + str(
            self.previousExpiredBlockHash) + "  " + str(self.previousBlockSignature)

        return txt
