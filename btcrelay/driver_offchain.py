#! /usr/bin/python3.6
import sys
import web3
from web3 import Web3
from lib.private_net import PrivateSmartContract
from lib.pymerkletools import MerkleTools 

##################
###### main ######
##################

if (len(sys.argv) < 4 ):
    print ("Usage: ./driver.py batch_size test_type (0: Loading, 1: Test) log account_index (default=0)")
    exit()

batch_size = int(sys.argv[1])
test_type = int(sys.argv[2])
log = sys.argv[3]
account_index = 0
if (len(sys.argv) == 5 ):
    account_index = int(sys.argv[4])

mk = MerkleTools()
SC = PrivateSmartContract(account_index)

records = []
with open(log, "r") as trace:
   records = trace.readlines()
 
def next_read(index, records):
    if index > len(records)-1:
        return False
    if records[index+1].strip("\n").split("\t")[0] == "R":
       return True
    return False

### test GRuB
Contract_Type = 'GRuB'
TXLogFile = 'results/TX_' + Contract_Type + '_Never_Replicate_' + str(batch_size)
SC.get_contract_instance('./contracts/offchain.sol', TXLogFile)

if test_type == 0:
    SC.send_transactions(Contract_Type, 1, [root], batch_size, 'Load')

if test_type == 1:
    RW_shift = False
    for r in records:
        record = r.strip("\n").split("\t")
        if record[0] == "W":
            num_blocks = int(record[1])
            for i in range(len(mk.leaves), num_blocks):
                mk.add_leaf("0x000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f")
            if next_read(records.index(r), records):
                mk.make_tree()
            root = mk.get_root()
            if not root:
                root = "0xcf55e1dcf75e73ec3efb8c0535b465af6b154ff8ce9fd26de2c8c872b3e98909"
            print ('root:', root, '#leaves:', len(mk.leaves))
            SC.send_transactions(Contract_Type, 1, [root], batch_size, 'Write')
            
        if (record[0] == "R"):
            # index starts from 0
            read_block = int(record[1])-1
            read_keys = [i for i in range(read_block, read_block+6)]
            values = ["0x000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f"] * 6
            # get proof
            if read_block > len(mk.leaves)-1:
                read_block = len(mk.leaves) - 1
            indices, proof=mk.get_proof(read_block)
            depth = mk.get_depth() 
            print ('#proof:', proof, "#indices:", indices, "depth", depth)
            SC.send_transactions(Contract_Type, 2, [read_keys, values, indices, proof, depth], 1, 'OffChainRead')
