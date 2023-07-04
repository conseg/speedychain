#!/bin/bash
#export PATH=$PATH:/usr/local/go/bin
#echo $GOPATH /home/roben/go

#pool size for PYRO => required when running many parallel instances
export PYRO_THREADPOOL_SIZE=1000

numDev=15
numTr=200
contexts=0010
sizePool=5
nsIP=192.168.3.2
consensus=PBFT
#python -m Pyro4.naming -n $nsIP -p 9090 &
#PIDPyroNS=$!
#sleep 1
#python ~/PycharmProjects/speedychain/API/runner.py -n $nsIP -p 9090 -G gwa -C $contexts -S $sizePool &
#PIDGwa=$!
#sleep 1
#python ~/PycharmProjects/speedychain/API/runner.py -n $nsIP -p 9090 -G gwb -C $contexts -S $sizePool &
#PIDGwb=$!
#sleep 1
#python ~/PycharmProjects/speedychain/API/runner.py -n $nsIP -p 9090 -G gwc -C $contexts -S $sizePool &
#PIDGwc=$!
#sleep 1
#python ~/PycharmProjects/speedychain/API/runner.py -n $nsIP -p 9090 -G gwd -C $contexts -S $sizePool &
#PIDGwd=$!
#sleep 1
#python ~/PycharmProjects/speedychain/API/runner.py -n $nsIP -p 9090 -G gwe -C $contexts -S $sizePool &
#PIDGwe=$!
#sleep 1
#python ~/PycharmProjects/speedychain/API/runner.py -n $nsIP -p 9090 -G gwf -C $contexts -S $sizePool &
#PIDGwf=$!
#sleep 1
#python ~/PycharmProjects/speedychain/API/runner.py -n $nsIP -p 9090 -G gwg -C $contexts -S $sizePool &
#PIDGwg=$!
#sleep 1
#python ~/PycharmProjects/speedychain/API/runner.py -n $nsIP -p 9090 -G gwh -C $contexts -S $sizePool &
#PIDGwh=$!
#sleep 1
#python ~/PycharmProjects/speedychain/API/runner.py -n $nsIP -p 9090 -G gwi -C $contexts -S $sizePool &
#PIDGwi=$!
#sleep 1
#python ~/PycharmProjects/speedychain/API/runner.py -n $nsIP -p 9090 -G gwj -C $contexts -S $sizePool &
#PIDGwj=$!
#sleep 1
#python ~/PycharmProjects/speedychain/API/runner.py -n $nsIP -p 9090 -G gwk -C $contexts -S $sizePool &
#PIDGwk=$!
#sleep 1
#python ~/PycharmProjects/speedychain/API/runner.py -n $nsIP -p 9090 -G gwl -C $contexts -S $sizePool &
#PIDGwl=$!
#sleep 1
#python ~/PycharmProjects/speedychain/API/runner.py -n $nsIP -p 9090 -G gwm -C $contexts -S $sizePool &
#PIDGwm=$!
#sleep 1
#python ~/PycharmProjects/speedychain/API/runner.py -n $nsIP -p 9090 -G gwn -C $contexts -S $sizePool &
#PIDGwn=$!
#sleep 1
#python ~/PycharmProjects/speedychain/API/runner.py -n $nsIP -p 9090 -G gwo -C $contexts -S $sizePool &
#PIDGwo=$!

#sleep 600
#gnome-terminal -e "bash -c \"python ~/PycharmProjects/speedychain_varruda/speedychain-master/src/tools/DeviceSimulator.py $nsIP 9090 gwa dev-a     50   10 PoW 1; exec bash\""
#for automated running devices calls should pass as arguments Pyro-NS_IP PORT GatewayNameToConnect DeviceName numBlocks numTx blockConsensus numContexts
python ~/PycharmProjects/speedychain/API/src/tools/DeviceSimulator.py $nsIP 9090 gwa dev-a $numDev $numTr $consensus $contexts &
PIDDeva=$!
python ~/PycharmProjects/speedychain/API/src/tools/DeviceSimulator.py $nsIP 9090 gwb dev-b $numDev $numTr $consensus $contexts &
PIDDevb=$!
python ~/PycharmProjects/speedychain/API/src/tools/DeviceSimulator.py $nsIP 9090 gwc dev-c $numDev $numTr $consensus $contexts &
PIDDevc=$!
python ~/PycharmProjects/speedychain/API/src/tools/DeviceSimulator.py $nsIP 9090 gwd dev-d $numDev $numTr $consensus $contexts &
PIDDevd=$!
python ~/PycharmProjects/speedychain/API/src/tools/DeviceSimulator.py $nsIP 9090 gwe dev-e $numDev $numTr $consensus $contexts &
PIDDeve=$!
python ~/PycharmProjects/speedychain/API/src/tools/DeviceSimulator.py $nsIP 9090 gwf dev-f $numDev $numTr $consensus $contexts &
PIDDevf=$!
python ~/PycharmProjects/speedychain/API/src/tools/DeviceSimulator.py $nsIP 9090 gwg dev-g $numDev $numTr $consensus $contexts &
PIDDevg=$!
python ~/PycharmProjects/speedychain/API/src/tools/DeviceSimulator.py $nsIP 9090 gwh dev-h $numDev $numTr $consensus $contexts &
PIDDevh=$!
python ~/PycharmProjects/speedychain/API/src/tools/DeviceSimulator.py $nsIP 9090 gwi dev-i $numDev $numTr $consensus $contexts &
PIDDevi=$!
python ~/PycharmProjects/speedychain/API/src/tools/DeviceSimulator.py $nsIP 9090 gwj dev-j $numDev $numTr $consensus $contexts &
#PIDDevj=$!
#python ~/PycharmProjects/speedychain/API/src/tools/DeviceSimulator.py $nsIP 9090 gwk dev-k $numDev $numTr $consensus $contexts &
#PIDDevk=$!
#python ~/PycharmProjects/speedychain/API/src/tools/DeviceSimulator.py $nsIP 9090 gwl dev-l $numDev $numTr $consensus $contexts &
#PIDDevl=$!
#python ~/PycharmProjects/speedychain/API/src/tools/DeviceSimulator.py $nsIP 9090 gwm dev-m $numDev $numTr $consensus $contexts &
#PIDDevm=$!
#python ~/PycharmProjects/speedychain/API/src/tools/DeviceSimulator.py $nsIP 9090 gwn dev-n $numDev $numTr $consensus $contexts &
#PIDDevn=$!
#python ~/PycharmProjects/speedychain/API/src/tools/DeviceSimulator.py $nsIP 9090 gwo dev-o $numDev $numTr $consensus $contexts &
#PIDDevo=$!

wait $PIDDeva
wait $PIDDevb
wait $PIDDevc
wait $PIDDevd
wait $PIDDeve
wait $PIDDevf
wait $PIDDevg
wait $PIDDevh
wait $PIDDevi
wait $PIDDevj
wait $PIDDevk
wait $PIDDevl
wait $PIDDevm
wait $PIDDevdn
wait $PIDDevo
#kill -9 $PIDPyroNS
#kill -9 $PIDGwa
#kill -9 $PIDGwb
#kill -9 $PIDGwc
#kill -9 $PIDGwd
#kill -9 $PIDGwe
#kill -9 $PIDGwf
#kill -9 $PIDGwg
#kill -9 $PIDGwh
#kill -9 $PIDGwi
#kill -9 $PIDGwj
#kill -9 $PIDGwk
#kill -9 $PIDGwl
#kill -9 $PIDGwm
#kill -9 $PIDGwn
#kill -9 $PIDGwo

timestamp=$(date +%F_%T)
t5=$"T5.csv"
t6=$"T6.csv"
t20=$"T20.csv"
t21=$"T21.csv"
t22=$"T22.csv"
t23=$"T23.csv"
t24=$"T24.csv"
t25=$"T25.csv"
t26=$"T26.csv"
t30=$"T30.csv"
t31=$"T31.csv"
ERROR=$"ERROR.csv"
more gw* | grep T5 > $timestamp$t5
more gw* | grep T6 > $timestamp$t6
more gw* | grep T20 > $timestamp$t20
more gw* | grep T21 > $timestamp$t21
more gw* | grep T22 > $timestamp$t22
more gw* | grep T23 > $timestamp$t23
more gw* | grep T24 > $timestamp$t24
more gw* | grep T25 > $timestamp$t25
more gw* | grep T26 > $timestamp$t26
more dev* | grep T30 > $timestamp$t30
more dev* | grep T31 > $timestamp$t31
more dev* | grep ERROR > $timestamp$ERROR
rm *.log*


#gnome-terminal -e "bash -c \"speedychain/API/EVM/EVM; exec bash\""
#gnome-terminal -e "bash -c \"gedit ~/go/src/EVM/howto.txt; exec bash\""