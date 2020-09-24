#! /usr/bin/python3.6
import sys
import web3
from web3 import Web3
from lib.private_net import PrivateSmartContract

##################
###### main ######
##################

if (len(sys.argv) < 4 ):
    print ("Usage: ./driver.py batch_size test_type (0: Load, 1: Test) log account_index(default=0)")
    exit()

batch_size = int(sys.argv[1])
test_type = int(sys.argv[2])
logfile = sys.argv[3]
account_index = 0
if (len(sys.argv) == 5 ):
    account_index = int(sys.argv[4])

### intialization
records = []
with open(logfile, "r") as trace:
   records = trace.readlines()

# Run baseline 1
Contract_Type = "GRuB"
SC = PrivateSmartContract(account_index)
TXLogFile = 'results/TX_' + Contract_Type + '_Always_Replicate_' + str(batch_size)
SC.get_contract_instance('./contracts/onchain.sol', TXLogFile)

if test_type == 0:
    SC.send_transactions(Contract_Type, 0, [write_indices], batch_size, 'Load')

if test_type == 1:
    for r in records:
        record = r.strip("\n").split("\t")
        if record[0] == "W":
            starting_block = int(record[1])
            write_indices = [i for i in range(starting_block, starting_block+batch_size)]
            values = ['0x000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f'] * len(write_indices)
            SC.send_transactions(Contract_Type, 1, [write_indices, values], batch_size, 'Write')

        elif (record[0] == "R"):
            read_block = int(record[1])
            read_keys = [ i for i in range(read_block, read_block+6)]
            SC.send_transactions(Contract_Type, 3, [read_keys], 1, 'OnChainRead')
