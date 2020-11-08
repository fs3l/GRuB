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
```
cd btcrelay/
```
Then follow the README.md in btcrelay folder

### Test YCSB trace (start a new terminal)
```
cd YCSB/
```
Then follow the README.md in YCSB folder

### Test YCSB trace (start a new terminal)
```
cd stableCoins/
```
Then follow the README.md in stableCoins folder

### Trouble-shooting
##### If you have multiple python3 versions, use the following commands to install Web3 and pysolc packages
```
python3.6 -m pip install web3
python3.6 -m pip install py-solc
```
##### If it prompts you that /usr/bin/solc is not executable, add execution permission by the following command
```
sudo chmod +x /usr/bin/solc
```

Reference
---

If you use our dataset, please reference our paper published in Middleware 2020

```
@inproceedings{grub,
 author    = {Kai Li and Yuzhe Tang and Jiaqi Chen and Zhehu Yuan and Cheng Xu and Jianliang Xu},
 title     = {Cost-Effective Data Feeds to Blockchains via Workload-Adaptive Data Replication},
 booktitle = {ACM/IFIP Middleware 2020},
 howpublished = {\url{https://arxiv.org/abs/1911.04078}}
}
```


