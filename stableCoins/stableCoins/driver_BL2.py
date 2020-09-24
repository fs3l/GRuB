#! /usr/bin/python3.6
import sys
import web3
from web3 import Web3
sys.path.append("../")
from lib.private_net import PrivateSmartContract
from lib.utils import partition_priceoracle

##################
###### main ######
##################

if (len(sys.argv) < 4 ):
    print ("Usage: ./driver.py batch_size test_type (0: Loading, 1: Test) merkle_tree_depth account_index (default=0)")
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
print("read:",read_keys)
read_values = [12458125000000000000]
root = '0xcf55e1dcf75e73ec3efb8c0535b465af6b154ff8ce9fd26de2c8c872b3e98909'
proof = ['0xcf55e1dcf75e73ec3efb8c0535b465af6b154ff8ce9fd26de2c8c872b3e98909']*depth
indices = list(range(1,depth+1))
print ('proof length:', len(proof), 'depth:', depth)

### test GRuB
Contract_Type = 'StableCoin'
TXLogFile = 'log/TX_' + Contract_Type + '_Never_Replicate_' + str(depth)
SC.get_contract_instance('./contracts/StableCoin_BL2.sol', TXLogFile)

if test_type == 0:
    SC.send_transactions(Contract_Type, 0, [write_indices], batch_size, 'Load')

if test_type == 1:
    for batch in batches:
        if batch[0] == "R":
            SC.send_transactions(Contract_Type, 2, [read_keys, read_values, indices, proof, depth], 1, 'Deposit')
        elif batch[0] == "W":
            SC.send_transactions(Contract_Type, 1, [root], batch_size, 'Poke')
