#! /usr/bin/python3.6
import sys
import pickle

from lib.merkle_multi_queries import getRoot, getProof, getDepth, update_tree
from lib.testnet_smart_contract import PublicSmartContract
from lib.local_smart_contract import PrivateSmartContract

##################
###### main ######
##################

if (len(sys.argv) < 3 ):
    print ("Usage: ./driver.py  range_size test_type (0: Loadning, 1: Test ) account_index(default=0)")
    exit()

range_size = int(sys.argv[1])
test_type = int(sys.argv[2])
account_index = 0

if (len(sys.argv) == 4 ):
    account_index = int(sys.argv[3])

#SC = PublicSmartContract(account_index)
SC = PrivateSmartContract(account_index)

### intialization
logfile='operation_log_1M/Operation.LogA'
path_prefix = logfile.strip('\n').split('/')[0] + '/'
file_prefix = logfile.strip('\n').split('.')[1] 

MKBfile = path_prefix + 'mkb_' + file_prefix
TXLogFile = path_prefix + 'TX_' + file_prefix
TXLogFile += '_Motivation'
SC.get_contract_instance('./contracts_motivation_v2/Motivation.sol', TXLogFile)

mt=[] # merkle tree
leafs=[] # merkle tree leafs

### retrieve Merkle Tree from local file 
with open(MKBfile, 'rb') as mkb:
    mt = pickle.load(mkb)
    print ('Merkle Tree #nodes:', len(mt))

depth = getDepth(mt)
root = getRoot(mt)
indices = list(range(range_size))
proof=getProof(mt,indices)

'''
# non-merged proof
for index in range(range_size):
    proof.extend(getProof(mt, [index]))
'''

print ('proof length:', len(proof), 'indices:', indices, 'depth:', depth)

contract_type='Motivation'
# insert 300-600 records for on-chain 
if test_type == 0: 
    values=['0xc055e1dcf75e73ec3efb8c0535b465af6b154ff8ce9fd26de2c8c872b3e98909']*300
    SC.send_transactions(contract_type, 0, [0, 299, values], range_size, 'Loading')
    #SC.send_transactions(contract_type, 1, [300, 599, values], range_size, 'Loading')
    SC.send_transactions(contract_type, 2, [root], range_size, 'Loading_digest')

### call data replication
# write
elif test_type == 1: 
    values=['0xc055e1dcf75e73ec3efb8c0535b465af6b154ff8ce9fd26de2c8c872b3e98905']*range_size
    SC.send_transactions(contract_type, 0, [0, range_size-1, values], range_size, 'OnChainWrite_1')
    SC.send_transactions(contract_type, 1, [0, range_size-1], range_size, 'OnChainRead_2')
    
    ### call no data replication
    SC.send_transactions(contract_type, 2, [root], range_size, 'OffChainWrite_3')
    SC.send_transactions(contract_type, 3, [0, values, indices, proof, depth], range_size, 'OffChainRead_4')
