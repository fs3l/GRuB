#! /usr/bin/python3.6
import sys
import pickle

from lib.memoryless import initialize_state, insert_state, make_decision_for_read, make_decision_for_write
from lib.utils import process, process_scan, order_by_decision, trim_by_decision
from lib.public_bkc import PublicSmartContract
from lib.private_bkc import PrivateSmartContract
from lib.pymerkletools import MerkleTools 

##################
###### main ######
##################

if (len(sys.argv) < 5 ):
    print ("Usage: ./driver.py logfile  recordcount  max_range test_type(0:Loading, 1:Test) account_index(default=0)")
    exit()

mt = MerkleTools()

logfile = sys.argv[1]
loading_len = int(sys.argv[2])
max_range = int(sys.argv[3])
test_type = int(sys.argv[4])
account_index = 0

if (len(sys.argv) == 6 ):
    account_index = int(sys.argv[5])

#SC = PublicSmartContract(account_index)
SC = PrivateSmartContract(account_index)

### intialization
path_prefix = logfile.strip('\n').split('/')[0] + '/'
file_prefix = logfile.strip('\n').split('.')[1] 

leafsfile = path_prefix + 'leafs_' + file_prefix
mapfile_key_indice = path_prefix + 'map_key_indice_' + file_prefix 
mapfile_key_value = path_prefix + 'map_key_value_' + file_prefix 
onChainStateFile = path_prefix + 'memoryless_onChainState_' + file_prefix 
TXLogFile = path_prefix + 'TX_memoryless_' + file_prefix

loading_keys = [] 
Batches=[]
K=2

### retrieve Merkle Tree from local file 
with open(leafsfile, 'rb') as lff:
    leafs=[] # merkle tree leafs
    leafs = pickle.load(lff)
    print ('#leaves:', len(leafs))
    mt.retrieve_leafs(leafs)

mt.make_tree()

### retrieve map of key to indice from local file 
map_key_indices={}
with open(mapfile_key_indice, 'rb') as mapfile:
    map_key_indices = pickle.load(mapfile)

loading_keys = list(map_key_indices.keys())

### retrieve map of key to value from local file 
map_key_values={}
with open(mapfile_key_value, 'rb') as mapfile:
    map_key_values = pickle.load(mapfile)

### process the log to partition the operation trace into multiple batches
Batches = process(logfile, loading_len, max_range)

### initialize on-chain state and drive the records into BKC
indices = [map_key_indices.get(key) for key in loading_keys]
loading_keys_len = len(indices) 

print ('loading records range:', len(loading_keys))
print ('Batches length:', len(Batches))
initialize_state(onChainStateFile, loading_keys)

### Test OffChain_Rational 
loading_range=200
TXLogFile += '_OffChain_Rational'
Contract_type = 'GRuB_Range_Query'
SC.get_contract_instance('./contracts_motivation_v2/memoryless/OffChain_Rational.sol', TXLogFile)

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
                keys = [key[1] for key in batch] 
                values = [map_key_values.get(key) for key in keys ]
    
            else:
                print ('A scan batch:', batch)
                keys, values = process_scan(batch, map_key_indices, map_key_values)
            
            onChainReadKeys, offChainKeys, offChainValues, lastReplicateIndex = make_decision_for_read(onChainStateFile, keys, values, K)
            # call on-chain read
            if len(onChainReadKeys) > 0:
                indices = [map_key_indices.get(key) for key in onChainReadKeys ]
                print('On_Chain_Read:', indices)
                SC.send_transactions(Contract_type, 3, [indices[0], indices[-1]], len(onChainReadKeys), 'OnR_'+str(i))
    
            # call off-chain read
            if len(offChainKeys) > 0:
                indices = [map_key_indices.get(key) for key in offChainKeys ]
                print('Off_Chain_Read:', indices)
                depth = mt.get_depth()
                proof = mt.get_proof(indices)
                SC.send_transactions(Contract_type, 2, [indices[0], offChainValues, lastReplicateIndex, indices, proof, depth], len(offChainKeys), 'OffR_'+str(i))
    
        elif batch[0][0] == 'INSERT':
            print ('A insert batch:', batch)
            keys = [ item[1] for item in batch]
            values = [ item[2] for item in batch]
            values = mt.hash_leaves(values)
        
            for j in range(len(keys)):
                map_key_indices[keys[j]] = mt.get_leaf_count() 
                map_key_values[keys[j]] = values[j] 
                mt.add_leaf(values[j])
                insert_state(onChainStateFile, keys)

            indices = [map_key_indices.get(key) for key in keys]
            mt.make_tree()
            digest = mt.get_root()
            print('new digest:', digest, 'updated range:', indices[0], indices[-1]) 
            SC.send_transactions(Contract_type, 1, [indices[0], indices[-1], 0, [], digest], len(batch), 'Insert_'+str(i))

        elif batch[0][0] == 'UPDATE':
            print ('A write batch:', batch)
            keys = [ item[1] for item in batch]
            values = [ item[2] for item in batch]
            values = mt.hash_leaves(values)

            for j in range(len(keys)):
                map_key_values[keys[j]] = values[j] 

            indices = [map_key_indices.get(key) for key in keys]
            submitKeys = make_decision_for_write(onChainStateFile, keys) 
    
            # update the merkle tree
            mt.update_leaves(indices, values)
            digest = mt.get_root()
            print('new digest:', digest, 'updated index:', indices)

            # no write will be replicated 
            #SC.send_transactions(Contract_type, 1, [indices[0], indices[-1], 0, [], digest], len(batch), 'Update_'+str(i))

            SC.send_transactions(Contract_type, 4, [indices, [], 0, digest], len(batch), 'Write_'+str(i))
