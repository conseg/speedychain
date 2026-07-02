numDev=100
numTr=100
contexts=0001
poolSize=100
port=9000
nsIP=127.0.0.1 #10.0.2.15
run=0
consensus=PBFT
txInterval=10000
mypathRunner=runner.py
mypathDevice=src/tools/DeviceSimulator.py

#!/bin/bash
python2 -m Pyro4.naming -n $nsIP -p 9090 &
PIDPyroNS=$!
sleep 1
python2 $mypathRunner -n $nsIP -p 9090 -G gwa -C $contexts -S $poolSize &
PIDGwa=$!
sleep 1
python2 $mypathRunner -n $nsIP -p 9090 -G gwb -C $contexts -S $poolSize &
PIDGwb=$!
sleep 1
sleep 10
python2 $mypathDevice $nsIP 9090 gwa dev-a $numDev $numTr $consensus $contexts $txInterval &
PIDDeva=$!


wait $PIDDeva
kill -9 $PIDPyroNS
kill -9 $PIDGwa
kill -9 $PIDGwb

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