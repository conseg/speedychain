class BlockHeaderMulti:
    #Nonce field added for PoW
    def __init__(self, index, previousHash, timestamp, transaction, hash, nonce, publicKey, blockContext, numTransactionChains = 4):
        self.index = index
        self.previousHash = previousHash
        self.timestamp = timestamp
        self.transactions = []
        self.numTransactionChains = int(numTransactionChains)
        for i in range(self.numTransactionChains):
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
            self.publicKey) + "\n Block Context: " + str(self.blockContext) + "\n Number of transaction chains: " + str(
            self.numTransactionChains)
        
        i = 0
        for transactionChain in self.transactions:
            txt = txt + "\n Number of transactions " + str(i) + ": " + str(len(transactionChain))
            i = i + 1

        txt = txt + "\n"
        return txt

    def strBlockToSave(self):
        transaction = self.transactions[0][0]
        txt = str(self.publicKey).replace('\n', '\\n') + "  " + str(self.blockContext) + "  " + str(self.timestamp) + "  " + str(
            self.nonce) + "  " + str(transaction.signature) + "  " + str(transaction.data) + "  " + str(
            self.numTransactionChains)  + "  " + str(self.index) 

        return txt
