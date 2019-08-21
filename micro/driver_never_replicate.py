#! /usr/bin/python3.6
import sys
import pickle

from lib.merkle_multi_queries import getRoot, getProof, getDepth, update_tree
from lib.testnet_smart_contract import PublicSmartContract
from lib.local_smart_contract import PrivateSmartContract
from lib.memorizing import initialize_state,make_decision_for_read,make_decision_for_write
from lib.utils import order_by_decision

##################
###### main ######
##################

if (len(sys.argv) < 3 ):
    print ("Usage: ./driver.py  test_type (0: Loading, 1: Test) account_index(default=0)")
    exit()

range_size = int(sys.argv[1])
test_type = int(sys.argv[2])
account_index = 0

if (len(sys.argv) == 4 ):
    account_index = int(sys.argv[3])

#SC = PublicSmartContract(account_index)
SC = PrivateSmartContract(account_index)

### intialization
logfile='log/Operation.LogA'
path_prefix = logfile.strip('\n').split('/')[0] + '/'
file_suffix = logfile.strip('\n').split('.')[1] 

TXLogFile = path_prefix + 'TX_Never_Replicate_' + file_suffix

loading_range = list(range(range_size))

### execution phase
test_times=10
write_times=10
read_times=64

operate_range = list(range(range_size))
values = ['0xc055e1dcf75e73ec3efb8c0535b465af6b154ff8ce9fd26de2c8c872b3e98909']*len(operate_range)
digest = '0xc055e1dcf75e73ec3efb8c0535b465af6b154ff8ce9fd26de2c8c872b3e98909'

indices = operate_range

Contract_Type = 'GRuB_Range_Query'

TXLogFile += '_' + Contract_Type + '_Never_Replicate'
SC.get_contract_instance('./contracts_motivation_v2/memorizing/Never_Replicate.sol', TXLogFile)
values=['0xc055e1dcf75e73ec3efb8c0535b465af6b154ff8ce9fd26de2c8c872b3e98904']*range_size


### no loading
'''
if test_type == 2:
    SC.send_transactions(Contract_Type, 2, [0, values, 0, indices, proof, depth], range_size, 'OffChainRead_NR')

if test_type == 0:
    SC.send_transactions(Contract_Type, 0, [0, 149, 300], range_size, 'Loading')
    SC.send_transactions(Contract_Type, 0, [150, 300, 300], range_size, 'Loading')
'''

if test_type == 1:
    for i in range(test_times):
        # write many times 
        for j in range(write_times):
            SC.send_transactions(Contract_Type, 1, [digest], range_size, 'Write')
     
        # read one time
        SC.send_transactions(Contract_Type, 2, [operate_range[0], values, indices, proof, depth], range_size, 'OffChainRead')

        ### workload shifting
        # write one time
        SC.send_transactions(Contract_Type, 1, [digest], range_size, 'Write')
     
        # read many times 
        for j in range(read_times):
            SC.send_transactions(Contract_Type, 2, [operate_range[0], values, indices, proof, depth], range_size, 'OffChainRead')

'''
### Invoke OffChain_Irrational
TXLogFile += '_' + Contract_Type + '_OffChain_Irrational'
SC.get_contract_instance('./contracts_motivation_v2/memorizing/OffChain_Irrational.sol', TXLogFile)
values=['0xc055e1dcf75e73ec3efb8c0535b465af6b154ff8ce9fd26de2c8c872b3e98904']*range_size

if test_type == 2:
    SC.send_transactions(Contract_Type, 2, [0, values, 0, indices, proof, depth], range_size, 'OffChainRead_NR')

if test_type == 0:
    SC.send_transactions(Contract_Type, 0, [0, 99], range_size, 'Loading')
    SC.send_transactions(Contract_Type, 0, [100, 199], range_size, 'Loading')
    SC.send_transactions(Contract_Type, 0, [200, 299], range_size, 'Loading')

if test_type == 1:
    for i in range(test_times):
        # write to a sub range
        submitKeys, submitValues, lastReplicateIndex = make_decision_for_write(onChainStateFile, operate_range, values, K, D)
        if len(submitKeys) == 0:
            offset = 0
            counters=[]
        else:
            offset = submitKeys[0]
            counters = [2]*len(operate_range)
        print('transaction range:', submitKeys, 'replicate range start from:', lastReplicateIndex, 'replicate range len:', len(submitValues))
        SC.send_transactions(Contract_Type, 1, [operate_range[0], operate_range[-1], offset, submitValues,counters,root], range_size, 'Write')
     
        # read a sub range
        for j in range(read_times):
            onChainReadKeys, offChainKeys, offChainValues, lastReplicateIndex = make_decision_for_read(onChainStateFile, operate_range, values, K, D)
            if len(onChainReadKeys):
                print('OnChain read:', onChainReadKeys)
                SC.send_transactions(Contract_Type, 3, [onChainReadKeys[0], onChainReadKeys[-1]], range_size, 'OnChainRead')
    
            if len(offChainKeys):
                print('OffChain read:', offChainKeys, 'replicate index:', lastReplicateIndex)
                SC.send_transactions(Contract_Type, 2, [offChainKeys[0], offChainValues, lastReplicateIndex, indices, proof, depth], range_size, 'OffChainRead')
'''

'''
### Invoke OnChain.sol 
TXLogFile += '_' + Contract_Type + '_OnChain'
SC.get_contract_instance('./contracts_motivation_v2/memorizing/OnChain.sol', TXLogFile)
values=['0xc055e1dcf75e73ec3efb8c0535b465af6b154ff8ce9fd26de2c8c872b3e98904']*range_size

if test_type == 2:
    SC.send_transactions(Contract_Type, 2, [0, values, 0, indices, proof, depth], range_size, 'OffChainRead_NR')

if test_type == 0:
    SC.send_transactions(Contract_Type, 0, [0, 49], range_size, 'Loading')
    SC.send_transactions(Contract_Type, 0, [50, 99], range_size, 'Loading')
    SC.send_transactions(Contract_Type, 0, [100, 149], range_size, 'Loading')
    SC.send_transactions(Contract_Type, 0, [150, 199], range_size, 'Loading')
    SC.send_transactions(Contract_Type, 0, [200, 249], range_size, 'Loading')

if test_type == 1:
    for i in range(test_times):
        # write to a sub range
        submitKeys, submitValues, lastReplicateIndex = make_decision_for_write(onChainStateFile, operate_range, values, K, D)
        print('transaction range:', submitKeys, 'replicate range start from:', lastReplicateIndex, 'replicate range len:', len(submitValues))
        SC.send_transactions(Contract_Type, 1, [operate_range[0], operate_range[-1], values, root], range_size, 'Write')
     
        # read a sub range
        for j in range(read_times):
            onChainReadKeys, offChainKeys, offChainValues, lastReplicateIndex = make_decision_for_read(onChainStateFile, operate_range, values, K, D)
            if len(onChainReadKeys):
                print('OnChain read:', onChainReadKeys)
                SC.send_transactions(Contract_Type, 3, [onChainReadKeys[0], onChainReadKeys[-1]], range_size, 'OnChainRead')
    
            if len(offChainKeys):
                print('OffChain read:', offChainKeys, 'replicate index:', lastReplicateIndex)
                SC.send_transactions(Contract_Type, 2, [offChainKeys[0], offChainValues, indices, proof, depth], range_size, 'OffChainRead')
'''

