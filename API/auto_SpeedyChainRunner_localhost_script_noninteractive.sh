#!/bin/bash
#export PATH=$PATH:/usr/local/go/bin
#echo $GOPATH /home/appendable/go

#pool size for PYRO => required when running many parallel instances
export PYRO_THREADPOOL_SIZE=100

numDev=100
numTr=100
contexts=0001
poolSize=100
nsIP=127.0.0.1 #10.0.2.15
run=0
consensus=PBFT
txInterval=10000
mypathRunner=runner.py
mypathDevice=src/tools/DeviceSimulator.py

for c in {1..1}
do
  for run in {1..1}
  do
    for x in {10..10.1}
    do
      #10 15 and 40 devices, for gives increment of 10
      for i in {10..10..10}
      do
      #  100,20,30 and 1000 transactions per device
        for j in {100..100..100}
        do
          if [ $j -eq 10 ] || [ $j -eq 100 ] || [ $j -eq 500 ] || [ $j -eq 1000 ]
          then
            contexts=$c
            numDev=$i
            numTr=$j
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
#            if [ $x -eq 5 ]
#            then
#              python $mypathRunner -n $nsIP -p 9090 -G gwe -C $contexts -S $poolSize &
#              PIDGwe=$!
#              sleep 1
#            fi
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
            #python2 $mypathRunner -n $nsIP -p 9090 -G gwk -C $contexts -S $poolSize &
            #PIDGwk=$!
            #sleep 1
            #python $mypathRunner -n $nsIP -p 9090 -G gwl -C $contexts -S $poolSize &
            #PIDGwl=$!
            #sleep 1
            #python $mypathRunner -n $nsIP -p 9090 -G gwm -C $contexts -S $poolSize &
            #PIDGwm=$!
            #sleep 1
            #python $mypathRunner -n $nsIP -p 9090 -G gwn -C $contexts -S $poolSize &
            #PIDGwn=$!
            #sleep 1
            #python $mypathRunner -n $nsIP -p 9090 -G gwo -C $contexts -S $poolSize &
            #PIDGwo=$!

            sleep 10
            #gnome-terminal -e "bash -c \"python ~/speedychain_varruda/speedychain-master/src/tools/DeviceSimulator.py $nsIP 9090 gwa dev-a     50   10 PoW 1; exec bash\""
            #for automated running devices calls should pass as arguments Pyro-NS_IP PORT GatewayNameToConnect DeviceName numBlocks numTx blockConsensus numContexts
            python2 $mypathDevice $nsIP 9090 gwa dev-a $numDev $numTr $consensus $contexts $txInterval &
            PIDDeva=$!
            python2 $mypathDevice $nsIP 9090 gwb dev-b $numDev $numTr $consensus $contexts $txInterval &
            PIDDevb=$!
            python2 $mypathDevice $nsIP 9090 gwc dev-c $numDev $numTr $consensus $contexts $txInterval &
            PIDDevc=$!
            python2 $mypathDevice $nsIP 9090 gwd dev-d $numDev $numTr $consensus $contexts $txInterval &
            PIDDevd=$!
#            if [ $x -eq 5 ]
#            then
#              python $mypathDevice $nsIP 9090 gwe dev-e $numDev $numTr $consensus $contexts $txInterval &
#              PIDDeve=$!
#            fi
            python2 $mypathDevice $nsIP 9090 gwe dev-e $numDev $numTr $consensus $contexts $txInterval &
            PIDDeve=$!
            python2 $mypathDevice $nsIP 9090 gwf dev-f $numDev $numTr $consensus $contexts $txInterval &
            PIDDevf=$!
            python2 $mypathDevice $nsIP 9090 gwg dev-g $numDev $numTr $consensus $contexts $txInterval &
            PIDDevg=$!
            python2 $mypathDevice $nsIP 9090 gwh dev-h $numDev $numTr $consensus $contexts $txInterval &
            PIDDevh=$!
            python2 $mypathDevice $nsIP 9090 gwi dev-i $numDev $numTr $consensus $contexts $txInterval &
            PIDDevi=$!
            python2 $mypathDevice $nsIP 9090 gwj dev-j $numDev $numTr $consensus $contexts $txInterval &
            PIDDevj=$!
            #python2 $mypathDevice $nsIP 9090 gwk dev-k $numDev $numTr $consensus $contexts $txInterval &
            #PIDDevk=$!
            #python $mypathDevice $nsIP 9090 gwl dev-l $numDev $numTr $consensus $contexts $txInterval &
            #PIDDevl=$!
            #python $mypathDevice $nsIP 9090 gwm dev-m $numDev $numTr $consensus $contexts $txInterval &
            #PIDDevm=$!
            #python $mypathDevice $nsIP 9090 gwn dev-n $numDev $numTr $consensus $contexts $txInterval &
            #PIDDevn=$!
            #python $mypathDevice $nsIP 9090 gwo dev-o $numDev $numTr $consensus $contexts &
            #PIDDevo=$!

            wait $PIDDeva
            wait $PIDDevb
            wait $PIDDevc
            wait $PIDDevd
#            if [ $x -eq 5 ]
#            then
#              wait $PIDDeve
#            fi
            wait $PIDDeve
            wait $PIDDevf
            wait $PIDDevg
            wait $PIDDevh
            wait $PIDDevi
            wait $PIDDevj
            #wait $PIDDevk
            #wait $PIDDevl
            #wait $PIDDevm
            #wait $PIDDevdn
            #wait $PIDDevo
            kill -9 $PIDPyroNS
            kill -9 $PIDGwa
            kill -9 $PIDGwb
            kill -9 $PIDGwc
            kill -9 $PIDGwd
#            if [ $x -eq 5 ]
#            then
#              kill -9 $PIDGwe
#            fi
            kill -9 $PIDGwe
            kill -9 $PIDGwf
            kill -9 $PIDGwg
            kill -9 $PIDGwh
            kill -9 $PIDGwi
            kill -9 $PIDGwj
            #kill -9 $PIDGwk
            #kill -9 $PIDGwl
            #kill -9 $PIDGwm
            #kill -9 $PIDGwn
            #kill -9 $PIDGwo
            folder="csv/"
            numRun="repetion_"
            numContexts="_contexts_"
            numGw="_Gws_"
            numDev="_devices_"
            numTx="_Tx_"
            timestamp=$(date +%F_%T)
            t3=$"T3.csv"
            t5=$"T5.csv"
            t6=$"T6.csv"
            t20=$"T20.csv"
            t21=$"T21.csv"
            t22=$"T22.csv"
            t23=$"T23.csv"
            t24=$"T24.csv"
            t25=$"T25.csv"
            t26=$"T26.csv"
            t27=$"T27.csv"
            t30=$"T30.csv"
            t31=$"T31.csv"
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
          fi
        done
      done
    done
  done
done


#gnome-terminal -e "bash -c \"~/speedychain/API/EVM/EVM; exec bash\""
#gnome-terminal -e "bash -c \"gedit ~/go/src/EVM/howto.txt; exec bash\""
