#! /usr/bin/python3.6
import sys
import pickle

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

logfile = sys.argv[1]
loading_len = int(sys.argv[2])
max_range = int(sys.argv[3])
test_type = int(sys.argv[4])
account_index = 0

if (len(sys.argv) == 6 ):
    account_index = int(sys.argv[5])
elif (len(sys.argv) == 7 ):
    account_index = int(sys.argv[5])

mt = MerkleTools()
#SC = PublicSmartContract(account_index)
SC = PrivateSmartContract(account_index)

### intialization
path_prefix = logfile.strip('\n').split('/')[0] + '/'
file_prefix = logfile.strip('\n').split('.')[1] 
TXLogFile = 'log/TX_' + file_prefix

### build Merkle Tree from log file 
mt.build_from_file(logfile, loading_len, True)
loading_keys = mt.get_all_keys()
indices = mt.get_indices_by_keys(loading_keys)
loading_keys_len = len(loading_keys)
print ('loading records length:', len(loading_keys), 'range:', indices[-1])

### process the log to partition the operation trace into multiple batches
Batches = process(logfile, loading_len, max_range)
print ('Batches length:', len(Batches))

### Test Never_Replicate 
loading_range=max_range
TXLogFile += '_Never_Replicate'
Contract_type = 'GRuB_Range_Query'
SC.get_contract_instance('./contracts/Never_Replicate.sol', TXLogFile)

# Loading phase
if test_type == 0:
   root = mt.get_root()
   if loading_keys_len <= loading_range:
       SC.send_transactions(Contract_type, 1, [root], loading_keys_len, 'Loading'+str(i))
   else:
       num=int(loading_keys_len/loading_range)
       for i in range(num):
           SC.send_transactions(Contract_type, 1, [root], loading_range, 'Loading'+str(i))
   
       if loading_keys_len > num*loading_range:
           SC.send_transactions(Contract_type, 1, [root], loading_keys_len-num*loading_range, 'Loading'+str(i+1))

# Execution phase
if test_type == 1:
    for i in range(len(Batches)):
        batch = Batches[i]
        if len(batch) > 0:
            if  batch[0][0] == 'READ' or batch[0][0] == 'SCAN':
                keys=[]
                values=[]
                if batch[0][0] == 'READ':
                    print ('A read batch:', len(batch))
                    keys = [item[1] for item in batch] 
                    values = [mt.get_values(key) for key in keys ]
                else:
                    print ('A scan batch:', batch)
                    keys, values = process_scan(batch, mt.get_key_indices_map(), mt.get_key_values_map())

                indices = mt.get_indices_by_keys(keys)
                # call off-chain read
                depth = mt.get_depth()
                proof = mt.get_proof(indices)
                SC.send_transactions(Contract_type, 2, [indices[0], values, indices, proof, depth], len(keys), 'OffR_'+str(i))

            elif batch[0][0] == 'INSERT':
                print ('A insert batch:', len(batch))
                keys = [ item[1] for item in batch]
                values = [ item[2] for item in batch]
                values = mt.hash_leaves(values)

                mt.insert_leaves(keys,values)
                indices = mt.get_indices_by_keys(keys)
                mt.make_tree()
                root = mt.get_root()
                SC.send_transactions(Contract_type, 1, [root], len(batch), 'Insert_'+str(i))

            elif batch[0][0] == 'UPDATE':
                print ('A write batch:', len(batch))
                keys = [ item[1] for item in batch]
                values = [ item[2] for item in batch]
                values = mt.hash_leaves(values)

                mt.update_leaves(keys, values)
                root = mt.get_root()
                indices = mt.get_indices_by_keys(keys)
                SC.send_transactions(Contract_type, 1, [root], len(batch), 'Write_'+str(i))
