# Gas-­efficient State Replication on Blockchain with Workload Awareness

## Preparition
### Install dependencies
```
sudo pip3 install web3
sudo pip3 install py-solc
```

## Test macrobenmark
### Deploy smart contract
```
cd macro
./deploy_smart_contract.py your_source_code(xxx.sol) 
```

### Drive YCSB workload
```
./driver_memoryless.py log/workloade.log 16384 240 0 0 2
./driver_memoryless.py log/workloade.log 16384 240 1 0 2
``` 
