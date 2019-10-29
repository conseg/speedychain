#!/bin/bash
gnome-terminal -e "bash -c \"python -m Pyro4.naming -n 127.0.0.1 -p 9090; exec bash\""
sleep 1
gnome-terminal -e "bash -c \"python runner.py 127.0.0.1 9090 gwa; exec bash\""
sleep 1
gnome-terminal -e "bash -c \"python runner.py 127.0.0.1 9090 gwb; exec bash\""
sleep 1
gnome-terminal -e "bash -c \"python runner.py 127.0.0.1 9090 gwc; exec bash\""
sleep 1
gnome-terminal -e "bash -c \"python runner.py 127.0.0.1 9090 gwd; exec bash\""
sleep 1

gnome-terminal -e "bash -c \"python src/tools/DeviceSimulator.py 127.0.0.1 9090 gwa dev-a; exec bash\""
gnome-terminal -e "bash -c \"./EVM/EVM; exec bash\""
