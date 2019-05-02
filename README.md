![SpeedyCHAIN](pages/assets/images/speedychain-logo.svg)

This is the source code for a blockchain prototype, designed to run on IoT devices.

It was wrote in Python 2.7

Dependencies:
- pyCrypto
- flask

The key folder is just a bunch of random public and private keys created for tests purpose.

HOW-TO:
1. ajustar ip do arquivo P2P.py
2. sudo python3 P2P.py (erro [Errno 98] é normal)
3. sudo ./sendRequest.sh
4. opção 5, inserir ip
5. opção 7
6. opção 1
7. opção 2
8. opção 8 p/ listar as infos
9. repetir passos 6 e 7 de acordo com necessidade

TODO List:
- implement an consensus algorithm
- improve the REST methods
- auto-generate the keys (for test purpouses only)
- instrumentalize code and parametrize its time collect
- change the info genesis block hash to point to the block header hash

Video tutorial setting up CORE emulator infrastructure:
https://www.youtube.com/watch?v=xCGu3r73xl4

Video tutorial setting up SpeedyChain and using DeviceSimulator:
https://www.youtube.com/watch?v=3MA8HBgbA8k
