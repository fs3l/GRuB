#! /usr/bin/python3.6
import sys
import web3
from web3 import Web3
sys.path.append("../")
from lib.private_net import PrivateSmartContract

##################
###### main ######
##################

if (len(sys.argv) < 4 ):
    print ("Usage: ./driver.py batch_size  test_type (0: Load, 1: Test) proof_size account_index(default=0)")
    exit()

batch_size = int(sys.argv[1])
test_type = int(sys.argv[2])
depth = int(sys.argv[3])
account_index = 0
if (len(sys.argv) == 5 ):
    account_index = int(sys.argv[4])

### intialization
SC = PrivateSmartContract(account_index)
logfile='log/workloada.Log_'+str(depth)
path_prefix = logfile.strip('\n').split('/')[0] + '/'
file_suffix = logfile.strip('\n').split('.')[1] 

# markets of tokens
markets=[]
for i in range(batch_size):
    markets.append(i)
read_keys=0
write_indices=markets

# price of tokens
values = [12458125000000000000]*batch_size
print("read:",read_keys)

Contract_Type = 'StableCoin'

# Run baseline 1
TXLogFile = path_prefix + 'TX_' + Contract_Type + '_Always_Replicate_ProofSize_' + str(depth)
SC.get_contract_instance('./contracts/StableCoin_BL1.sol', TXLogFile)

if test_type == 0:
    SC.send_transactions(Contract_Type, 0, [write_indices], batch_size, 'Load')

if test_type == 1:
    # poke once 
    SC.send_transactions(Contract_Type, 1, [write_indices, values], batch_size, 'Poke')
         
    # deposit once 
    SC.send_transactions(Contract_Type, 3, [read_keys], 1, 'Deposit')
    SC.send_transactions(Contract_Type, 3, [read_keys], 1, 'Deposit')
