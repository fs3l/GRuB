#!/usr/bin/python3.6

import sys
from lib.testnet_smart_contract import PublicSmartContract

def hex_to_dec(s):
    return int(s,16)

if (len(sys.argv) < 2 ):
    print ("Usage: ./calculator TXLogfile offset operations_per_epoch")
    exit()

SC = PublicSmartContract()
f = open(sys.argv[1], 'r').readlines()
offset = int(sys.argv[2])
operations_per_epoch = int(sys.argv[3]) 

seq=1
phase_gas=0
phase_size=0
lines_count=0
print ('Epoch'+'\t'+'Gas per opeation (X10^3)')

for i in range(offset, len(f),1):
    line = f[i]
    lines_count += 1

    item = line.strip('\n').split('\t')
    tx_id = item[0]
    range_size = int(item[3]) 
    gas = item[2] 

    if gas == '':
       gas = int(SC.getTransactionReceipt(tx_id)['gasUsed'])
    else:
       gas = int(gas)  
 
    phase_gas += gas
    phase_size += range_size

    if lines_count >= operations_per_epoch:
        print(str(seq)+'\t'+str(phase_gas/1000.0/phase_size)) 
        seq += 1
        phase_gas=0
        phase_size=0
        lines_count=0

if lines_count > 0:
    print(str(seq)+'\t'+str(phase_gas/1000.0/phase_size))
