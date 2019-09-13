class Transaction:
    def __init__(self, index, previousHash, timestamp, data, signature, nonce):
        self.index = index
        self.previousHash = previousHash
        self.timestamp = timestamp
        self.data = data
        self.signature = signature
        self.nonce = nonce

    def __str__(self):
        return "%s,%s,%s,%s,%s" % (
            str(self.index), str(self.previousHash), str(self.timestamp), str(self.data), str(self.signature), str(self.signature))

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def strBlock(self):
        txt = "Index: " + str(self.index) + "\n Previous Hash: " + str(self.previousHash) + "\n Time Stamp: " + str(
            self.timestamp) + "\n Data: " + str(self.data) + "\n Signature: " + str(
            self.signature) + "\n" + str(self.nonce) + "\n"
        return txt