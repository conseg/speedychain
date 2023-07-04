![SpeedyCHAIN](API/pages/assets/images/speedychain-logo.svg)

This is the source code for a blockchain prototype, designed to run on IoT devices.

For more details about how to use it and proper appendable-block blockchain code, please access the API folder.

Dependencies (all available with pip install):
- pyCrypto
- flask
- requests
- merklee
- pyro4

The Ethereum Virtual Machine (evm) use golang, installation instructions available on:
https://golang.org/doc/install

To compile the EVM after installing the Golang
- Run "go get github.com/ethereum/go-ethereum"
- Access the EVM folder
- Run "go build"


QUICK START:
- Run the quickstart.sh
- If an EVM is necessary for testing, uncomment the EVM line in quickstart.sh script


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

The key folder is just a bunch of random public and private keys created for tests purpose.

Video tutorial setting up CORE emulator infrastructure:
https://www.youtube.com/watch?v=xCGu3r73xl4

Video tutorial setting up SpeedyChain and using DeviceSimulator (deprecated):
https://www.youtube.com/watch?v=3MA8HBgbA8k
