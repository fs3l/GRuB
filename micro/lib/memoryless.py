#! /usr/bin/python3.6
import sys
import pickle

'''
   For a read operation, increase the counter and compare it with K,
   if larger than K, make a positive decision, 
   otherwise make a negative decision 
'''

def make_decision_for_read(onStateFile, keys, values, K):
    with open(onStateFile, 'rb') as osf:
        state = pickle.load(osf)

    countersMap = state[0] 
    replicateMap = state[1]
    
    onChainKeys=[]
    offChainKeys=[] 
    offChainValues=[] 
    replicatedIndex=0     # marker to separate the replicated value and non-replicated value

    for i in range(len(keys)):
        key = keys[i] 
        value = values[i] 
        if replicateMap[key]:            # on-chain state is valid  
            onChainKeys.append(key)
        else:
            if key not in offChainKeys: # A duplicate read doesn't modify the counter
                countersMap[key] += 1
            else:
                print('find a duplicate key:', key, ', from:', offChainKeys)

            offChainKeys.append(key)
            offChainValues.append(value)

            if countersMap[key] >= K:
                replicateMap[key] = True
                replicatedIndex += 1     # replicate decision move the marker back

    # write on-chain state back to the file 
    state[0] = countersMap
    state[1] = replicateMap

    with open(onStateFile, 'wb') as osf:
        pickle.dump(state,osf)

    return onChainKeys, offChainKeys, offChainValues, replicatedIndex 

'''
   For a write operation, reset the counter to 0,
   and invalidate the on-chain state if it is valid.
'''

def make_decision_for_write(onStateFile, keys):
    with open(onStateFile, 'rb') as osf:
        state = pickle.load(osf)

    countersMap = state[0] 
    replicateMap = state[1]
  
    ret_keys=[]
    for key in keys:
        if key in replicateMap and replicateMap[key]: # the on-chain state is R 
            replicateMap[key] = False
            ret_keys.append(key)
            countersMap[key] = 0                          # reset the counter 

    # write state back
    state[0] = countersMap
    state[1] = replicateMap
    
    with open(onStateFile, 'wb') as osf:
        pickle.dump(state,osf)

    return ret_keys

def initialize_state(onStateFile, loading_keys):
    
    state = []
    countersMap = {} 
    replicateMap = {} 
   
    for key in loading_keys:
        replicateMap[key] = False
        countersMap[key] = 0

    # write state back
    with open(onStateFile, 'wb') as osf:
        state.append(countersMap)
        state.append(replicateMap)
        pickle.dump(state,osf)

def insert_state(onStateFile, keys):
    with open(onStateFile, 'rb') as osf:
        state = pickle.load(osf)

    readCountersMap = state[0] 
    writeCountersMap = state[1] 
    replicateMap = state[2]
 
    for key in keys:
        replicateMap[key] = False
        readCountersMap[key] = 0
        writeCountersMap[key] = 0

    state[0] = readCountersMap
    state[1] = writeCountersMap
    state[2] = replicateMap

    with open(onStateFile, 'wb') as osf:
        pickle.dump(state,osf)
