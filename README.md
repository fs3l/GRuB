# Gas-­efficient State Replication on Blockchain with Workload Awareness

## Preparition
### Install dependencies
```
sudo pip3 install web3
sudo pip3 install py-solc
```

## Test macrobenmark
Make sure your Ethereum client (geth) is running and RPC is enabled.
```
cd macro
```
### Deploy smart contract
```
./deploy_smart_contract.py your_source_code(xxx.sol) 
```

### Drive YCSB workload
```
./driver_memoryless.py log/workloade.log 16384 240 0 0 2
./driver_memoryless.py log/workloade.log 16384 240 1 0 2
``` 

## Trouble-shooting
Sometimes the latest solc compiler(0.5.0+) maybe not compatible with web3.py, try the following:

```
python3.6 -m solc.install v0.4.25
sudo cp ~/.py-solc/solc-v0.4.25/bin/solc /usr/bin/solc
```
