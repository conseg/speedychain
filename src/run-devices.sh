#!/bin/bash

# sudo su
# cd /app/src
# ps -aux | grep python

# device-us-east-1 = ec2-34-207-193-122.compute-1.amazonaws.com = 172.31.87.123
# python2.7 Device.py 50.16.193.245 9090 gateway-us-east-1 10 10

# device-us-west-2 = ec2-52-36-138-0.us-west-2.compute.amazonaws.com = 172.31.29.215
# python2.7 Device.py 50.16.193.245 9090 gateway-us-west-2 10 10

# device-ap-northeast-1 = ec2-52-194-252-12.ap-northeast-1.compute.amazonaws.com = 172.31.36.63
# python2.7 Device.py 50.16.193.245 9090 gateway-ap-northeast-1 10 10

# No name-server:
pyro4-ns -n 0.0.0.0 -p 9090 &
pyro4-nsc -n 0.0.0.0 -p 9090 list

# gateway-us-east-1
python Gateway.py 54.91.146.246 9090 gateway-us-east-1 &
# gateway-us-west-2
python Gateway.py 54.91.146.246 9090 gateway-us-west-2 &
# gateway-us-east-1
python Gateway.py 54.91.146.246 9090 gateway-ap-northeast-1 &
# gateway-us-east-1
python Gateway.py 54.91.146.246 9090 gateway-sa-east-1 &

# No device:
# Testing connectivity:
python Device.py 54.91.146.246 9090 gateway-us-east-1      device-us-east-1     5   5 PoW
python Device.py 54.91.146.246 9090 gateway-us-west-2      device-us-east-1     5   5 PoW
python Device.py 54.91.146.246 9090 gateway-ap-northeast-1 device-us-east-1     5   5 PoW
python Device.py 54.91.146.246 9090 gateway-sa-east-1      device-us-east-1     5   5 PoW
# Clean S3
aws s3 rm s3://speedychain --recursive

# PoW

# 50 devices

# No gateway:
truncate -s 0 /var/log/gateway*.log

# No device:
python Device.py 54.91.146.246 9090 gateway-us-east-1      device-us-east-1     50   10 PoW &
python Device.py 54.91.146.246 9090 gateway-us-west-2      device-us-east-1     50   10 PoW &
python Device.py 54.91.146.246 9090 gateway-ap-northeast-1 device-us-east-1     50   10 PoW &
python Device.py 54.91.146.246 9090 gateway-sa-east-1      device-us-east-1     50   10 PoW &

# No gateway:
aws s3 cp /var/log/gateway*.log s3://speedychain/log/PoW/50-devices/10-transactions/
truncate -s 0 /var/log/gateway*.log

# No device:
python Device.py 54.91.146.246 9090 gateway-us-east-1      device-us-east-1     50  100 PoW &
python Device.py 54.91.146.246 9090 gateway-us-west-2      device-us-east-1     50  100 PoW &
python Device.py 54.91.146.246 9090 gateway-ap-northeast-1 device-us-east-1     50  100 PoW &
python Device.py 54.91.146.246 9090 gateway-sa-east-1      device-us-east-1     50  100 PoW &

# No gateway:
aws s3 cp /var/log/gateway*.log s3://speedychain/log/PoW/50-devices/100-transactions/
truncate -s 0 /var/log/gateway*.log

# No device:
python Device.py 54.91.146.246 9090 gateway-us-east-1      device-us-east-1     50 1000 PoW &
python Device.py 54.91.146.246 9090 gateway-us-west-2      device-us-east-1     50 1000 PoW &
python Device.py 54.91.146.246 9090 gateway-ap-northeast-1 device-us-east-1     50 1000 PoW &
python Device.py 54.91.146.246 9090 gateway-sa-east-1      device-us-east-1     50 1000 PoW &

# No gateway:
aws s3 cp /var/log/gateway*.log s3://speedychain/log/PoW/50-devices/1000-transactions/
truncate -s 0 /var/log/gateway*.log

# 100 devices

# No gateway:
truncate -s 0 /var/log/gateway*.log

# No device:
python Device.py 54.91.146.246 9090 gateway-us-east-1      device-us-east-1    100   10 PoW &
python Device.py 54.91.146.246 9090 gateway-us-west-2      device-us-east-1    100   10 PoW &
python Device.py 54.91.146.246 9090 gateway-ap-northeast-1 device-us-east-1    100   10 PoW &
python Device.py 54.91.146.246 9090 gateway-sa-east-1      device-us-east-1    100   10 PoW &

# No gateway:
aws s3 cp /var/log/gateway*.log s3://speedychain/log/PoW/100-devices/10-transactions/
truncate -s 0 /var/log/gateway*.log

# No device:
python Device.py 54.91.146.246 9090 gateway-us-east-1      device-us-east-1    100  100 PoW &
python Device.py 54.91.146.246 9090 gateway-us-west-2      device-us-east-1    100  100 PoW &
python Device.py 54.91.146.246 9090 gateway-ap-northeast-1 device-us-east-1    100  100 PoW &
python Device.py 54.91.146.246 9090 gateway-sa-east-1      device-us-east-1    100  100 PoW &

# No gateway:
aws s3 cp /var/log/gateway*.log s3://speedychain/log/PoW/100-devices/100-transactions/
truncate -s 0 /var/log/gateway*.log

# No device:
python Device.py 54.91.146.246 9090 gateway-us-east-1      device-us-east-1    100 1000 PoW &
python Device.py 54.91.146.246 9090 gateway-us-west-2      device-us-east-1    100 1000 PoW &
python Device.py 54.91.146.246 9090 gateway-ap-northeast-1 device-us-east-1    100 1000 PoW &
python Device.py 54.91.146.246 9090 gateway-sa-east-1      device-us-east-1    100 1000 PoW &

# No gateway:
aws s3 cp /var/log/gateway*.log s3://speedychain/log/PoW/100-devices/1000-transactions/
truncate -s 0 /var/log/gateway*.log

# 650 devices

# No gateway:
truncate -s 0 /var/log/gateway*.log

# No device:
python Device.py 54.91.146.246 9090 gateway-us-east-1      device-us-east-1    650   10 PoW &
python Device.py 54.91.146.246 9090 gateway-us-west-2      device-us-east-1    650   10 PoW &
python Device.py 54.91.146.246 9090 gateway-ap-northeast-1 device-us-east-1    650   10 PoW &
python Device.py 54.91.146.246 9090 gateway-sa-east-1      device-us-east-1    650   10 PoW &
     
# No gateway:
aws s3 cp /var/log/gateway*.log s3://speedychain/log/PoW/100-devices/1000-transactions/
truncate -s 0 /var/log/gateway*.log

# No device:
python Device.py 54.91.146.246 9090 gateway-us-east-1      device-us-east-1    650  100 PoW &
python Device.py 54.91.146.246 9090 gateway-us-west-2      device-us-east-1    650  100 PoW &
python Device.py 54.91.146.246 9090 gateway-ap-northeast-1 device-us-east-1    650  100 PoW &
python Device.py 54.91.146.246 9090 gateway-sa-east-1      device-us-east-1    650  100 PoW &
     
# No gateway:
aws s3 cp /var/log/gateway*.log s3://speedychain/log/PoW/650-devices/100-transactions/
truncate -s 0 /var/log/gateway*.log

# No device:
python Device.py 54.91.146.246 9090 gateway-us-east-1      device-us-east-1    650 1000 PoW &
python Device.py 54.91.146.246 9090 gateway-us-west-2      device-us-east-1    650 1000 PoW &
python Device.py 54.91.146.246 9090 gateway-ap-northeast-1 device-us-east-1    650 1000 PoW &
python Device.py 54.91.146.246 9090 gateway-sa-east-1      device-us-east-1    650 1000 PoW &
     
# No gateway:
aws s3 cp /var/log/gateway*.log s3://speedychain/log/PoW/650-devices/1000-transactions/
truncate -s 0 /var/log/gateway*.log

# dBFT

# 50 devices

# No gateway:
truncate -s 0 /var/log/gateway*.log

# No device:
python Device.py 54.91.146.246 9090 gateway-us-east-1      device-us-east-1     50   10 dBFT &
python Device.py 54.91.146.246 9090 gateway-us-west-2      device-us-east-1     50   10 dBFT &
python Device.py 54.91.146.246 9090 gateway-ap-northeast-1 device-us-east-1     50   10 dBFT &
python Device.py 54.91.146.246 9090 gateway-sa-east-1      device-us-east-1     50   10 dBFT &

# No gateway:
aws s3 cp /var/log/gateway*.log s3://speedychain/log/dBFT/50-devices/10-transactions/
truncate -s 0 /var/log/gateway*.log

# No device:
python Device.py 54.91.146.246 9090 gateway-us-east-1      device-us-east-1     50  100 dBFT &
python Device.py 54.91.146.246 9090 gateway-us-west-2      device-us-east-1     50  100 dBFT &
python Device.py 54.91.146.246 9090 gateway-ap-northeast-1 device-us-east-1     50  100 dBFT &
python Device.py 54.91.146.246 9090 gateway-sa-east-1      device-us-east-1     50  100 dBFT &

# No gateway:
aws s3 cp /var/log/gateway*.log s3://speedychain/log/dBFT/50-devices/100-transactions/
truncate -s 0 /var/log/gateway*.log

# No device:
python Device.py 54.91.146.246 9090 gateway-us-east-1      device-us-east-1     50 1000 dBFT &
python Device.py 54.91.146.246 9090 gateway-us-west-2      device-us-east-1     50 1000 dBFT &
python Device.py 54.91.146.246 9090 gateway-ap-northeast-1 device-us-east-1     50 1000 dBFT &
python Device.py 54.91.146.246 9090 gateway-sa-east-1      device-us-east-1     50 1000 dBFT &

# No gateway:
aws s3 cp /var/log/gateway*.log s3://speedychain/log/dBFT/50-devices/1000-transactions/
truncate -s 0 /var/log/gateway*.log

# 100 devices

# No gateway:
truncate -s 0 /var/log/gateway*.log

# No device:
python Device.py 54.91.146.246 9090 gateway-us-east-1      device-us-east-1    100   10 dBFT &
python Device.py 54.91.146.246 9090 gateway-us-west-2      device-us-east-1    100   10 dBFT &
python Device.py 54.91.146.246 9090 gateway-ap-northeast-1 device-us-east-1    100   10 dBFT &
python Device.py 54.91.146.246 9090 gateway-sa-east-1      device-us-east-1    100   10 dBFT &

# No gateway:
aws s3 cp /var/log/gateway*.log s3://speedychain/log/dBFT/100-devices/10-transactions/
truncate -s 0 /var/log/gateway*.log

# No device:
python Device.py 54.91.146.246 9090 gateway-us-east-1      device-us-east-1    100  100 dBFT &
python Device.py 54.91.146.246 9090 gateway-us-west-2      device-us-east-1    100  100 dBFT &
python Device.py 54.91.146.246 9090 gateway-ap-northeast-1 device-us-east-1    100  100 dBFT &
python Device.py 54.91.146.246 9090 gateway-sa-east-1      device-us-east-1    100  100 dBFT &

# No gateway:
aws s3 cp /var/log/gateway*.log s3://speedychain/log/dBFT/100-devices/100-transactions/
truncate -s 0 /var/log/gateway*.log

# No device:
python Device.py 54.91.146.246 9090 gateway-us-east-1      device-us-east-1    100 1000 dBFT &
python Device.py 54.91.146.246 9090 gateway-us-west-2      device-us-east-1    100 1000 dBFT &
python Device.py 54.91.146.246 9090 gateway-ap-northeast-1 device-us-east-1    100 1000 dBFT &
python Device.py 54.91.146.246 9090 gateway-sa-east-1      device-us-east-1    100 1000 dBFT &

# No gateway:
aws s3 cp /var/log/gateway*.log s3://speedychain/log/dBFT/100-devices/1000-transactions/
truncate -s 0 /var/log/gateway*.log

# 650 devices

# No gateway:
truncate -s 0 /var/log/gateway*.log

# No device:
python Device.py 54.91.146.246 9090 gateway-us-east-1      device-us-east-1    650   10 dBFT &
python Device.py 54.91.146.246 9090 gateway-us-west-2      device-us-east-1    650   10 dBFT &
python Device.py 54.91.146.246 9090 gateway-ap-northeast-1 device-us-east-1    650   10 dBFT &
python Device.py 54.91.146.246 9090 gateway-sa-east-1      device-us-east-1    650   10 dBFT &
     
# No gateway:
aws s3 cp /var/log/gateway*.log s3://speedychain/log/dBFT/100-devices/1000-transactions/
truncate -s 0 /var/log/gateway*.log

# No device:
python Device.py 54.91.146.246 9090 gateway-us-east-1      device-us-east-1    650  100 dBFT &
python Device.py 54.91.146.246 9090 gateway-us-west-2      device-us-east-1    650  100 dBFT &
python Device.py 54.91.146.246 9090 gateway-ap-northeast-1 device-us-east-1    650  100 dBFT &
python Device.py 54.91.146.246 9090 gateway-sa-east-1      device-us-east-1    650  100 dBFT &
     
# No gateway:
aws s3 cp /var/log/gateway*.log s3://speedychain/log/dBFT/650-devices/100-transactions/
truncate -s 0 /var/log/gateway*.log

# No device:
python Device.py 54.91.146.246 9090 gateway-us-east-1      device-us-east-1    650 1000 dBFT &
python Device.py 54.91.146.246 9090 gateway-us-west-2      device-us-east-1    650 1000 dBFT &
python Device.py 54.91.146.246 9090 gateway-ap-northeast-1 device-us-east-1    650 1000 dBFT &
python Device.py 54.91.146.246 9090 gateway-sa-east-1      device-us-east-1    650 1000 dBFT &
     
# No gateway:
aws s3 cp /var/log/gateway*.log s3://speedychain/log/dBFT/650-devices/1000-transactions/
truncate -s 0 /var/log/gateway*.log

# PBFT

# 50 devices

# No gateway:
truncate -s 0 /var/log/gateway*.log

# No device:
python Device.py 54.91.146.246 9090 gateway-us-east-1      device-us-east-1     50   10 PBFT &
python Device.py 54.91.146.246 9090 gateway-us-west-2      device-us-east-1     50   10 PBFT &
python Device.py 54.91.146.246 9090 gateway-ap-northeast-1 device-us-east-1     50   10 PBFT &
python Device.py 54.91.146.246 9090 gateway-sa-east-1      device-us-east-1     50   10 PBFT &

# No gateway:
aws s3 cp /var/log/gateway*.log s3://speedychain/log/PBFT/50-devices/10-transactions/
truncate -s 0 /var/log/gateway*.log

# No device:
python Device.py 54.91.146.246 9090 gateway-us-east-1      device-us-east-1     50  100 PBFT &
python Device.py 54.91.146.246 9090 gateway-us-west-2      device-us-east-1     50  100 PBFT &
python Device.py 54.91.146.246 9090 gateway-ap-northeast-1 device-us-east-1     50  100 PBFT &
python Device.py 54.91.146.246 9090 gateway-sa-east-1      device-us-east-1     50  100 PBFT &

# No gateway:
aws s3 cp /var/log/gateway*.log s3://speedychain/log/PBFT/50-devices/100-transactions/
truncate -s 0 /var/log/gateway*.log

# No device:
python Device.py 54.91.146.246 9090 gateway-us-east-1      device-us-east-1     50 1000 PBFT &
python Device.py 54.91.146.246 9090 gateway-us-west-2      device-us-east-1     50 1000 PBFT &
python Device.py 54.91.146.246 9090 gateway-ap-northeast-1 device-us-east-1     50 1000 PBFT &
python Device.py 54.91.146.246 9090 gateway-sa-east-1      device-us-east-1     50 1000 PBFT &

# No gateway:
aws s3 cp /var/log/gateway*.log s3://speedychain/log/PBFT/50-devices/1000-transactions/
truncate -s 0 /var/log/gateway*.log

# 100 devices

# No gateway:
truncate -s 0 /var/log/gateway*.log

# No device:
python Device.py 54.91.146.246 9090 gateway-us-east-1      device-us-east-1    100   10 PBFT &
python Device.py 54.91.146.246 9090 gateway-us-west-2      device-us-east-1    100   10 PBFT &
python Device.py 54.91.146.246 9090 gateway-ap-northeast-1 device-us-east-1    100   10 PBFT &
python Device.py 54.91.146.246 9090 gateway-sa-east-1      device-us-east-1    100   10 PBFT &

# No gateway:
aws s3 cp /var/log/gateway*.log s3://speedychain/log/PBFT/100-devices/10-transactions/
truncate -s 0 /var/log/gateway*.log

# No device:
python Device.py 54.91.146.246 9090 gateway-us-east-1      device-us-east-1    100  100 PBFT &
python Device.py 54.91.146.246 9090 gateway-us-west-2      device-us-east-1    100  100 PBFT &
python Device.py 54.91.146.246 9090 gateway-ap-northeast-1 device-us-east-1    100  100 PBFT &
python Device.py 54.91.146.246 9090 gateway-sa-east-1      device-us-east-1    100  100 PBFT &

# No gateway:
aws s3 cp /var/log/gateway*.log s3://speedychain/log/PBFT/100-devices/100-transactions/
truncate -s 0 /var/log/gateway*.log

# No device:
python Device.py 54.91.146.246 9090 gateway-us-east-1      device-us-east-1    100 1000 PBFT &
python Device.py 54.91.146.246 9090 gateway-us-west-2      device-us-east-1    100 1000 PBFT &
python Device.py 54.91.146.246 9090 gateway-ap-northeast-1 device-us-east-1    100 1000 PBFT &
python Device.py 54.91.146.246 9090 gateway-sa-east-1      device-us-east-1    100 1000 PBFT &

# No gateway:
aws s3 cp /var/log/gateway*.log s3://speedychain/log/PBFT/100-devices/1000-transactions/
truncate -s 0 /var/log/gateway*.log

# 650 devices

# No gateway:
truncate -s 0 /var/log/gateway*.log

# No device:
python Device.py 54.91.146.246 9090 gateway-us-east-1      device-us-east-1    650   10 PBFT &
python Device.py 54.91.146.246 9090 gateway-us-west-2      device-us-east-1    650   10 PBFT &
python Device.py 54.91.146.246 9090 gateway-ap-northeast-1 device-us-east-1    650   10 PBFT &
python Device.py 54.91.146.246 9090 gateway-sa-east-1      device-us-east-1    650   10 PBFT &
     
# No gateway:
aws s3 cp /var/log/gateway*.log s3://speedychain/log/PBFT/100-devices/1000-transactions/
truncate -s 0 /var/log/gateway*.log

# No device:
python Device.py 54.91.146.246 9090 gateway-us-east-1      device-us-east-1    650  100 PBFT &
python Device.py 54.91.146.246 9090 gateway-us-west-2      device-us-east-1    650  100 PBFT &
python Device.py 54.91.146.246 9090 gateway-ap-northeast-1 device-us-east-1    650  100 PBFT &
python Device.py 54.91.146.246 9090 gateway-sa-east-1      device-us-east-1    650  100 PBFT &
     
# No gateway:
aws s3 cp /var/log/gateway*.log s3://speedychain/log/PBFT/650-devices/100-transactions/
truncate -s 0 /var/log/gateway*.log

# No device:
python Device.py 54.91.146.246 9090 gateway-us-east-1      device-us-east-1    650 1000 PBFT &
python Device.py 54.91.146.246 9090 gateway-us-west-2      device-us-east-1    650 1000 PBFT &
python Device.py 54.91.146.246 9090 gateway-ap-northeast-1 device-us-east-1    650 1000 PBFT &
python Device.py 54.91.146.246 9090 gateway-sa-east-1      device-us-east-1    650 1000 PBFT &
     
# No gateway:
aws s3 cp /var/log/gateway*.log s3://speedychain/log/PBFT/650-devices/1000-transactions/
truncate -s 0 /var/log/gateway*.log



