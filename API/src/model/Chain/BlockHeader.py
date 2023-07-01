class BlockHeader:
    #Nonce field added for PoW
    def __init__(self, index, previousHash, timestamp, transaction, hash, nonce, publicKey, blockContext, device = "device"):
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
            self.device) + "\n Number of transactions: " + str(len(self.transactions)) + "\n"

        return txt
    
    def strBlockToSave(self):
        transaction = self.transactions[0]
        txt = str(self.publicKey).replace('\n', '\\n') + "  " + str(self.blockContext) + "  " + str(
            self.timestamp) + "  " + str(self.nonce) + "  " + str(transaction.signature) + "  " + str(
            transaction.data) + "  " + str(self.index)  + "  " + str(self.device)

        return txt
