#! /usr/bin/python3.6
import sys
import pickle


from lib.memorizing import MemorizingState 
#from lib.memorizing_new import initialize_state, insert_state, make_decision_for_read,make_decision_for_write
from lib.utils import process, process_scan, order_by_decision, trim_by_decision
from lib.testnet_smart_contract import PublicSmartContract
from lib.local_smart_contract import PrivateSmartContract
from lib.pymerkletools import MerkleTools 

##################
###### main ######
##################

if (len(sys.argv) < 3 ):
    print ("Usage: ./driver.py loading_length range  test_type (0: Loading, 1: Test) account_index(default=0)")
    exit()

loading_len = int(sys.argv[1])
range_size = int(sys.argv[2])
test_type = int(sys.argv[3])
account_index = 0

if (len(sys.argv) == 5 ):
    account_index = int(sys.argv[4])


mt = MerkleTools()
onChainState = MemorizingState()
#SC = PublicSmartContract(account_index)
SC = PrivateSmartContract(account_index)

### intialization
logfile='log/workloadg.Log'
path_prefix = logfile.strip('\n').split('/')[0] + '/'
file_suffix = logfile.strip('\n').split('.')[1] 

mt.build_from_file(logfile, loading_len, False)
loading_keys = mt.get_all_keys()
indices = mt.get_indices_by_keys(loading_keys)
loading_keys_len = len(loading_keys)
print ('loading records length:', len(loading_keys), 'range: 0 -', indices[-1])
onChainState.initialize_state(loading_keys)

### execution phase
K=1
D=1
switch_times=4
test_times1=1
test_times2=2
write_times=1
read_times=5

onChainReadKeys=[]
offChainKeys=[]
offChainValues=[]

depth = mt.get_depth()
root = mt.get_root()

operate_range = list(range(range_size))
values = ['0xc055e1dcf75e73ec3efb8c0535b465af6b154ff8ce9fd26de2c8c872b3e98909']*range_size
digest = '0xc055e1dcf75e73ec3efb8c0535b465af6b154ff8ce9fd26de2c8c872b3e98909'

indices = operate_range
proof=mt.get_proof(indices)
print ('proof length:', len(proof), 'depth:', depth)

### test GRuB
Contract_Type = 'GRuB_Range_Query'

### Invoke OffChain_Rational
TXLogFile = 'TX_memorizing_' + Contract_Type + '_OffChain_Rational'
SC.get_contract_instance('./contracts_motivation_v2/memorizing/OffChain_Rational.sol', TXLogFile)
values=['0xc055e1dcf75e73ec3efb8c0535b465af6b154ff8ce9fd26de2c8c872b3e98904']*range_size

if test_type == 2:
    SC.send_transactions(Contract_Type, 2, [0, values, 0, indices, proof, depth], range_size, 'OffChainRead_NR')

if test_type == 0:
    SC.send_transactions(Contract_Type, 0, [0, 149, 300], range_size, 'Loading')
    SC.send_transactions(Contract_Type, 0, [150, 300, 300], range_size, 'Loading')

if test_type == 1:
    for i in range(switch_times):
        for k in range((i+1)*test_times1):
            # write many times 
            for j in range(write_times):
                submitKeys, submitValues, lastReplicateIndex = onChainState.make_decision_for_write(operate_range, values, K, D)
                if len(submitKeys) == 0:
                    offset = 0
                else:
                    offset = submitKeys[0]
                print('transaction range:', submitKeys, 'replicateIndex:', lastReplicateIndex, 'replicate len:', len(submitValues))
                #SC.send_transactions(Contract_Type, 1, [operate_range[0], operate_range[-1], offset, submitValues, root], range_size, 'Write')
         
            # read one time
            onChainReadKeys, offChainKeys, offChainValues, lastReplicateIndex = onChainState.make_decision_for_read( operate_range, values, K, D)
            if len(onChainReadKeys):
                print('OnChain read:', onChainReadKeys)
                #SC.send_transactions(Contract_Type, 3, [onChainReadKeys[0], onChainReadKeys[-1]], range_size, 'OnChainRead')
    
            if len(offChainKeys):
                print('OffChain read:', offChainKeys, 'replicate index:', lastReplicateIndex)
                #SC.send_transactions(Contract_Type, 2, [offChainKeys[0], offChainValues, lastReplicateIndex, indices, proof, depth], range_size, 'OffChainRead')

        ### workload shifting
        for k in range((i+1)*test_times1+1):
            # write one time
            submitKeys, submitValues, lastReplicateIndex = onChainState.make_decision_for_write( operate_range, values, K, D)
            if len(submitKeys) == 0:
                offset = 0
            else:
                offset = submitKeys[0]
            print('transaction range:', submitKeys, 'replicateIndex:', lastReplicateIndex, 'replicate len:', len(submitValues))
            #SC.send_transactions(Contract_Type, 1, [operate_range[0], operate_range[-1], offset, submitValues, root], range_size, 'Write')
         
            # read many times 
            for j in range(read_times):
                onChainReadKeys, offChainKeys, offChainValues, lastReplicateIndex = onChainState.make_decision_for_read(operate_range, values, K, D)
                if len(onChainReadKeys):
                    print('OnChain read:', onChainReadKeys)
                    #SC.send_transactions(Contract_Type, 3, [onChainReadKeys[0], onChainReadKeys[-1]], range_size, 'OnChainRead')
        
                if len(offChainKeys):
                    print('OffChain read:', offChainKeys, 'replicate index:', lastReplicateIndex)
                    #SC.send_transactions(Contract_Type, 2, [offChainKeys[0], offChainValues, lastReplicateIndex, indices, proof, depth], range_size, 'OffChainRead')

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

