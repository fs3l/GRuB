#! /bin/bash

./deploy_sc.py contracts/memorizing/OffChain_Rational.sol 0 
./driver_memorizing.py log/workloade.Log 1000 240 0 0 8
./driver_memorizing.py log/workloade.Log 1000 240 1 0 8

./deploy_sc.py contracts/memorizing/OffChain_Rational.sol 0
./driver_memorizing.py log/workloade.Log 1000 240 0 0 16
./driver_memorizing.py log/workloade.Log 1000 240 1 0 16

./deploy_sc.py contracts/memorizing/OffChain_Rational.sol 0
./driver_memorizing.py log/workloade.Log 1000 240 0 0 32
./driver_memorizing.py log/workloade.Log 1000 240 1 0 32
