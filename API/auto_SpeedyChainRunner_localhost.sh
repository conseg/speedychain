#!/bin/bash
#export PATH=$PATH:/usr/local/go/bin
#echo $GOPATH /home
export PYRO_THREADPOOL_SIZE=1000
numDev=35
numTr=200
contexts=0004
sizePool=15
python -m Pyro4.naming -n 127.0.0.1 -p 9090 &
PIDPyroNS=$!
sleep 1
python ~/PycharmProjects/speedychain/API/runner.py -n 127.0.0.1 -p 9090 -G gwa -C $contexts -S $sizePool &
PIDGwa=$!
sleep 1
python ~/PycharmProjects/speedychain/API/runner.py -n 127.0.0.1 -p 9090 -G gwb -C $contexts -S $sizePool &
PIDGwb=$!
sleep 1
python ~/PycharmProjects/speedychain/API/runner.py -n 127.0.0.1 -p 9090 -G gwc -C $contexts -S $sizePool &
PIDGwc=$!
sleep 1
python ~/PycharmProjects/speedychain/API/runner.py -n 127.0.0.1 -p 9090 -G gwd -C $contexts -S $sizePool &
PIDGwd=$!
sleep 1
python ~/PycharmProjects/speedychain/API/runner.py -n 127.0.0.1 -p 9090 -G gwe -C $contexts -S $sizePool &
PIDGwe=$!
sleep 1
#gnome-terminal -e "bash -c \"python ~/speedychain_varruda/speedychain-master/src/tools/DeviceSimulator.py 127.0.0.1 9090 gwa dev-a     50   10 PoW 1; exec bash\""
#for automated running devices calls should pass as arguments Pyro-NS_IP PORT GatewayNameToConnect DeviceName numBlocks numTx blockConsensus numContexts
python ~/PycharmProjects/speedychain/API/src/tools/DeviceSimulator.py 127.0.0.1 9090 gwa dev-a $numDev $numTr PBFT $contexts &
PIDDeva=$!
python ~/PycharmProjects/speedychain/API/src/tools/DeviceSimulator.py 127.0.0.1 9090 gwb dev-b $numDev $numTr PBFT $contexts &
PIDDevb=$!
python ~/PycharmProjects/speedychain/API/src/tools/DeviceSimulator.py 127.0.0.1 9090 gwc dev-c $numDev $numTr PBFT $contexts &
PIDDevc=$!
python ~/PycharmProjects/speedychain/API/src/tools/DeviceSimulator.py 127.0.0.1 9090 gwd dev-d $numDev $numTr PBFT $contexts &
PIDDevd=$!
python ~/PycharmProjects/speedychain/API/src/tools/DeviceSimulator.py 127.0.0.1 9090 gwe dev-e $numDev $numTr PBFT $contexts &
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

timestamp=$(date +%F_%T)
t20=$"T20.csv"
t21=$"T21.csv"
t22=$"T22.csv"
t23=$"T23.csv"
t24=$"T24.csv"
t25=$"T25.csv"
t26=$"T26.csv"
t30=$"T30.csv"
t31=$"T31.csv"
more gw* | grep T20 > $timestamp$t20
more gw* | grep T21 > $timestamp$t21
more gw* | grep T22 > $timestamp$t22
more gw* | grep T23 > $timestamp$t23
more gw* | grep T24 > $timestamp$t24
more gw* | grep T25 > $timestamp$t25
more gw* | grep T26 > $timestamp$t26
more dev* | grep T30 > $timestamp$t30
more dev* | grep T31 > $timestamp$t31
rm *.log*


#gnome-terminal -e "bash -c \"~/PycharmProjects/speedychain/API/EVM/EVM; exec bash\""
#gnome-terminal -e "bash -c \"gedit ~/go/src/EVM/howto.txt; exec bash\""