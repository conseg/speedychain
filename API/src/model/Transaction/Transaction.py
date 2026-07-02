from ...tools import CryptoFunctions

class Transaction:
    def __init__(self, index, previousHash, timestamp, data, signature, nonce, id = "id"):
        self.index = index
        self.previousHash = previousHash
        self.timestamp = timestamp
        self.data = data
        self.signature = signature
        self.nonce = nonce
        self.identification = id
        self.hash = CryptoFunctions.calculateTransactionHash(self)

    def __str__(self):
        return "%s, %s, %s, %s, %s, %s" % (
            str(self.index), str(self.previousHash), str(self.timestamp), str(self.data), str(self.signature), str(self.nonce))

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def strBlock(self):
        txt = " Index: " + str(self.index) + "\n Previous Hash: " + str(self.previousHash) + "\n Time Stamp: " + str(
            self.timestamp) + "\n Data: " + str(self.data) + "\n Signature: " + str(
            self.signature) + "\n Nonce: " + str(self.nonce) + "\n ID: " + str(self.identification) + "\n Hash: " + str(self.hash) + "\n"
        return txt
    
    def strTransactionToSave(self):
        txt = str(self.timestamp) + "  " + str(self.data) + "  " + str(
            self.signature) + "  " + str(self.nonce) + "  " + str(self.identification)
        return txt

    def setHash(self, hash):
        self.hash = hash
    
    def getDataAndSignatureInsideLifecycle(self):
        """ Gets the data and signature inside the transaction data\n
        The transaction data is a LifecycleEvent with DeviceInfo inside
        """
        splitData = str(self.data).split(', ')
        deviceInfo = splitData[len(splitData)-1]
        splitDeviceInfo = deviceInfo.split(',')
        d = " " + splitDeviceInfo[1]+ " " +splitDeviceInfo[2]
        sig = splitDeviceInfo[0]
        return d, sig