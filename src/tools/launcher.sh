#!/bin/bash
INSTANCES=2
for ((i=0; $i<$INSTANCES; i++))
do
	n=$(($i%4))
	echo $n
	python StreamHandler.py 129.94.175.201 12666 R$n dev-$i x > x$i.txt&
	sleep 1
done