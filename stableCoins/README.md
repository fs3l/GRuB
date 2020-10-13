### Test StableCoin trace
##### Deploy smart contracts
```
./deploy_contract.py contracts/PriceOracle_Onchain.sol
./deploy_contract.py contracts/PriceOracle_Offchain.sol
./deploy_contract.py contracts/PriceOracle_GRuB.sol
```

##### Run baseline of Offchain data placement (BL1)
```
./driver_offchain.py 10 1 10 trace/ether_2018_0425_0430_RW.data
``` 
The first parameter `10` is the `batch size` while the second parameter `10` is the `Merkle Tree Depth`.

This step may take long time due to heavy merkle-tree computation.

##### Run baseline of Onchain data placement (BL2)
```
./driver_onchain.py 10 1 trace/ether_2018_0425_0430_RW.data
```

##### Run GRuB
```
./driver_grub.py 10 1 10 trace/ether_2018_0425_0430_RW.data
```
