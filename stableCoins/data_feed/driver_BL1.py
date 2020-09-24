#! /usr/bin/python3.6
import sys
sys.path.append("../")
import web3
from web3 import Web3
from lib.private_net import PrivateSmartContract
from lib.utils import partition_priceoracle

##################
###### main ######
##################

if (len(sys.argv) < 4 ):
    print ("Usage: ./driver.py batch_size  test_type (0: Load, 1: Test) proof_size account_index(default=0)")
    exit()

batch_size = int(sys.argv[1])
test_type = int(sys.argv[2])
depth = int(sys.argv[3])
trace = sys.argv[4]
account_index = 0
if (len(sys.argv) == 6 ):
    account_index = int(sys.argv[5])

### intialization
SC = PrivateSmartContract(account_index)
batches = partition_priceoracle(trace) 
print(len(batches))

# markets of tokens
markets=[]
for i in range(batch_size):
    markets.append(i)
read_keys=0
write_indices=markets

# price of tokens
values = [12458125000000000000]*batch_size
print("read:",read_keys)

# Run baseline 1
Contract_Type = 'GRuB'
TXLogFile =  'log/TX_' + Contract_Type + '_Always_Replicate_ProofSize_' + str(depth)
SC.get_contract_instance('../contracts/PriceFeed_BL1.sol', TXLogFile)

if test_type == 0:
    SC.send_transactions(Contract_Type, 0, [write_indices], batch_size, 'Load')

if test_type == 1:
    for batch in batches:
        if batch[0] == "R":
            SC.send_transactions(Contract_Type, 3, [read_keys], 1, 'OnChainRead')
        elif batch[0] == "W":
            values=[batch[1]]*batch_size
            SC.send_transactions(Contract_Type, 1, [write_indices, values], batch_size, 'Write')
