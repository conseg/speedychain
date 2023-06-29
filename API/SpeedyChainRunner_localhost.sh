#!/bin/bash
#export PATH=$PATH:/usr/local/go/bin
#echo $GOPATH /home/roben/go
gnome-terminal --tab  -e "bash -c \"python -m Pyro4.naming -n 127.0.0.1 -p 9090; exec bash\""
sleep 1
gnome-terminal --tab  -e "bash -c \"python runner.py -n 127.0.0.1 -p 9090 -G gwa -C 0001 -S 1; exec bash\""
sleep 1
gnome-terminal --tab  -e "bash -c \"python runner.py -n 127.0.0.1 -p 9090 -G gwb -C 0001 -S 1; exec bash\""
sleep 1
gnome-terminal --tab  -e "bash -c \"python runner.py -n 127.0.0.1 -p 9090 -G gwc -C 0001 -S 1; exec bash\""
sleep 1
gnome-terminal --tab  -e "bash -c \"python runner.py -n 127.0.0.1 -p 9090 -G gwd -C 0001 -S 1; exec bash\""
sleep 1
gnome-terminal --tab  -e "bash -c \"python runner.py -n 127.0.0.1 -p 9090 -G gwe -C 0001 -S 1; exec bash\""
sleep 1
#gnome-terminal -e "bash -c \"python ~/speedychain_varruda/speedychain-master/src/tools/DeviceSimulator.py 127.0.0.1 9090 gwa dev-a     50   10 PoW; exec bash\""
gnome-terminal -e "bash -c \"python src/tools/DeviceSimulator.py 127.0.0.1 9090 gwa dev-a; exec bash\""
gnome-terminal --tab  -e "bash -c \"python src/tools/DeviceSimulator.py 127.0.0.1 9090 gwb dev-b; exec bash\""
gnome-terminal --tab  -e "bash -c \"python src/tools/DeviceSimulator.py 127.0.0.1 9090 gwc dev-c; exec bash\""
gnome-terminal --tab  -e "bash -c \"python src/tools/DeviceSimulator.py 127.0.0.1 9090 gwd dev-d; exec bash\""
gnome-terminal --tab  -e "bash -c \"python src/tools/DeviceSimulator.py 127.0.0.1 9090 gwe dev-e; exec bash\""

#gnome-terminal -e "bash -c \"~/PycharmProjects/speedychain/API/EVM/EVM; exec bash\""
#gnome-terminal -e "bash -c \"gedit ~/go/src/EVM/howto.txt; exec bash\""