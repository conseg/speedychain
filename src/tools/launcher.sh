#!/bin/bash
gnome-terminal -e "bash -c \"python StreamHandler.py 129.94.175.201 12666 R1 dev-a true; exec bash\""
sleep 1
gnome-terminal -e "bash -c \"python StreamHandler.py 129.94.175.201 12666 R2 dev-b true; exec bash\""
sleep 1
gnome-terminal -e "bash -c \"python StreamHandler.py 129.94.175.201 12666 R3 dev-c true; exec bash\""