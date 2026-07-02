#!/bin/bash
gnome-terminal -e "bash -c \"python -m Pyro4.naming -n 127.0.0.1 -p 9090; exec bash\""
sleep 1
gnome-terminal -e "bash -c \"python runner.py -n 127.0.0.1 -p 9090 gwa -C 0001 -S 1; exec bash\""
sleep 1
gnome-terminal -e "bash -c \"python runner.py -n 127.0.0.1 -p 9090 gwb -C 0001 -S 1; exec bash\""
sleep 1
gnome-terminal -e "bash -c \"python runner.py -n 127.0.0.1 -p 9090 gwc -C 0001 -S 1; exec bash\""
sleep 1
gnome-terminal -e "bash -c \"python runner.py -n 127.0.0.1 -p 9090 gwd -C 0001 -S 1; exec bash\""
sleep 1

gnome-terminal -e "bash -c \"python src/tools/DeviceSimulator.py 127.0.0.1 9090 gwa dev-a; exec bash\""
gnome-terminal -e "bash -c \"./EVM/EVM; exec bash\""
