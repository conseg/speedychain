#!/bin/bash
#export PATH=$PATH:/usr/local/go/bin
#echo $GOPATH /home
export PYRO_THREADPOOL_SIZE=1000
numDev=35
numTr=200
contexts=0004
sizePool=15
nsIP=127.0.0.1
txInterval=10000
python -m Pyro4.naming -n $nsIP -p 9090 &
PIDPyroNS=$!
sleep 1
python runner.py -n $nsIP -p 9090 -G gwa -C $contexts -S $sizePool &
PIDGwa=$!
sleep 1
python runner.py -n $nsIP -p 9090 -G gwb -C $contexts -S $sizePool &
PIDGwb=$!
sleep 1
python runner.py -n $nsIP -p 9090 -G gwc -C $contexts -S $sizePool &
PIDGwc=$!
sleep 1
python runner.py -n $nsIP -p 9090 -G gwd -C $contexts -S $sizePool &
PIDGwd=$!
sleep 1
python runner.py -n $nsIP -p 9090 -G gwe -C $contexts -S $sizePool &
PIDGwe=$!
sleep 1
#gnome-terminal -e "bash -c \"python ~/speedychain_varruda/speedychain-master/src/tools/DeviceSimulator.py $nsIP 9090 gwa dev-a     50   10 PoW 1; exec bash\""
#for automated running devices calls should pass as arguments Pyro-NS_IP PORT GatewayNameToConnect DeviceName numBlocks numTx blockConsensus numContexts
python src/tools/DeviceSimulator.py $nsIP 9090 gwa dev-a $numDev $numTr PBFT $contexts $txInterval &
PIDDeva=$!
python src/tools/DeviceSimulator.py $nsIP 9090 gwb dev-b $numDev $numTr PBFT $contexts $txInterval &
PIDDevb=$!
python src/tools/DeviceSimulator.py $nsIP 9090 gwc dev-c $numDev $numTr PBFT $contexts $txInterval &
PIDDevc=$!
python src/tools/DeviceSimulator.py $nsIP 9090 gwd dev-d $numDev $numTr PBFT $contexts $txInterval &
PIDDevd=$!
python src/tools/DeviceSimulator.py $nsIP 9090 gwe dev-e $numDev $numTr PBFT $contexts $txInterval &
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

$folder="csv/"
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
more gw* | grep T20 > $folder$timestamp$t20
more gw* | grep T21 > $folder$timestamp$t21
more gw* | grep T22 > $folder$timestamp$t22
more gw* | grep T23 > $folder$timestamp$t23
more gw* | grep T24 > $folder$timestamp$t24
more gw* | grep T25 > $folder$timestamp$t25
more gw* | grep T26 > $folder$timestamp$t26
more dev* | grep T30 > $folder$timestamp$t30
more dev* | grep T31 > $folder$timestamp$t31
rm *.log*


#gnome-terminal -e "bash -c \"~/PycharmProjects/speedychain/API/EVM/EVM; exec bash\""
#gnome-terminal -e "bash -c \"gedit ~/go/src/EVM/howto.txt; exec bash\""