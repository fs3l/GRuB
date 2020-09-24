#! /usr/bin/python3.6
import sys
import pickle

'''
   For a read operation, increase the read counter by 1 and compare it with K,
   if read counter is larger than or equal to K, 
   make a positive decision, otherwise make a negative decision 
'''

# we only maintain the read count
def make_decision_for_read(onStateFile, keys, values, K, D):
    with open(onStateFile, 'rb') as osf:
        state = pickle.load(osf)

    readCountersMap = state[0] 
    replicateMap = state[1]
    
    onChainKeys=[]
    offChainKeys=[] 
    offChainValues=[] 
    replicatedIndex=0 # marker to separate the replicated value and non-replicated value

    for i in range(len(keys)):
        key = keys[i] 
        value = values[i] 
    
        if replicateMap[key]:             # on-chain state is valid  
            if key not in onChainKeys:
                readCountersMap[key] += 1 # on-chain read needs to be counted
            onChainKeys.append(key)
        else:
            if key not in offChainKeys:  # A duplicate read doesn't modify the counter
                readCountersMap[key] += 1
            else:
                print('find a duplicate key:', key, ', from:', offChainKeys)

            offChainKeys.append(key)
            offChainValues.append(value)

            if readCountersMap[key] >= K:
                replicateMap[key] = True # update the local view
                replicatedIndex += 1     # replicate decision move the marker back

    #print(key, 'read count:', readCountersMap[key])
    # write on-chain state back to the file 
    state[0] = readCountersMap
    state[1] = replicateMap

    with open(onStateFile, 'wb') as osf:
        pickle.dump(state,osf)

    return onChainKeys, offChainKeys, offChainValues, replicatedIndex 

'''
   For a write operation, check the previous replicate state in the map,
   if it is R, then this write will also be replicated, but reset the read counter. 
'''

def make_decision_for_write(onStateFile, keys, values, K, D):
    with open(onStateFile, 'rb') as osf:
        state = pickle.load(osf)

    readCountersMap = state[0] 
    replicateMap = state[1]
  
    replicateKeys=[]
    replicateValues=[]
    invalidKeys=[]
    replicatedIndex=0  #marker to separate the replicated value and non-replicated value

    ret_keys=[]        # for those inserted keys or keys' onchain state is NR, we can omit it in the transaction 

    for i in range(len(keys)):
        key = keys[i] 
 
        if key in replicateMap: 
            if not replicateMap[key]:        # the on-chain state is NR, we need to tell SS to invalidate it 
                    invalidKeys.append(key) 
            else:                            # on-chain state is R, check the read counter
                if readCountersMap[key] >= K: 
                    replicateMap[key] = True
                    replicateKeys.append(key)
                    replicatedIndex += 1
                    replicateValues.append(values[i])
                else:
                    invalidKeys.append(key)  # a successor write
                    replicateMap[key] = False
            readCountersMap[key] = 0 # reset the read counter.
        else:
            # an insertion
            replicateMap[key] = False
            readCountersMap[key] = 0
 
    # write state back
    state[0] = readCountersMap
    state[1] = replicateMap
    
    with open(onStateFile, 'wb') as osf:
        pickle.dump(state,osf)
   
    # merge the replicate keys with invalid keys
    ret_keys.extend(replicateKeys)
    ret_keys.extend(invalidKeys)
    
    return ret_keys, replicateValues, replicatedIndex 

def initialize_state(onStateFile, loading_records):
    state = []
    readCountersMap = {} 
    replicateMap = {} 
   
    for key in loading_records:
        replicateMap[key] = False
        readCountersMap[key] = 0 

    # write the state back
    with open(onStateFile, 'wb') as osf:
        state.append(readCountersMap)
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
