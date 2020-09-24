#! /usr/bin/python3.6
import sys
import web3
from web3 import Web3
from lib.private_net import PrivateSmartContract

##################
###### main ######
##################

if (len(sys.argv) < 3 ):
    print ("Usage: ./driver.py batch_size test_type (0: Loading, 1: Test) depth account_index(default=0)")
    exit()

batch_size = int(sys.argv[1])
test_type = int(sys.argv[2])
depth = int(sys.argv[3])
account_index = 0
if (len(sys.argv) == 5 ):
    account_index = int(sys.argv[4])

### intialization
SC = PrivateSmartContract(account_index)

### execution phase
test_times = 2
read_times = 8
K = 2

onChainReadKeys=[]
offChainKeys=[]
offChainValues=[]

# addresses of tokens
#addresses=[]
#for i in range(batch_size):
#    Hash = Web3.sha3(hexstr=hex(i))
#    address = Web3.toHex(Hash[-20:])
#    addresses.append(Web3.toChecksumAddress(address))
#    print(address)
#
#read_keys=addresses[0:1]

# markets of tokens
markets=[]
for i in range(batch_size):
    markets.append(i)
read_keys=0
write_indices=markets
values = [12458125000000000000]*len(read_keys)
read_values=values[0:1]
write_keys=addresses

# price of tokens
print("read:",read_keys)
root = '0xcf55e1dcf75e73ec3efb8c0535b465af6b154ff8ce9fd26de2c8c872b3e98909'
proof = ['0xcf55e1dcf75e73ec3efb8c0535b465af6b154ff8ce9fd26de2c8c872b3e98909']*depth
indices = list(range(1, depth+1)) 
print ('proof length:', len(proof), 'depth:', depth)

### test GRuB
Contract_Type = 'GRuB'

### Invoke OffChain_Rational
TXLogFile = 'log/TX_' + Contract_Type + '_Rational_' + str(depth)
SC.get_contract_instance('../contracts/PriceFeed_GRuB.sol', TXLogFile)

if test_type == 2:
    SC.send_transactions(Contract_Type, 2, [0, values, 0, indices, proof, depth], range_size, 'OffChainRead_NR')

if test_type == 0:
    SC.send_transactions(Contract_Type, 0, [markets], batch_size, 'Load')

if test_type == 1:
    # write a sub range
    SC.send_transactions(Contract_Type, 1, [[], root], batch_size, 'Write')
   
    # read a sub range
    for j in range(read_times):
        if j > K: 
            SC.send_transactions(Contract_Type, 3, [read_keys, [], False, [], [], depth], 1, 'OnChainRead')
        elif j == K: 
            SC.send_transactions(Contract_Type, 3, [read_keys, read_values, True, indices, proof, depth], 1, 'OffChainRead_R')
        else:
            SC.send_transactions(Contract_Type, 3, [read_keys, read_values, False, indices, proof, depth], 1, 'OffChainRead_NR')

    for j in range(read_times):
        SC.send_transactions(Contract_Type, 1, [read_keys, root], batch_size, 'Write')
    SC.send_transactions(Contract_Type, 3, [read_keys, read_values, False, indices, proof, depth], 1, 'OffChainRead_NR')
