#!/bin/bash
export PATH=$PATH:/usr/local/go/bin
echo $GOPATH /home/roben/go
gnome-terminal -e "bash -c \"python -m Pyro4.naming -n 127.0.0.1 -p 9090; exec bash\""
sleep 1
gnome-terminal -e "bash -c \"python ~/PycharmProjects/speedychain/API/runner.py 127.0.0.1 9090 gwa 0001; exec bash\""
sleep 1
gnome-terminal -e "bash -c \"python ~/PycharmProjects/speedychain/API/runner.py 127.0.0.1 9090 gwb 0001; exec bash\""
sleep 1
gnome-terminal -e "bash -c \"python ~/PycharmProjects/speedychain/API/runner.py 127.0.0.1 9090 gwc 0001; exec bash\""
sleep 1
gnome-terminal -e "bash -c \"python ~/PycharmProjects/speedychain/API/runner.py 127.0.0.1 9090 gwd 0001; exec bash\""
sleep 1
#gnome-terminal -e "bash -c \"python ~/speedychain_varruda/speedychain-master/src/tools/DeviceSimulator.py 127.0.0.1 9090 gwa dev-a     50   10 PoW; exec bash\""
gnome-terminal -e "bash -c \"python ~/PycharmProjects/speedychain/API/src/tools/DeviceSimulator.py 127.0.0.1 9090 gwa dev-a; exec bash\""
gnome-terminal -e "bash -c \"python ~/PycharmProjects/speedychain/API/src/tools/DeviceSimulator.py 127.0.0.1 9090 gwa dev-b; exec bash\""
gnome-terminal -e "bash -c \"python ~/PycharmProjects/speedychain/API/src/tools/DeviceSimulator.py 127.0.0.1 9090 gwb dev-c; exec bash\""
#gnome-terminal -e "bash -c \"~/PycharmProjects/speedychain/API/EVM/EVM; exec bash\""
#gnome-terminal -e "bash -c \"gedit ~/go/src/EVM/howto.txt; exec bash\""