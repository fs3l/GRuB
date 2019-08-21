#! /usr/bin/python3.6
import sys
import pickle

from lib.merkle_multi_queries import getRoot, getProof, getDepth, update_tree
from lib.testnet_smart_contract import PublicSmartContract
from lib.local_smart_contract import PrivateSmartContract
from lib.memoryless import initialize_state,make_decision_for_read,make_decision_for_write
from lib.utils import order_by_decision

##################
###### main ######
##################

if (len(sys.argv) < 3 ):
    print ("Usage: ./driver.py  range_size test_type (0:Loading, 1: Test) account_index(default=0)")
    exit()

range_size = int(sys.argv[1])
test_type = int(sys.argv[2])
account_index = 0
K=8

if (len(sys.argv) == 4 ):
    account_index = int(sys.argv[3])

#SC = PublicSmartContract(account_index)
SC = PrivateSmartContract(account_index)

### intialization
logfile='operation_log_1M/Operation.LogA'
path_prefix = logfile.strip('\n').split('/')[0] + '/'
file_suffix = logfile.strip('\n').split('.')[1] 

MKBfile = path_prefix + 'mkb_' + file_suffix 
TXLogFile = path_prefix + 'TX_memoryless' + file_suffix
onChainStateFile = path_prefix + 'onChainState_memoryless_' + file_suffix

mt=[] # merkle tree
leafs=[] # merkle tree leafs

### retrieve Merkle Tree from local file 
with open(MKBfile, 'rb') as mkb:
    mt = pickle.load(mkb)
    print ('Merkle Tree #nodes:', len(mt))


loading_range = list(range(range_size))
initialize_state(onChainStateFile, loading_range)

### execution phase
test_times = 6 
read_times = K+1

onChainReadKeys=[]
offChainKeys=[]
offChainValues=[]

depth = getDepth(mt)
root = getRoot(mt)

operate_range = list(range(range_size))
values = ['0xc055e1dcf75e73ec3efb8c0535b465af6b154ff8ce9fd26de2c8c872b3e98909']*len(operate_range)
digest = '0xc055e1dcf75e73ec3efb8c0535b465af6b154ff8ce9fd26de2c8c872b3e98909'

indices = operate_range
proof=getProof(mt,indices)
print ('proof length:', len(proof), 'depth:', depth)

### test GRuB
Contract_Type = 'GRuB_Range_Query'

### Invoke OffChain_Rational
TXLogFile += '_' + Contract_Type + '_OffChain_Rational'
SC.get_contract_instance('./contracts_motivation_v2/memoryless/OffChain_Rational.sol', TXLogFile)
values=['0xc055e1dcf75e73ec3efb8c0535b465af6b154ff8ce9fd26de2c8c872b3e98904']*range_size

if test_type == 2:
    SC.send_transactions(Contract_Type, 2, [0, values, 0, indices, proof, depth], range_size, 'OffChainRead_NR')

if test_type == 0:
    SC.send_transactions(Contract_Type, 0, [0, 149], range_size, 'Loading')
    SC.send_transactions(Contract_Type, 0, [150, 300], range_size, 'Loading')

if test_type == 1:
    for i in range(test_times):
        # write to a sub range
        submitKeys = make_decision_for_write(onChainStateFile, operate_range)
        if len(submitKeys) == 0:
            offset = 0
        else:
            offset = submitKeys[0]
        print('transaction range:', submitKeys)
        SC.send_transactions(Contract_Type, 1, [operate_range[0], operate_range[-1], operate_range[0], [], root], range_size, 'Write')
     
        # read a sub range
        for j in range(read_times):
            onChainReadKeys, offChainKeys, offChainValues, lastReplicateIndex = make_decision_for_read(onChainStateFile, operate_range, values, K)
            if len(onChainReadKeys):
                print('OnChain read:', onChainReadKeys)
                SC.send_transactions(Contract_Type, 3, [onChainReadKeys[0], onChainReadKeys[-1]], range_size, 'OnChainRead')
    
            if len(offChainKeys):
                print('OffChain read:', offChainKeys, 'replicate index:', lastReplicateIndex)
                SC.send_transactions(Contract_Type, 2, [offChainKeys[0], offChainValues, lastReplicateIndex, indices, proof, depth], range_size, 'OffChainRead')

'''
### Invoke OffChain_Irrational
TXLogFile += '_Memoryless_OffChain_Irrational'
SC.get_contract_instance('./contracts_motivation_v2/memoryless/OffChain_Irrational.sol', TXLogFile)
values=['0xc055e1dcf75e73ec3efb8c0535b465af6b154ff8ce9fd26de2c8c872b3e98904']*range_size

if complete_test == 2:
    SC.send_transactions(Contract_Type, 3, [0, values, range_size, indices, proof, depth], range_size, 'OffChainRead_R')

if complete_test == 0:
    SC.send_transactions(Contract_Type, 0, [0, 149], range_size, 'Loading')
    SC.send_transactions(Contract_Type, 0, [150, 299], range_size, 'Loading')
    SC.send_transactions(Contract_Type, 0, [300, 349], range_size, 'Loading')

if complete_test == 1:
    # write
    SC.send_transactions(Contract_Type, 1, [0, range_size-1, 0,[], root], range_size, 'Write')
    
    # read_offchain 
    for i in range(K-1):
        # no replication
        SC.send_transactions(Contract_Type, 3, [0, values, 0, indices, proof, depth], range_size, 'OffChainRead_NR')
    
    # read_offchain replication
    SC.send_transactions(Contract_Type, 3, [0, values, range_size, indices, proof, depth], range_size, 'OffChainRead_R')
    
    # read_onchain
    SC.send_transactions(Contract_Type, 2, [0, range_size-1], range_size, 'OnChainRead')
   
    # next write 
    SC.send_transactions(Contract_Type, 1, [0, range_size-1, 0, [2]*range_size, root], range_size, 'Write')
'''
'''
### Invoke OnChain.sol 
TXLogFile += '_Memoryless_OnChain'
SC.get_contract_instance('./contracts_motivation_v2/memoryless/OnChain.sol', TXLogFile)
values=['0xc055e1dcf75e73ec3efb8c0535b465af6b154ff8ce9fd26de2c8c872b3e98904']*range_size

if complete_test == 0:
    SC.send_transactions(Contract_Type, 0, [0, 149], range_size, 'Loading')
    SC.send_transactions(Contract_Type, 0, [150, 299], range_size, 'Loading')
    SC.send_transactions(Contract_Type, 0, [300, 349], range_size, 'Loading')

if complete_test == 1:
    # write
    SC.send_transactions(Contract_Type, 1, [0, range_size-1, root], range_size, 'Write')
    
    # read_offchain 
    for i in range(K-1):
        # no replication
        SC.send_transactions(Contract_Type, 3, [0, values, indices, proof, depth], range_size, 'OffChainRead_NR')
    
    # read_offchain replication
    SC.send_transactions(Contract_Type, 3, [0, values, indices, proof, depth], range_size, 'OffChainRead_R')
    
    # read_onchain
    SC.send_transactions(Contract_Type, 2, [0, range_size-1], range_size, 'OnChainRead')
   
    # next write 
    SC.send_transactions(Contract_Type, 1, [0, range_size-1, root], range_size, 'Write')
'''
