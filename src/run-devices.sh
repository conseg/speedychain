#!/bin/bash
# device-us-east-1 = ec2-34-207-193-122.compute-1.amazonaws.com = 172.31.87.123
# device-us-west-2 = ec2-52-36-138-0.us-west-2.compute.amazonaws.com = 172.31.29.215
# device-ap-northeast-1 = ec2-52-194-252-12.ap-northeast-1.compute.amazonaws.com = 172.31.36.63
python2.7 Device.py 50.16.193.245 9090 gateway-us-east-1 100 50 &
python2.7 Device.py 50.16.193.245 9090 gateway-us-west-2 100 50 &
python2.7 Device.py 50.16.193.245 9090 gateway-ap-northeast-1 100 50 &
python2.7 Device.py 50.16.193.245 9090 gateway-us-east-1 100 50 &
python2.7 Device.py 50.16.193.245 9090 gateway-us-west-2 100 50 &
python2.7 Device.py 50.16.193.245 9090 gateway-ap-northeast-1 100 50 &
