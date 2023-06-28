class LifecycleEvent:
    #Nonce field added for PoW
    def __init__(self, type, id, data, index = 0):
        self.index = index
        self.type = type
        self.id = id
        self.data = data

    def __str__(self):
        return "%s, %s, %s, %s" % (
            str(self.index), str(self.type), str(self.id), str(self.data))

    def __repr__(self):
        return "<%s, %s, %s, %s>" % (
            str(self.index), str(self.type), str(self.id), str(self.data))

    def strEvent(self):
        txt = "Index: " + str(self.index) + "\n Data type: " + str(self.type) + "\n Identification: " + str(
            self.id) + "\n Data: " + str(self.data) + "\n"

        return txt

    #def strBlockToSave(self):
        #txt = str(self.publicKey).replace('\n', '\\n') + "  " + str(self.blockContext) + "  " + str(self.timestamp) + "  " + str(
            #self.nonce) + "  " + str(transaction.signature) + "  " + str(transaction.data)
        #return txt
