#!/bin/bash
export PATH=$PATH:/usr/local/go/bin
echo $GOPATH /home/roben/go
gnome-terminal -e "bash -c \"python -m Pyro4.naming -n 10.58.208.181 -p 9090; exec bash\""
sleep 1
gnome-terminal -e "bash -c \"python ~/PycharmProjects/speedychain/runner.py  10.58.208.181 9090 gwa 0001; exec bash\""
sleep 1
gnome-terminal -e "bash -c \"python ~/PycharmProjects/speedychain/runner.py 10.58.208.181 9090 gwb 0001; exec bash\""
sleep 1
gnome-terminal -e "bash -c \"python ~/PycharmProjects/speedychain/src/tools/DeviceSimulator.py 10.58.208.181 9090 gwa dev-a; exec bash\""
