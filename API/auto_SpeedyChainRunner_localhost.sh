#!/bin/bash
#export PATH=$PATH:/usr/local/go/bin
#echo $GOPATH /home/roben/go
python -m Pyro4.naming -n 127.0.0.1 -p 9090 &
PIDPyroNS=$!
sleep 1
python ~/PycharmProjects/speedychain/API/runner.py -n 127.0.0.1 -p 9090 -G gwa -C 0001 &
PIDGwa=$!
sleep 1
python ~/PycharmProjects/speedychain/API/runner.py -n 127.0.0.1 -p 9090 -G gwb -C 0001 &
PIDGwb=$!
sleep 1
python ~/PycharmProjects/speedychain/API/runner.py -n 127.0.0.1 -p 9090 -G gwc -C 0001 &
PIDGwc=$!
sleep 1
python ~/PycharmProjects/speedychain/API/runner.py -n 127.0.0.1 -p 9090 -G gwd -C 0001 &
PIDGwd=$!
sleep 1
python ~/PycharmProjects/speedychain/API/runner.py -n 127.0.0.1 -p 9090 -G gwe -C 0001 &
PIDGwe=$!
sleep 1
#gnome-terminal -e "bash -c \"python ~/speedychain_varruda/speedychain-master/src/tools/DeviceSimulator.py 127.0.0.1 9090 gwa dev-a     50   10 PoW 1; exec bash\""
#for automated running devices calls should pass as arguments Pyro-NS IP PORT GatewayNameToConnect DeviceName numBlocks numTx blockConsensus numContexts
python ~/PycharmProjects/speedychain/API/src/tools/DeviceSimulator.py 127.0.0.1 9090 gwa dev-a 30 250 PBFT 4 &
PIDDeva=$!
python ~/PycharmProjects/speedychain/API/src/tools/DeviceSimulator.py 127.0.0.1 9090 gwb dev-b 30 250 PBFT 4 &
PIDDevb=$!
python ~/PycharmProjects/speedychain/API/src/tools/DeviceSimulator.py 127.0.0.1 9090 gwc dev-c 30 250 PBFT 4 &
PIDDevc=$!
python ~/PycharmProjects/speedychain/API/src/tools/DeviceSimulator.py 127.0.0.1 9090 gwd dev-d 30 250 PBFT 4 &
PIDDevd=$!
python ~/PycharmProjects/speedychain/API/src/tools/DeviceSimulator.py 127.0.0.1 9090 gwe dev-e 30 250 PBFT 4 &
PIDDeve=$!

wait $PIDDeva
wait $PIDDevb
wait $PIDDevc
wait $PIDDevd
wait $PIDDeve
kill -9 $PIDPyroNS
kill -9 $PIDGwa
kill -9 $PIDGwb
kill -9 $PIDGwc
kill -9 $PIDGwd
kill -9 $PIDGwe

#gnome-terminal -e "bash -c \"~/PycharmProjects/speedychain/API/EVM/EVM; exec bash\""
#gnome-terminal -e "bash -c \"gedit ~/go/src/EVM/howto.txt; exec bash\""