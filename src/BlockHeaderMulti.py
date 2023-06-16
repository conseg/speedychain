class BlockHeaderMulti:
    #Nonce field added for PoW
    def __init__(self, index, previousHash, timestamp, transaction, hash, nonce, publicKey, blockContext):
        self.index = index
        self.previousHash = previousHash
        self.timestamp = timestamp
        self.transactions = []
        for i in range(4):
            a = []
            a.append(transaction)
            self.transactions.append(a)
        self.hash = hash
        self.nonce = nonce
        self.publicKey = publicKey
        self.blockContext = blockContext

    def __str__(self):
        return "%s,%s,%s,%s,%s,%s,%s,%s" % (
            str(self.index), str(self.previousHash), str(self.timestamp), str(self.transactions), str(self.hash), str(self.nonce),
            str(self.publicKey), str(self.blockContext))

    def __repr__(self):
        return "<%s, %s, %s, %s, %s, %s, %s, %s>" % (
            str(self.index), str(self.previousHash), str(self.timestamp), str(self.transactions), str(self.hash), str(self.nonce),
            str(self.publicKey), str(self.blockContext))

    def strBlock(self):
        txt = " Index: " + str(self.index) + "\n Previous Hash: " + str(self.previousHash) + "\n Time Stamp: " + str(
            self.timestamp) + "\n Hash: " + str(self.hash) + "\n Nonce:" + str(self.nonce) + "\n Public Key: " + str(
            self.publicKey) + "\n Block Context: " + str(self.blockContext) + "\n Number of transactions[0]: " + str(
            len(self.transactions[0])) + "\n Number of transactions[1]: " + str(len(self.transactions[1])
            ) + "\n Number of transactions[2]: " + str(len(self.transactions[2])) + "\n Number of transactions[3]: " + str(
            len(self.transactions[3])) + "\n"

        return txt

    def strBlockToSave(self):
        transaction = self.transactions[0]
        txt = str(self.publicKey).replace('\n', '\\n') + "  " + str(self.blockContext) + "  " + str(self.timestamp) + "  " + str(
            self.nonce) + "  " + str(transaction.signature) + "  " + str(transaction.data)

        return txt