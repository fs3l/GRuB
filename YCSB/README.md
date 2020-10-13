### Test YCSB trace
##### Deploy smart contracts
```
./deploy_contract.py contracts/Always_Replicate.sol
./deploy_contract.py contracts/Motivation.sol
./deploy_contract.py contracts/Never_Replicate.sol
./deploy_contract.py contracts/OffChain_Irrational.sol
./deploy_contract.py contracts/OffChain_Rational.sol
./deploy_contract.py contracts/OnChain.sol
./deploy_contract.py contracts/Secure_DB.sol
```

##### Run baseline of Offchain data placement (BL1)
```
./driver_offchain.py ycsb_trace/workloadg.Log 10 10 1
``` 
The first parameter `10` is the `batch size` while the second parameter `10` is the `loading range`, you can use any other values other than 10. Parameter `ycsb_trace/workloadg.Log` is the `test data`, you can use any file in `ycsb_trace`.

This step may take long time due to heavy merkle-tree computation.

##### Run baseline of Onchain data placement (BL2)
```
./driver_onchain.py ycsb_trace/workloadg.Log 10 10 1
```

##### Run GRuB
```
./driver_memoryless.py ycsb_trace/workloadg.Log 10 10 1
```
