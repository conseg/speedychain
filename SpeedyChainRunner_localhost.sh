#!/bin/bash

read -p "Enter Pyro and Gateway IP: " ip
read -p "Enter Pyro and Gateway Port: " port


export PATH=$PATH:/usr/local/go/bin
echo $GOPATH /home/roben/go
gnome-terminal -e "bash -c \"python -m Pyro4.naming -n $ip -p $port; exec bash\""
sleep 1

read -p "How Many Gateways?: " numG

for (( c=1; c<=numG; c++ ))
do
  read -p "Enter Gateway name: " gName
  gnome-terminal -e "bash -c \"python ~/PycharmProjects/speedychain/API/runner.py -n $ip -p $port -G $gName -C 0001; exec bash\""
  sleep 1
done

read -p "How Many Devices?: " numD
for (( c=1; c<=numD; c++ ))
do
  read -p "Enter Device name: " dName
  read -p "Enter Gateway name to connect: " gName
  gnome-terminal -e "bash -c \"python ~/PycharmProjects/speedychain/runDevice.py -n $ip -p $port -G $gName -D $dName; exec bash\""
  sleep 1
done

gnome-terminal -e "bash -c \"~/PycharmProjects/speedychain/API/EVM/EVM; exec bash\""
gnome-terminal -e "bash -c \"gedit ~/go/src/EVM/howto.txt; exec bash\""
#sleep 1
#gnome-terminal -e "bash -c \"python ~/PycharmProjects/speedychain/runDevice.py $ip $port; exec bash\""


