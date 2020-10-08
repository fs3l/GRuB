## GRuB: Cost-Effective Data Feeds to Blockchains via Workload-Adaptive Data Replication

### Preparation
##### Download Virtual Box and Ubuntu 18.04 ISO using the following link, and setup a virtual ubuntu environment.
https://www.virtualbox.org/wiki/Downloads

http://mirrors.aliyun.com/ubuntu-releases/18.04.5/ubuntu-18.04.5-desktop-amd64.iso

##### Install Python3, Web3 and pysolc
```
sudo apt-get install python3.6
sudo apt-get install python3-pip
sudo pip3 install web3
sudo pip3 install py-solc
sudo pip3 install sha3
python3.6 -m solc.install v0.4.25
sudo cp ~/.py-solc/solc-v0.4.25/bin/solc /usr/bin/solc
```

##### Install Geth
```
sudo apt-get install software-properties-common
sudo add-apt-repository -y ppa:ethereum/ethereum
sudo apt-get update
sudo apt-get install ethereum
```

##### Download GRuB
```
sudo apt-get install git
git clone https://github.com/syracuse-fullstacksecurity/GRuB.git
cd GRuB
```

##### Run your private ethereum node (do not close this terminal)
```
geth --datadir "geth_data" init genesis.json
geth --datadir "geth_data" --rpc --allow-insecure-unlock --mine --minerthreads 1 --unlock "0x71ad2477b729741951b652aa7f9825e2f91f5a65" --password <(echo -n "") console 2>log
```

### Test BtcRelay trace (start a new terminal)
##### Deploy smart contracts
```
cd GRuB/btcrelay
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

### Trouble-shooting
##### If you have multiple python3 versions, use the following commands to install Web3 and pysolc packages
```
python3.6 -m pip install web3
python3.6 -m pip install py-solc
```
##### If it aware you that need /usr/bin/solc to be executable, use following commands
```
sudo chmod +x /usr/bin/solc
```
