#! /usr/bin/python3.6
import sys
import pickle

from lib.memorizing_kl import MemorizingState 
from lib.utils import process, process_scan, order_by_decision, trim_by_decision
from lib.public_bkc import PublicSmartContract
from lib.private_bkc import PrivateSmartContract
from lib.pymerkletools import MerkleTools 

##################
###### main ######
##################

if (len(sys.argv) < 5 ):
    print ("Usage: ./driver.py logfile recordcount max_range test_type(0:Loading, 1:Test) account_index(default:0) K(default:0)")
    exit()

logfile = sys.argv[1]
loading_len = int(sys.argv[2])
max_range = int(sys.argv[3])
test_type = int(sys.argv[4])
account_index = 0
K = 0

if (len(sys.argv) == 6 ):
    account_index = int(sys.argv[5])
elif (len(sys.argv) == 7 ):
    account_index = int(sys.argv[5])
    K = int(sys.argv[6])

mt = MerkleTools()
onChainState = MemorizingState()
#SC = PublicSmartContract(account_index)
SC = PrivateSmartContract(account_index)

### intialization
path_prefix = logfile.strip('\n').split('/')[0] + '/'
file_prefix = logfile.strip('\n').split('.')[1] 
TXLogFile = path_prefix + 'TX_memorizing_' + file_prefix

Batches=[]
D=1
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
loading_range=200
TXLogFile += '_OffChain_Rational_' + str(K)
Contract_type = 'GRuB_Range_Query'
SC.get_contract_instance('./contracts/memorizing/OffChain_Rational.sol', TXLogFile)

# Loading phase
if test_type == 0:
    if loading_keys_len <= loading_range:
        SC.send_transactions(Contract_type, 0, [indices[0], indices[-1], indices[-1]], loading_keys_len, 'Loading')
    else:
        num=int(loading_keys_len/loading_range)
        for i in range(num):
            SC.send_transactions(Contract_type, 0, [indices[i*loading_range], indices[(i+1)*loading_range-1], indices[-1]], loading_range, 'Loading')
    
        if loading_keys_len > num*loading_range: 
            SC.send_transactions(Contract_type, 0, [indices[num*loading_range], indices[-1], indices[-1]], loading_keys_len-num*loading_range, 'Loading')

# Execution phase
elif test_type == 1:
    onChainReadKeys=[]
    offChainKeys=[]
    offChainValues=[]
    indices=[]
    
    for i in range(len(Batches)):
        batch = Batches[i]
        if  batch[0][0] == 'READ' or batch[0][0] == 'SCAN':
            if batch[0][0] == 'READ':
                print ('A read batch:', len(batch))
                keys = [item[1] for item in batch] 
                values = [mt.get_values(key) for key in keys ]
    
            else:
                print ('A scan batch:', batch)
                keys, values = process_scan(batch, mt.get_key_indices_map(), mt.get_key_values_map())
            
            onChainReadKeys, offChainKeys, offChainValues, lastReplicateIndex = onChainState.make_decision_for_read(keys, values, K, D)

            # call on-chain read
            if len(onChainReadKeys) > 0:
                indices = mt.get_indices_by_keys(onChainReadKeys)
                print('On_Chain_Read:', indices)
                SC.send_transactions(Contract_type, 3, [indices[0], indices[-1]], len(onChainReadKeys), 'OnR_'+str(i))
    
            # call off-chain read
            if len(offChainKeys) > 0:
                indices = mt.get_indices_by_keys(offChainKeys)
                print('Off_Chain_Read:', indices)
                depth = mt.get_depth()
                proof = mt.get_proof(indices)
                SC.send_transactions(Contract_type, 2, [indices[0], offChainValues, lastReplicateIndex, indices, proof, depth], len(offChainKeys), 'OffR_'+str(i))
    
        elif batch[0][0] == 'INSERT':
            print ('A insert batch:', len(batch))
            keys = [ item[1] for item in batch]
            values = [ item[2] for item in batch]
            values = mt.hash_leaves(values)

            onChainState.insert_state(keys)
            mt.insert_leaves(keys,values)
            indices = mt.get_indices_by_keys(keys)
            mt.make_tree()
            digest = mt.get_root()
            print('new digest:', digest, 'updated range:', indices[0], indices[-1]) 

            SC.send_transactions(Contract_type, 1, [indices[0], indices[-1], 0, [], digest], len(batch), 'Insert_'+str(i))

        elif batch[0][0] == 'UPDATE':
            print ('A write batch:', len(batch))
            keys = [ item[1] for item in batch]
            values = [ item[2] for item in batch]
            values = mt.hash_leaves(values)

            mt.update_leaves(keys, values)
            indices = mt.get_indices_by_keys(keys) 

            submitKeys, submitValues, lastReplicateIndex = onChainState.make_decision_for_write( keys, values, K, D) 
    
            # update the merkle tree
            digest = mt.get_root()
            print('new digest:', digest, 'updated index:', indices, 'replicate index:', lastReplicateIndex) 
            SC.send_transactions(Contract_type, 4, [indices, submitValues, lastReplicateIndex, digest], len(batch), 'Write_'+str(i))
