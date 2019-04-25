---
layout: default
title: "Home"
---

# About SpeedyCHAIN

SpeedyCHAIN ​​is a blockchain prototype developed to support the CONSEG (Reliability and Systems Security Group of PPGCC / PUC-RS) researches.

It was wrote in Python 2.7.

# Structure

Dependencies:
- pyCrypto
- flask

The key folder is just a bunch of random public and private keys created for tests purpose.

# How to run SpeedyCHAIN

1. ajustar IP do arquivo P2P.py
2. sudo python3 P2P.py (erro [Errno 98] é normal)
3. sudo ./sendRequest.sh
4. opção 5, inserir ip
5. opção 7
6. opção 1
7. opção 2
8. opção 8 p/ listar as infos
9. repetir passos 6 e 7 de acordo com necessidade

## Videos

[Video tutorial setting up CORE emulator infrastructure](https://www.youtube.com/watch?v=xCGu3r73xl4)

[Video tutorial setting up SpeedyChain and using DeviceSimulator](https://www.youtube.com/watch?v=3MA8HBgbA8k)

# Todo list

- implement an consensus algorithm
- improve the REST methods
- auto-generate the keys (for test purpouses only)
- instrumentalize code and parametrize its time collect
- change the info genesis block hash to point to the block header hash
