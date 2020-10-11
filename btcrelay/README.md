### Test BtcRelay trace
##### Deploy smart contracts
```
./deploy_contract.py contracts/grub.sol
./deploy_contract.py contracts/offchain.sol
./deploy_contract.py contracts/onchain.sol
```

##### Run baseline of Offchain data placement (BL1)
```
./driver_offchain.py 10 1 trace/subtrace_1.data
``` 
Parameter `10` is the `batch size`, you can use any other values other than 10.

This step may take long time due to heavy merkle-tree computation.

##### Run baseline of Onchain data placement (BL2)
```
./driver_onchain.py 10 1 trace/subtrace_1.data
```

##### Run GRuB
```
./driver_memoryless.py 10 1 trace/subtrace_1.data 0
```
