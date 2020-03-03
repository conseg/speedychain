![SpeedyCHAIN](pages/assets/images/speedychain-logo.svg)

This is the source code for a blockchain prototype, designed to run on IoT devices.

It was wrote in Python 2.7

Dependencies:
flask>=1.0.2
Pyro4>=4.76
pyCrypto>=2.6.1
merkle>=0.1.3
requests2>=2.16.0
ptvsd>=4.2.10
colorlog>=4.0.2


The key folder is just a bunch of random public and private keys created for tests purpose.

HOW-TO:
1. run a instance of Pyro nameserver (ex: python -m Pyro4.naming -n 127.0.0.1 -p 9090)
2. run n instances of Gateways (ex: python [PATH]/speedychain/runner.py 127.0.0.1 9090 gwa) -> gwa is the chosen name
3. run the user interface (ex: python [PATH]/speedychain/src/tools/DeviceSimulator.py 127.0.0.1 9090 gwa dev-a) -> dev-a is the chosen name
4. in the user interface choose your consensus algorithm (option 12 -> "PBFT")
4.1. run a bath of simulated devices (option 9 -> 100 -> 1000)  -> 100 devices and 1000 transactions per device


The Ethereum Virtual Machine (evm) use golang, installation instructions available on: https://golang.org/doc/install

To compile the EVM after installing the Golang

    - Run "go get github.com/ethereum/go-ethereum"
    - Access the EVM folder
    - Run "go build"

QUICK START:

    - Run the quickstart.sh
    If an EVM is necessary for testing, uncomment the EVM line in quickstart.sh script

SMART CONTRACTS automated:

"python src/tools/loader.py -ip localhost -port 9090 -gn gwa -file EVM/gpsTracker2.csv"

STREAMING FULL SETUP:
1. Setup virtual environment in the raspberry pi:

1.1. sudo pip install virtualenv

1.2. sudo pip install virtualenvwrapper

2. Add the following variables to the ~/.bashrc:
`
export WORKON_HOME=$HOME/.virtualenvs

export VIRTUALENVWRAPPER_VIRTUALENV=/usr/local/bin/virtualenv

source /usr/local/bin/virtualenvwrapper.sh

export VIRTUALENVWRAPPER_ENV_BIN_DIR=bin
`

Reload the bashrc: `source ~/.bashrc`

3. Create the virtual environment:

3.1. mkvirtualenv speedy

3.2 workon speedy

4. Get the last project verion:

`git clone https://github.com/conseg/speedychain.git

cd speedychain

git checkout streamMultilevel

cd src

pip install -r requirements.txt
`

5. Execution:

Node 1 (name server): pyro4-ns 192.168.0.2 -p 12345

Node 2 (gateway[s]): python runner.py 192.168.0.2 12345 Gw2

Node 3 (gateway[s]): python runner.py 192.168.0.2 12345 Gw3

...

Node 10 (streamings):

Individual execution:

python speedychain/src/tools/StreamHandler.py 192.168.0.2 12345 Gw2 dev-0

Multiple instances:

python speedychain/src/tools/launcher.sh




TODO List:
- improve the REST methods
- change the info genesis block hash to point to the block header hash

Video tutorial setting up CORE emulator infrastructure (deprecated):
https://www.youtube.com/watch?v=xCGu3r73xl4

Video tutorial setting up SpeedyChain and using DeviceSimulator (deprecated):
https://www.youtube.com/watch?v=3MA8HBgbA8k
