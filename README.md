## GRuB: Cost-Effective Data Feeds to Blockchains via Workload-Adaptive Data Replication

### Preparation
##### Download Virtual Box and mirror from following address, and setup virtual ubuntu environment.
https://www.virtualbox.org/wiki/Downloads

http://mirrors.aliyun.com/ubuntu-releases/18.04.5/ubuntu-18.04.5-desktop-amd64.iso

##### Install Python3, Web3 and pysolc
```
sudo apt-get install python3.6
sudo apt-get install python3-pip
sudo pip3 install web3
sudo pip3 install py-solc
```

##### Install Geth
```
sudo apt-get install software-properties-common
sudo add-apt-repository -y ppa:ethereum/ethereum
sudo apt-get update
sudo apt-get install ethereum
```
##### Run your private ethereum node (Don't close this process, start another process to do BtcRelay test)
```
geth --datadir "geth_data" init genesis.json
geth --datadir "geth_data" --rpc --allow-insecure-unlock --mine --minerthreads 1 --unlock "0x71ad2477b729741951b652aa7f9825e2f91f5a65" --password <(echo -n "") console 2>log
```

### Test BtcRelay trace
##### Deploy smart contracts
```
cd btcrelay
./deploy_contract.py contract/grub.sol
./deploy_contract.py contract/offchain.sol
./deploy_contract.py contract/onchain.sol
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

### Trouble-shooting
##### Sometimes the latest solc compiler(0.5.0+) maybe not compatible with web3.py, try the following:
```
python3.6 -m solc.install v0.4.25
sudo cp ~/.py-solc/solc-v0.4.25/bin/solc /usr/bin/solc
```

##### If you have multiple python3 versions, use the following commands to install Web3 and pysolc packages
```
python3.6 -m pip install web3
python3.6 -m pip install py-solc
```
