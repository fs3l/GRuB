#!/usr/bin/python3.6

import sys
from lib.testnet_smart_contract import PublicSmartContract

def hex_to_dec(s):
    return int(s,16)

if (len(sys.argv) < 2 ):
    print ("Usage: ./calculator TXLogfile")
    exit()

SC = PublicSmartContract()
f = open(sys.argv[1], 'r')
seq=1
phase_num=0
phase_gas=0
phase_size=0

print ('Timeline (index of epoch)'+'\t'+'Gas per operation (X1000)')

for line in f:
    item = line.strip('\n').split('\t')
    tx_id = item[0]
    phase = item[4]
    batchSize = int(item[3]) 
    gas = item[2] 

    if gas == '':
       gas = int(SC.getTransactionReceipt(tx_id)['gasUsed'])
    else:
       gas = int(gas)  
 
    if phase.find('_') > 0:
        new_phase_num = int(phase.split('_')[1])
        if new_phase_num > phase_num:
            print(str(seq)+'\t'+str(phase_gas/phase_size/1000)) 
            #print('last phase:' + str(phase_num) + ' gas:' + str(phase_gas) + '\t' + 'batchsize:' + str(phase_size)) 
            phase_num = new_phase_num
            phase_gas = gas
            phase_size = batchSize
            seq += 1
        else:
            phase_gas += gas
            phase_size += batchSize
    else:
        print(str(seq)+'\t'+str(gas/240/1000)) 
        seq += 1

#print('last phase:' + str(phase_num) + ' gas:' + str(phase_gas) + '\t' + 'batchsize:' + str(phase_size))

print(str(seq)+'\t'+str(phase_gas/phase_size/1000)) 
