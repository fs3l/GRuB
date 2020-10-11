#! /usr/bin/python3.6
import sys
import pickle

from lib.memoryless import MemorylessState 
from lib.utils import process, process_scan, order_by_decision, trim_by_decision
from lib.pymerkletools import MerkleTools 
from lib.private_bkc import PrivateSmartContract

##################
###### main ######
##################

if (len(sys.argv) < 5 ):
    print ("Usage: ./driver_grub.py logfile recordcount max_range test_type(0:Loading, 1:Test) account_index(default:0) K(default:2)")
    exit()

logfile = sys.argv[1]
loading_len = int(sys.argv[2])
max_range = int(sys.argv[3])
test_type = int(sys.argv[4])
account_index = 0
K = 2 

if (len(sys.argv) == 6 ):
    account_index = int(sys.argv[5])
elif (len(sys.argv) == 7 ):
    account_index = int(sys.argv[5])
    K = float(sys.argv[6])

mt = MerkleTools()
onChainState = MemorylessState()
SC = PrivateSmartContract(account_index)

### intialization
path_prefix = logfile.strip('\n').split('/')[0] + '/'
file_prefix = logfile.strip('\n').split('.')[1] 
TXLogFile = 'log/TX_memoryless_' + file_prefix
print("K:",K)

### build Merkle Tree from log file 
mt.build_from_file(logfile, loading_len, True)
loading_keys = mt.get_all_keys()
indices = mt.get_indices_by_keys(loading_keys)
loading_keys_len = len(loading_keys)
print ('loading records length:', len(loading_keys), 'range:', indices[-1])

### process the log to partition the operation trace into multiple batches
Batches = process(logfile, loading_len, max_range)
print ('Batches length:', len(Batches))

### initialize on-chain state and drive the records into BKC
onChainState.initialize_state(loading_keys)

### Test OffChain_Rational 
loading_range=400
TXLogFile += '_OffChain_Rational_' + str(K)
Contract_type = 'GRuB_Range_Query'
SC.get_contract_instance('./contracts/Secure_DB.sol', TXLogFile)

# Loading phase
if test_type == 0:
    root = mt.get_root()
    if loading_keys_len <= loading_range:
        SC.send_transactions(Contract_type, 1, [ indices[0], indices[-1], 0, [], root], loading_keys_len, 'Loading')
    else:
        num=int(loading_keys_len/loading_range)
        for i in range(num):
            SC.send_transactions(Contract_type, 1, [indices[i*loading_range], indices[(i+1)*loading_range-1], 0, [], root], loading_range, 'Loading_'+str(i))
    
        if loading_keys_len > num*loading_range: 
            SC.send_transactions(Contract_type, 1, [indices[num*loading_range], indices[-1], 0, [], root], loading_keys_len-num*loading_range, 'Loading_'+str(i))

# Execution phase
if test_type == 1:
    for i in range(len(Batches)):
        batch = Batches[i]
        if len(batch) > 0:
            if  batch[0][0] == 'READ' or batch[0][0] == 'SCAN':
                if batch[0][0] == 'READ':
                    print ('A read batch:', batch)
                    keys = [item[1] for item in batch] 
                    values = [mt.get_values(key) for key in keys ]
                else:
                    print ('A scan batch:', batch)
                    keys, values = process_scan(batch, mt.get_key_indices_map(), mt.get_key_values_map())
                
                onChainKeys, offChainKeys, offChainValues, lastReplicateIndex = onChainState.make_decision_for_read(keys, values, K)

                # call read
                indices = mt.get_indices_by_keys(keys)
                offchain_data_indices = mt.get_indices_by_keys(offChainKeys)
                print('Read indices:', indices, 'Offchain indices:', offchain_data_indices, 'replicateIndex:', lastReplicateIndex)
                depth = mt.get_depth()
                proof = mt.get_proof(offchain_data_indices)
                SC.send_transactions(Contract_type, 2, [indices[0], indices[-1], offChainValues, lastReplicateIndex, offchain_data_indices, proof, depth], len(keys), 'Read_'+str(i))

            elif batch[0][0] == 'INSERT':
                print ('A insert batch:', batch)
                keys = [ item[1] for item in batch]
                values = [ item[2] for item in batch]
                values = mt.hash_leaves(values)

                onChainState.insert_state(keys)
                mt.insert_leaves(keys,values)
                indices = mt.get_indices_by_keys(keys)
                mt.make_tree()
                root = mt.get_root()
                print('new root:', root, 'Insert range:', indices[0], indices[-1]) 

                SC.send_transactions(Contract_type, 7, [root], len(batch), 'Insert_'+str(i))

            elif batch[0][0] == 'UPDATE':
                print ('A write batch:', batch)
                keys = [ item[1] for item in batch]
                values = [ item[2] for item in batch]
                values = mt.hash_leaves(values)

                mt.update_leaves(keys, values)

                submitKeys, submitValues, replicateIndex = onChainState.make_decision_for_write(keys, values, K) 
                indices = mt.get_indices_by_keys(submitKeys) 
                # update the merkle tree
                root = mt.get_root()
                print('submit indices:', indices, 'replicate:',replicateIndex, 'new root:', root) 
                SC.send_transactions(Contract_type, 4, [indices, submitValues, replicateIndex, root], len(batch), 'Write_'+str(i))
