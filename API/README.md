![SpeedyCHAIN](pages/assets/images/speedychain-logo.svg)

This is the source code for a blockchain prototype, designed to run on IoT devices.

It was wrote in Python 2.7.

Please, check your OS and its repositories to install python2.7, python2.7-dev, python-pip and pyro4

example for debain/ubuntu based OS: sudo apt install python2.7 python2.7-dev python-pip pyro4

Dependencies:
flask>=1.0.2
Pyro4>=4.76
pyCrypto>=2.6.1
merkle>=0.1.3
requests2>=2.16.0
ptvsd>=4.2.10
colorlog>=4.0.2


The key folder is just a bunch of random public and private keys created for tests purpose.

HOW-TO RUN INTERACTIVE MODE:
1. run a instance of Pyro nameserver (ex: python2 -m Pyro4.naming -n 127.0.0.1 -p 9090)
2. run n instances of Gateways (ex: python2 runner.py -n 127.0.0.1 -p 9090 -G gwa -C 0001 -S 100) -> gwa is the chosen name, 0001 is the default context that gateway is part of, 100 is the tx pool size
3. run the user interface (ex: python2 src/tools/DeviceSimulator.py 127.0.0.1 9090 gwa dev-a) -> dev-a is the chosen name
4. in the user interface choose your consensus algorithm (option 12 -> "PBFT")
4.1. run a batch of simulated devices (option 9 -> 100 -> 1000)  -> 100 devices and 1000 transactions per device

HOW TO RUN INTERCATIVE MODE EASILY (by script):
1. run the script SpeedyChainRunner_localhost (ex: sh SpeedyChainRunner_localhost)


HOW TO AUTO-RUN (SCRIPT/BACKGROUND) - used for experiments:
1. run the script auto_SpeedyChainRunner_localhost_script_noninteractive.sh (ex: SpeedyChainRunner_localhost_script_noninteractive.sh)



FOR SMART CONTRACTS ONLY
The Ethereum Virtual Machine (evm) use golang, installation instructions available on: https://golang.org/doc/install
To compile the EVM after installing the Golang

    - Run "go get github.com/ethereum/go-ethereum"
    - Access the EVM folder
    - Run "go build"

QUICK START:

    - Run the quickstart.sh
    If an EVM is necessary for testing, uncomment the EVM line in quickstart.sh script


TODO List:
- improve the REST methods
- change the info genesis block hash to point to the block header hash

Video tutorial setting up CORE emulator infrastructure (deprecated):
https://www.youtube.com/watch?v=xCGu3r73xl4

Video tutorial setting up SpeedyChain and using DeviceSimulator (deprecated):
https://www.youtube.com/watch?v=3MA8HBgbA8k
