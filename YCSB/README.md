### Test YCSB trace
##### Deploy smart contracts
```
./deploy_contract.py contracts/Always_Replicate.sol
./deploy_contract.py contracts/Never_Replicate.sol
./deploy_contract.py contracts/Secure_DB.sol
```

##### Run baseline of Offchain data placement (BL1)
```
./driver_offchain.py ycsb_trace/workloada.Log 65535 10 1
``` 
The first parameter `ycsb_trace/workloadg.Log` is the testing trace, the second parameter `65535` is the `KV count` in the trace while the third parameter `10` is the `batch size`, you can use any other values other than 10. You can use other traces in the `ycsb_trace` folder.

This step may take long time due to heavy merkle-tree computation.

##### Run baseline of Onchain data placement (BL2)
```
./driver_onchain.py ycsb_trace/workloada.Log 65535 10 1
```

##### Run GRuB
```
./driver_grub.py ycsb_trace/workloada.Log 65535 10 1
```
