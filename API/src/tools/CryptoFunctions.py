import base64
import hashlib
# from Crypto.Cipher import AES
# from Crypto.Hash import SHA256
# from Crypto.PublicKey import RSA
# from Crypto.Signature import PKCS1_v1_5
# from Crypto.Cipher import PKCS1_OAEP

from cryptography.hazmat.primitives.asymmetric import rsa, padding, ec
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
    # print("\tentrou no encryptAES!!")
    try:
        # print("text: {}".format(text))
        # print("key: {}".format(base64.b64encode(k)))
        # print("len(k): {}".format(len(k)))
        # instancia o algoritmo de Cifra
        cypher = Cipher(algorithms.AES(k),modes.CBC(iv)).encryptor()
        # instancia o padder e faz o padding
        padder = symmetricPadding.PKCS7(algorithms.AES.block_size).padder()
        textPadded = padder.update(text)
        textPadded += padder.finalize()
        #cifra
        cy = cypher.update(textPadded)
        cy += cypher.finalize()
        #encoda em b64
        enc64 = base64.b64encode(cy)
        # print("\tsaiu do encryptAES com sucesso!!")
        return enc64
    except Exception as e:
        # print("\tsaiu do encryptAES sem sucesso!!")
        print("erro: {}".format(e))
    # cypher = AES.new(k, AES.MODE_CBC, iv)
    # textPadded = pad(text)
    # cy = cypher.encrypt(textPadded)
    # enc64 = base64.b64encode(cy)
    # return enc64

def decryptAES(text, k):
    """ Receive a key and a text and decrypt the text with the key using AES \n
        @param k - key to make te decrypt\n
        @param text - text encrypted\n
        @return plainTextUnpadded - text decrypted
    """
    # print("\tentrou no decryptAES!!")
    try:
        # print("texto: {}".format(text))
        # print("k: {}".format(base64.b64encode(k)))
        # print("k-size: {}".format(len(k)))

        # decode the text in b64
        enc = base64.b64decode(text)
        # instancia o algoritmo de Cifra
        decypher = Cipher(algorithms.AES(k),modes.CBC(iv)).decryptor()
        
        #decifra
        plain_text = decypher.update(enc)
        plain_text += decypher.finalize()
        
        # instancia o unpadder e faz o unpadding
        unpadder = symmetricPadding.PKCS7(algorithms.AES.block_size).unpadder()
        plainTextUnpadded = unpadder.update(plain_text)
        plainTextUnpadded += unpadder.finalize()
        
        # print("plaintext: {}".format(plainTextUnpadded))
        
        # print("\tsaiu do decryptAES com sucesso!!")
        return plainTextUnpadded
    except Exception as e:
        # print("\tsaiu do decryptAES sem sucesso!!")
        print("erro: {}".format(e))
        
    # enc = base64.b64decode(text)
    # decryption_suite = AES.new(k, AES.MODE_CBC, iv)
    # plain_text = decryption_suite.decrypt(enc)
    # plainTextUnpadded = unpad(plain_text)
    # return plainTextUnpadded

# RSA

def encryptRSA2(key, plaintext):
    """ Receive a key and a text and encrypt it on Base 64\n
        @param key - key to make the encrypt\n
        @paran text - text that will be encrypted\n
        @return enc64 - text encrypted
    """
    try:
        # print("\tentrou no encryptRSA!!")
        # print("key: \n{}size: {}".format(key,len(key)))
                
        key = key.encode('utf-8')
        
        #load key
        pubkey = serialization.load_pem_public_key(
            key
        )
        
        # print("\tcarregou a chave com sucesso!!")
        #encrypt the text
        ciphertext = pubkey.encrypt(
            plaintext,
            padding.OAEP(
                mgf=padding.MGF1(hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        #encode the ciphertext in b64
        ciphertext64 = base64.b64encode(ciphertext)
        
        # print("saiu do encryptRSA com ciphertext: \n{}".format(ciphertext64))
        # print("\tsaiu do encryptRSA!!")
    except Exception as e:
        print("saiu do encryptRSA com erro")
        print("erro: {}".format(e))
    return ciphertext64
    # k = RSA.importKey(key)
    # # enc = k.encrypt(text, 42)[0]
    # Cipher = PKCS1_OAEP.new(k)
    # enc = Cipher.encrypt(text)
    # enc64 = base64.b64encode(enc)
    # return enc64

def decryptRSA2(key, ciphertext, password=None):
    """ Receive a key and a text and decrypt the text with the key using Base 64 \n
        @param key - key to make te decrypt\n
        @param text - text encrypted\n
        @return data - text decrypted
    """
    try:
        # print("\tentrou no decryptRSA2!!")
        key = key.encode('utf-8')
        #load key
        privkey = serialization.load_pem_private_key(
            key,
            password
        )
        # print("\tcarregou a chave sem erro!!")
        #decifra
        plaintext = privkey.decrypt(
            #decode the b64 ciphertext
            base64.b64decode(ciphertext),
            padding.OAEP(
                mgf=padding.MGF1(hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        # print("saiu do decryptRSA sem erro")
        return plaintext    
    except Exception as e:
        print("saiu do decryptRSA com erro")
        print("erro: {}".format(e))
        return ""
    # k = RSA.importKey(key)
    # deb = base64.b64decode(text)
    # Cipher = PKCS1_OAEP.new(k)
    # # data = k.decrypt(deb)
    # data = Cipher.decrypt(deb)
    # return data

def signInfo(gwPvtKey, data,password=None):
    """ Sign some data with the peer's private key\n 
        @param gwPvtKey - peer's private key\n
        @param data - data to sign\n
        @return sinature - signature of the data maked with the private key
    """
    try:
        # print("\tantes de carregar a chave de assinatura!!")
        key = gwPvtKey.encode('utf-8')
        #load key
        privkey = serialization.load_pem_private_key(
            key,
            password
        )
        # print("\tchave carregada com sucesso!!")
        #sign the data
        #TODO prehashed
        sig = privkey.sign(
            data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        # print("\tassinado com sucesso!!")
        #encode the signature in b64
        signature = base64.b64encode(sig)
        # print("assinatura em b64: {}".format(signature))
        return signature
    except Exception as e:
        print("\tsaiu da assinatura RSA sem sucesso!!")
        print("error: {}".format(e))
        return ""
    # try:
    #     k = RSA.importKey(gwPvtKey)
    #     signer = PKCS1_v1_5.new(k)
    #     digest = SHA256.new()
    #     digest.update(data.encode('utf-8')) #added encode to support python 3 , need to evluate if it is still working
    #     #digest.update(data)
    #     s = signer.sign(digest)
    #     signature = base64.b64encode(s)
    #     return signature
    # except:
    #     return ""

def signVerify(data, signature, gwPubKey):
    """ Verify if a data sign by a private key it's unaltered\n
        @param data - data to be verified\n
        @param signature - signature of the data to be validated\n
        @param gwPubKey - peer's private key
    """
    # print("\tentrou no valida assinatura RSA!!")
    try:
        # print("\tantes de carregar a chave de verificacao RSA!!")
        key = gwPubKey.encode('utf-8')
        # print("key: {}".format(key))
        #load key
        pubkey = serialization.load_pem_public_key(
            key
        )
        # print("\tchave carregada com sucesso!!")
        #verify the signature
        #TODO prehashed
        pubkey.verify(
            #decode the b64 signature
            base64.b64decode(signature),
            data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        # print("\tassinatura valida!!")
        return True
    except Exception as e:
        print("\tsaiu da verificacao RSA sem sucesso!!")
        print("error: {}".format(e))
        return False
    # try:
    #     k = RSA.importKey(gwPubKey)
    #     signer = PKCS1_v1_5.new(k)
    #     digest = SHA256.new()
    #     digest.update(data.encode('utf-8')) #added encode to support python 3 , need to evluate if it is still working
    #     #digest.update(data)
    #     signaturerOr = base64.b64decode(signature)
    #     result = signer.verify(digest, signaturerOr)
    #     return result
    # except:
    #     return False

def generateRSAKeyPair():
    """ Generate a pair of RSA keys using RSA 3072\n
        @return pub, prv - public and private key
    """
    try:
        #print("entrou no generate RSA keys")
        keysize = 3072
        publicexpoent = 65537

        private = rsa.generate_private_key(
            publicexpoent,
            key_size=keysize
        )
        #print("gerou a chave privada")

        pubKey = private.public_key()

        #print("gerou a chave publica")
        
        prv = private.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        # print("serializou a chave privada: \n{}\nsize: {}".format(prv,len(prv)))
        pub = pubKey.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo    
        )
        # print("serializou a chave publica: \n{}\nsize: {}".format(pub,len(pub)))
        
        #print("saiu do generate RSA keys")
        return pub, prv
    except Exception as e:
        print("error: {}".format(e))
        return "",""

        # private = RSA.generate(3072)

        # pubKey = private.public_key()
        # prv = private.export_key()
        # pub = pubKey.export_key()
        # return pub, prv

# ECC

## ECDSA

def signInfoECDSA(gwPvtKey, data, password=None):
    """ Sign some data with the peer's private key\n 
        @param gwPvtKey - peer's private key\n
        @param data - data to sign\n
        @return sinature - signature of the data maked with the private key
    """
    # print("\tinside signInfoECDSA!!")
    # print("gwPvtKey: {} \ndata: {} \npassword: {}".format(gwPvtKey,data,password))
    try:
        #load key
        key = gwPvtKey.encode('utf-8')
        privatekey = serialization.load_pem_private_key(
            key,
            password
        )
        # print("successful loaded key!!")
        # sign the data
        # TODO prehashed
        sign = privatekey.sign(
            data,
            ec.ECDSA(hashes.SHA256())
        )
        # print("successful signed!!")
        # encode the signature in b64
        signatureb64 = base64.b64encode(sign)
        # print("signatureb64: {}".format(signatureb64))
        # print("\texited signInfoECDSA with success!!")
        return signatureb64
    except Exception as e:
        print("\texited signInfoECDSA without success!!")
        print("error: {}".format(e))
        return ""

def signVerifyECDSA(data, signature, gwPubKey):
    """ Verify if a data sign by a private key it's unaltered\n
        @param data - data to be verified\n
        @param signature - signature of the data to be validated\n
        @param gwPubKey - peer's private key
    """
    # print("\tinside signVerifyECDSA!!")
    # print("data: {} \nsignature: {} \ngwPubKey: {}".format(data,signature,gwPubKey))
    try:
        # load key
        key = gwPubKey.encode('utf-8')
        publickey = serialization.load_pem_public_key(
            key
        )
        # print("successful loaded key!!")
        # verify the signature
        # TODO prehashed
        publickey.verify(
            # decode the b64 signature
            base64.b64decode(signature),
            data,
            ec.ECDSA(hashes.SHA256())
        )
        # print("valid signature!!")
        # print("\texited signVerifyECDSA with success!!")
        return True
    except Exception as e:
        print("\texited signVerifyECDSA without success!!")
        print("error: {}".format(e))
        return False

def generateECDSAKeyPair():
    """ Generate a pair of ECDSA keys using SECP256R1\n
        @return pub, prv - public and private key
    """
    # print("\tinside generateECDSAKeyPair!!")
    try:
        privatekey = ec.generate_private_key(
            ec.SECP256R1
        )
        # print("private key generated")
        publickey = privatekey.public_key()
        # print("public key generated")
        
        prv = privatekey.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        # print("private key serialized: {}".format(prv))
        pub = publickey.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        # print("public key serialized: {}".format(pub))
        
        # print("\texited generateECDSAKeyPair with success!!")
        return pub, prv
    except Exception as e:
        print("\texited generateECDSAKeyPair without success!!")
        print("error: {}".format(e))
        return "",""

## ECDH

def generateSharedKey(myPrivatekey, otherPublicKey, password=None):
    """ Stabilish a new shared key between two parties\n
        @Param myPrivateKey - the private key of the part using this function\n
        @Param otherPublicKey - the public key of the part to share the key\n
        @Return sharedKey - the key shared between the parties
    """
    # print("\tinside generateSharedKey!!")
    # print("types:")
    # print("myprivatekey: {}".format(type(myPrivatekey)))
    # print("otherpublickey: {}".format(type(otherPublicKey)))
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
        # print("\tsuccesful loaded keys!!")
        # print("DHPrivKey: {} \nDHPubKey: {}".format(type(DHPrivKey),type(DHPubKey)))
        # print("")
        # print("myPrivatekey: \n{} \notherPublicKey: \n{}".format(myPrivatekey,otherPublicKey))
        sharedKey = DHPrivKey.exchange(ec.ECDH(),DHPubKey)
        # print("sharedKey: {}".format(type(sharedKey)))
        # print("\texited generateSharedKey with success!!")
        return sharedKey
    except Exception as e:
        print("\texited generateSharedKey without success!!")
        print("error: {}".format(e))
