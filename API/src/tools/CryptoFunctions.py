import base64
import hashlib
# from Crypto.Cipher import AES
# from Crypto.Hash import SHA256
# from Crypto.PublicKey import RSA
# from Crypto.Signature import PKCS1_v1_5

from cryptography.hazmat.primitives.asymmetric import rsa, ec, padding
# from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives import padding as symmetricPadding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


iv = "4242424242424242"
BS = 32
pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
unpad = lambda s: s[0:-ord(s[-1])]

def calculateHash(index, previousHash, timestamp, nonce, key, blockContext, device):
    """ Calculate the hash of all arguments concatenated in the order as declared\n
        @param index - block index\n
        @param previousHash - previous block hash\n
        @param timestamp - generation time of the block\n
        @param nonce - nonce of the block\n
        @param key - key of the block\n
        @param blockContext - blockContext of the block\n
        @param device - device name of the block\n
        @return val - hash of it all
    """
    shaFunc = hashlib.sha256()
    shaFunc.update((str(index) + str(previousHash) + str(timestamp) + str(nonce) + str(
        key) + str(blockContext) + str(device)).encode('utf-8'))
    val = shaFunc.hexdigest()
    return val

def calculateHashForBlock(block):
    """ Receive a block and calulates his hash using the index, previous block hash, timestamp and the public key of the block\n
        @return result of calculateHash function - a hash
    """
    return calculateHash(block.index, block.previousHash, block.timestamp, block.nonce, 
                         block.publicKey, block.blockContext, block.device)

def calculateTransactionHash(blockLedger):
    """ Receive a transaction and calculate the hash\n
        @param blockLedger - transaction object\n
        @return hash of (index + previousHash + timestamp + data + signature) UTF-8
    """
    shaFunc = hashlib.sha256()
    shaFunc.update((str(blockLedger.index) + str(blockLedger.previousHash) + str(blockLedger.timestamp) + str(
        blockLedger.data) + str(blockLedger.signature)+ str(blockLedger.nonce)+ str(blockLedger.identification)).encode('utf-8'))
    val = shaFunc.hexdigest()
    return val

# AES

def encryptAES(text, k):
    """ Receive a key and a text and encrypt it on AES\n
        @param k - key to make the encrypt\n
        @paran text - text that will be encrypted\n
        @return enc64 - text encrypted
    """
    # print("\tentered encryptAES!!")
    try:
        # print("text: {}".format(text))
        # print("key: {}".format(base64.b64encode(k)))
        # print("len(k): {}".format(len(k)))
        
        # instantiates the Cipher algorithm
        cypher = Cipher(algorithms.AES(k),modes.CBC(iv)).encryptor()
        # instantiate the padder and do the padding
        padder = symmetricPadding.PKCS7(algorithms.AES.block_size).padder()
        textPadded = padder.update(text)
        textPadded += padder.finalize()
        # cipher
        cy = cypher.update(textPadded)
        cy += cypher.finalize()
        # encode in b64
        enc64 = base64.b64encode(cy)
        # print("\tsuccessfully exited encryptAES!!")
        return enc64
    except Exception as e:
        # print("\tunsuccessfully exited encryptAES!!")
        print("error: {}".format(e))

def decryptAES(text, k):
    """ Receive a key and a text and decrypt the text with the key using AES \n
        @param k - key to make te decrypt\n
        @param text - text encrypted\n
        @return plainTextUnpadded - text decrypted
    """
    # print("\tentered decryptAES!!")
    try:
        # print("texto: {}".format(text))
        # print("k: {}".format(base64.b64encode(k)))
        # print("k-size: {}".format(len(k)))

        # decode the text in b64
        enc = base64.b64decode(text)
        # instantiates the Cipher algorithm
        decypher = Cipher(algorithms.AES(k),modes.CBC(iv)).decryptor()
        
        # decipher
        plain_text = decypher.update(enc)
        plain_text += decypher.finalize()
        
        # instantiates the unpadder and do the unpadding
        unpadder = symmetricPadding.PKCS7(algorithms.AES.block_size).unpadder()
        plainTextUnpadded = unpadder.update(plain_text)
        plainTextUnpadded += unpadder.finalize()
        
        # print("plaintext: {}".format(plainTextUnpadded))
        # print("\tsuccessfully exited decryptAES!!")
        return plainTextUnpadded
    except Exception as e:
        # print("\tunsuccessfully exited decryptAES!!")
        print("error: {}".format(e))
        
## RSA

def encryptRSA2(key, plaintext):
    """ Receive a key and a text and encrypt it on Base 64\n
        @param key - key to make the encrypt\n
        @paran text - text that will be encrypted\n
        @return ciphertext64 - text encrypted in base64
    """    
    # print("\tentered encryptRSA!!")
    try:
        print("key: \n{}size: {}".format(key,len(key)))
        
        #load key
        key = key.encode('utf-8')
        pubkey = serialization.load_pem_public_key(
            key
        )
        # print("\tsuccessfully loaded the key!!")
        
        # encrypt the text
        ciphertext = pubkey.encrypt(
            plaintext,
            padding.OAEP(
                mgf=padding.MGF1(hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        # encode the ciphertext in b64
        ciphertext64 = base64.b64encode(ciphertext)
        
        # print("\tsuccessfully exited encryptRSA!!")
    except Exception as e:
        # print("\tunsuccessfully exited encryptRSA!!")
        print("error: {}".format(e))
    return ciphertext64

def decryptRSA2(key, ciphertext,password=None):
    """ Receive a key and a text and decrypt the text with the key using Base 64 \n
        @param key - key to make te decrypt\n
        @param text - text encrypted\n
        @return data - text decrypted
    """    
    # print("\tentered decryptRSA2!!")
    try:
        #load key
        key = key.encode('utf-8')
        privkey = serialization.load_pem_private_key(
            key,
            password
        )
        # print("\tsuccessfully loaded key!!")

        # decipher
        plaintext = privkey.decrypt(
            # decode the b64 ciphertext
            base64.b64decode(ciphertext),
            padding.OAEP(
                mgf=padding.MGF1(hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        # print("\tsuccessfully exited decryptRSA!!")
        return plaintext    
    except Exception as e:
        # print("\tunsuccessfully exited decryptRSA!!")
        print("error: {}".format(e))
        return ""

def signInfo(gwPvtKey, data,password=None):
    """ Sign some data with the peer's private key\n 
        @param gwPvtKey - peer's private key\n
        @param data - data to sign\n
        @return sinature - signature of the data maked with the private key
    """
    # print("\tentered signInfo!!")
    try:
        # load key
        key = gwPvtKey.encode('utf-8')
        privkey = serialization.load_pem_private_key(
            key,
            password
        )
        # print("\tsuccessfully loaded key!!")
        
        # sign the data
        # TODO prehashed
        sig = privkey.sign(
            data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        # print("\tsuccessfully signed!!")

        # encode the signature in b64
        signature = base64.b64encode(sig)
        # print("b64 signature: {}".format(signature))
        # print("\tsuccessfully exited signInfo!!")
        return signature
    except Exception as e:
        # print("\tunsuccessfully exited signInfo!!")
        print("error: {}".format(e))
        return ""

def signVerify(data, signature, gwPubKey):
    """ Verify if a data sign by a private key it's unaltered\n
        @param data - data to be verified\n
        @param signature - signature of the data to be validated\n
        @param gwPubKey - peer's private key
    """
    # print("\tentered signVerify!!")
    try:
        #load key
        key = gwPubKey.encode('utf-8')
        pubkey = serialization.load_pem_public_key(
            key
        )
        # print("\tsuccessfully loaded key!!")
        
        # verify the signature
        # TODO prehashed
        pubkey.verify(
            # decode the b64 signature
            base64.b64decode(signature),
            data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        # print("\tvalid signature!!")
        # print("\tsuccessfully exited signVerify!!")
        return True
    except Exception as e:
        # print("\tunsuccessfully exited signVerify!!")
        print("error: {}".format(e))
        return False

def generateRSAKeyPair():
    """ Generate a pair of RSA keys using RSA 3072\n
        @return pub, prv - public and private key
    """
    # print("entered generate RSA keys")
    try:
        keysize = 3072
        publicexpoent = 65537

        private = rsa.generate_private_key(
            publicexpoent,
            key_size=keysize
        )
        pubKey = private.public_key()
        
        prv = private.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        pub = pubKey.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo    
        )
        
        # print("successfully exited generate RSA keys")
        return pub, prv
    except Exception as e:
        # print("\tunsuccessfully exited generate RSA keys")
        print("error: {}".format(e))
        return "",""

## ECC/ECDSA

def signInfoECDSA(gwPvtKey, data,password=None):
    """ Sign some data with the peer's private key\n 
        @param gwPvtKey - peer's private key\n
        @param data - data to sign\n
        @return sinature - signature of the data maked with the private key
    """
    # print("\tentered signInfoECDSA!!")
    try:
        #load key
        key = gwPvtKey.encode('utf-8')
        privatekey = serialization.load_pem_private_key(
            key,
            password
        )
        # print("successfully loaded key!!")

        # sign the data
        # TODO prehashed
        sign = privatekey.sign(
            data,
            ec.ECDSA(hashes.SHA256())
        )
        # print("successfully signed!!")

        # encode the signature in b64
        signatureb64 = base64.b64encode(sign)
        # print("assinaturab64: {}".format(signatureb64))
        # print("\tsuccessfully exited signInfoECDSA!!")
        return signatureb64
    except Exception as e:
        # print("\tunsuccessfully exited signInfoECDSA!!")
        print("error: {}".format(e))
        return ""

def signVerifyECDSA(data, signature, gwPubKey):
    """ Verify if a data sign by a private key it's unaltered\n
        @param data - data to be verified\n
        @param signature - signature of the data to be validated\n
        @param gwPubKey - peer's private key
    """
    # print("\tentered signInfoECDSA!!")
    try:
        # load key
        key = gwPubKey.encode('utf-8')
        publickey = serialization.load_pem_public_key(
            key
        )
        # print("successfully loaded key!!")

        # verify the signature
        # TODO prehashed
        publickey.verify(
            # decode the b64 signature
            base64.b64decode(signature),
            data,
            ec.ECDSA(hashes.SHA256())
        )
        print("valid signature!!")
        # print("\tsuccessfully exited signVerifyECDSA!!")
        return True
    except Exception as e:
        # print("\tunsuccessfully exited signVerifyECDSA!!")
        print("error: {}".format(e))
        return False

def generateECDSAKeyPair():
    """ Generate a pair of ECDSA keys using SECP256R1\n
        @return pub, prv - public and private key
    """
    # print("\tentered generate ECDSA keys!!")
    try:
        privatekey = ec.generate_private_key(
            ec.SECP256R1
        )
        publickey = privatekey.public_key()
        
        prv = privatekey.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        pub = publickey.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        # print("\tsuccessfully exited generate ECDSA keys!!")
        return pub, prv
    except Exception as e:
        # print("\tunsuccessfully exited generate ECDSA keys!!")
        print("error: {}".format(e))
        return "",""

# ECDH

def generateSharedKey(myPrivatekey,otherPublicKey,password=None):
    """ Stabilish a new shared key between two parties\n
        @Param myPrivateKey - the private key of the part using this function\n
        @Param otherPublicKey - the public key of the part to share the key\n
        @Return sharedKey - the key shared between the parties
    """
    # print("\tentered generateSharedKey!!")
    try:
        # load keys
        myPrivatekey = myPrivatekey.encode('utf-8')
        DHPrivKey = serialization.load_pem_private_key(
            myPrivatekey,
            password
        )
        otherPublicKey = otherPublicKey.encode('utf-8')
        DHPubKey = serialization.load_pem_public_key(
            otherPublicKey
        )
        # print("\tsuccessfully loaded keys!!")
        
        sharedKey = DHPrivKey.exchange(ec.ECDH(),DHPubKey)
        # print("sharedKey: {}".format(type(sharedKey)))
        # print("\tsuccessfully exited generateSharedKey!!")
        return sharedKey
    except Exception as e:
        # print("\tsuccessfully exited generateSharedKey!!")
        print("error: {}".format(e))

