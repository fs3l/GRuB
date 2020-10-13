#! /usr/bin/python3.6
import sys
sys.path.append("../")
import web3
from web3 import Web3
from lib.private_net import PrivateSmartContract
from lib.utils import partition_priceoracle 
from queue import Queue

##################
###### main ######
##################

if (len(sys.argv) < 3 ):
    print ("Usage: ./driver.py batch_size test_type (0: Loading, 1: Test) depth account_index(default=0)")
    exit()

batch_size = int(sys.argv[1])
test_type = int(sys.argv[2])
depth = int(sys.argv[3])
trace = sys.argv[4]
account_index = 0
if (len(sys.argv) == 6 ):
    account_index = int(sys.argv[5])

K = 1 
### intialization
SC = PrivateSmartContract(account_index)
batches = partition_priceoracle(trace)
print(len(batches))
history = Queue(maxsize = 3)

# markets of tokens
markets=[]
for i in range(batch_size):
    markets.append(i)
read_keys=0
write_indices=markets

### execution phase
# price of tokens
print("read:",read_keys)
root = '0xcf55e1dcf75e73ec3efb8c0535b465af6b154ff8ce9fd26de2c8c872b3e98909'
proof = ['0xcf55e1dcf75e73ec3efb8c0535b465af6b154ff8ce9fd26de2c8c872b3e98909']*depth
indices = list(range(1, depth+1)) 
print ('proof length:', len(proof), 'depth:', depth)

### test GRuB
Contract_Type = 'GRuB'

### Invoke OffChain_Rational
TXLogFile = 'log/TX_' + Contract_Type + '_depth_' + str(depth)
SC.get_contract_instance('./contracts/PriceOracle_GRuB.sol', TXLogFile)

if test_type == 2:
    SC.send_transactions(Contract_Type, 2, [0, values, 0, indices, proof, depth], range_size, 'OffChainRead_NR')

if test_type == 0:
    SC.send_transactions(Contract_Type, 0, [markets], batch_size, 'Load')

R_COUNTER=0
if test_type == 1:
    for batch in batches:
        if batch[0] == "R":
            read_values = [batch[1]]
            R_COUNTER+=1
            if R_COUNTER > K: 
                SC.send_transactions(Contract_Type, 3, [read_keys, [], False, [], [], depth], 1, 'OnChainRead_K'+str(K))
            elif R_COUNTER == K: 
                SC.send_transactions(Contract_Type, 3, [read_keys, read_values, True, indices, proof, depth], 1, 'OffChainRead_R_K'+str(K))
            else:
                SC.send_transactions(Contract_Type, 2, [read_keys, read_values, False, indices, proof, depth], 1, 'OffChainRead_NR_K'+str(K))
        elif batch[0] == "W":
            # report read_num to adaptive K
            SC.send_transactions(Contract_Type, 1, [[read_keys], root], batch_size, 'Write')
            R_COUNTER=0
