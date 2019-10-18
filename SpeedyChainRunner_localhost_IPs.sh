#!/bin/bash
export PATH=$PATH:/usr/local/go/bin
echo $GOPATH /home/roben/go
gnome-terminal -e "bash -c \"python -m Pyro4.naming -n 10.58.203.78 -p 9090; exec bash\""
sleep 1
gnome-terminal -e "bash -c \"python ~/PycharmProjects/speedychain/src/runner.py  10.58.203.78 9090 gwa; exec bash\""
sleep 1
gnome-terminal -e "bash -c \"python ~/PycharmProjects/speedychain/src/runner.py 10.58.203.78 9090 gwb; exec bash\""
sleep 1
gnome-terminal -e "bash -c \"python ~/PycharmProjects/speedychain/src/DeviceSimulator.py 10.58.203.78 9090 gwa dev-a; exec bash\""
