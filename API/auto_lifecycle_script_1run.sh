#!/bin/bash
#export PATH=$PATH:/usr/local/go/bin
#echo $GOPATH /home/appendable/go

#pool size for PYRO => required when running many parallel instances
export PYRO_THREADPOOL_SIZE=100

numDev=5
numTr=5
contexts=0001
poolSize=100
port=9000
nsIP=127.0.0.1 #10.0.2.15
run=0
consensus=PBFT
txInterval=10000
mypathRunner=runner.py
mypathDevice=src/tools/DeviceSimulator.py
mode=lifecycleMulti
x=10
i=$numDev
j=$numTr
python2 -m Pyro4.naming -n $nsIP -p 9090 &
PIDPyroNS=$!
sleep 1
python2 $mypathRunner -n $nsIP -p 9090 -G gwa -C $contexts -S $poolSize &
PIDGwa=$!
sleep 1
python2 $mypathRunner -n $nsIP -p 9090 -G gwb -C $contexts -S $poolSize &
PIDGwb=$!
sleep 1
python2 $mypathRunner -n $nsIP -p 9090 -G gwc -C $contexts -S $poolSize &
PIDGwc=$!
sleep 1
python2 $mypathRunner -n $nsIP -p 9090 -G gwd -C $contexts -S $poolSize &
PIDGwd=$!
sleep 1
python2 $mypathRunner -n $nsIP -p 9090 -G gwe -C $contexts -S $poolSize &
PIDGwe=$!
sleep 1
python2 $mypathRunner -n $nsIP -p 9090 -G gwf -C $contexts -S $poolSize &
PIDGwf=$!
sleep 1
python2 $mypathRunner -n $nsIP -p 9090 -G gwg -C $contexts -S $poolSize &
PIDGwg=$!
sleep 1
python2 $mypathRunner -n $nsIP -p 9090 -G gwh -C $contexts -S $poolSize &
PIDGwh=$!
sleep 1
python2 $mypathRunner -n $nsIP -p 9090 -G gwi -C $contexts -S $poolSize &
PIDGwi=$!
sleep 1
python2 $mypathRunner -n $nsIP -p 9090 -G gwj -C $contexts -S $poolSize &
PIDGwj=$!
sleep 1

sleep 10
python2 $mypathDevice $nsIP 9090 gwa dev-a $numDev $numTr $consensus $contexts $txInterval $mode &
PIDDeva=$!
python2 $mypathDevice $nsIP 9090 gwb dev-b $numDev $numTr $consensus $contexts $txInterval $mode &
PIDDevb=$!
python2 $mypathDevice $nsIP 9090 gwc dev-c $numDev $numTr $consensus $contexts $txInterval $mode &
PIDDevc=$!
python2 $mypathDevice $nsIP 9090 gwd dev-d $numDev $numTr $consensus $contexts $txInterval $mode &
PIDDevd=$!
python2 $mypathDevice $nsIP 9090 gwe dev-e $numDev $numTr $consensus $contexts $txInterval $mode &
PIDDeve=$!
python2 $mypathDevice $nsIP 9090 gwf dev-f $numDev $numTr $consensus $contexts $txInterval $mode &
PIDDevf=$!
python2 $mypathDevice $nsIP 9090 gwg dev-g $numDev $numTr $consensus $contexts $txInterval $mode &
PIDDevg=$!
python2 $mypathDevice $nsIP 9090 gwh dev-h $numDev $numTr $consensus $contexts $txInterval $mode &
PIDDevh=$!
python2 $mypathDevice $nsIP 9090 gwi dev-i $numDev $numTr $consensus $contexts $txInterval $mode &
PIDDevi=$!
python2 $mypathDevice $nsIP 9090 gwj dev-j $numDev $numTr $consensus $contexts $txInterval $mode &
PIDDevj=$!

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
kill -9 $PIDPyroNS
kill -9 $PIDGwa
kill -9 $PIDGwb
kill -9 $PIDGwc
kill -9 $PIDGwd
kill -9 $PIDGwe
kill -9 $PIDGwf
kill -9 $PIDGwg
kill -9 $PIDGwh
kill -9 $PIDGwi
kill -9 $PIDGwj
folder="csv/"
numRun="repetion_"
numContexts="_contexts_"
numGw="_Gws_"
numDev="_devices_"
numTx="_Tx_"
timestamp=$(date +%F_%T)
t3=$"_T3.csv"
t5=$"_T5.csv"
t6=$"_T6.csv"
t20=$"_T20.csv"
t21=$"_T21.csv"
t22=$"_T22.csv"
t23=$"_T23.csv"
t24=$"_T24.csv"
t25=$"_T25.csv"
t26=$"_T26.csv"
t30=$"_T30.csv"
t31=$"_T31.csv"
ERROR=$"ERROR.csv"
more gw* | grep T3 >  $folder$numRun$run$numContexts$contexts$numGw$x$numDev$i$numTx$j$t3
more gw* | grep T5 >  $folder$numRun$run$numContexts$contexts$numGw$x$numDev$i$numTx$j$t5
more gw* | grep T6 >  $folder$numRun$run$numContexts$contexts$numGw$x$numDev$i$numTx$j$t6
more gw* | grep T20 > $folder$numRun$run$numContexts$contexts$numGw$x$numDev$i$numTx$j$t20
more gw* | grep T21 > $folder$numRun$run$numContexts$contexts$numGw$x$numDev$i$numTx$j$t21
more gw* | grep T22 > $folder$numRun$run$numContexts$contexts$numGw$x$numDev$i$numTx$j$t22
more gw* | grep T23 > $folder$numRun$run$numContexts$contexts$numGw$x$numDev$i$numTx$j$t23
more gw* | grep T24 > $folder$numRun$run$numContexts$contexts$numGw$x$numDev$i$numTx$j$t24
more gw* | grep T25 > $folder$numRun$run$numContexts$contexts$numGw$x$numDev$i$numTx$j$t25
more gw* | grep T26 > $folder$numRun$run$numContexts$contexts$numGw$x$numDev$i$numTx$j$t26
more dev* | grep T27 > $folder$numRun$run$numContexts$contexts$numGw$x$numDev$i$numTx$j$t27
more dev* | grep T30 > $folder$numRun$run$numContexts$contexts$numGw$x$numDev$i$numTx$j$t30
more dev* | grep T31 > $folder$numRun$run$numContexts$contexts$numGw$x$numDev$i$numTx$j$t31
more dev* | grep ERROR > $folder$numRun$run$numContexts$contexts$numGw$x$numDev$i$numTx$j$ERROR
#rm *.log*


#gnome-terminal -e "bash -c \"~/speedychain/API/EVM/EVM; exec bash\""
#gnome-terminal -e "bash -c \"gedit ~/go/src/EVM/howto.txt; exec bash\""
