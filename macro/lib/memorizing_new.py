#! /usr/bin/python3.6
import sys

'''
   For a read operation, increase the read counter by 1 and compare it with K,
   if read counter is larger than or equal to K, 
   make a positive decision, otherwise make a negative decision 
'''
class MemorizingState(object):
    def __init__(self, loading_records=[]):
        self.reset_state()
 
        if len(loading_records) > 0:
            self.initialize_state(loading_records)

    def reset_state(self):
        self.readCountersMap = {} 
        self.replicateMap = {} 

    # we only maintain the read count
    def make_decision_for_read(self, keys, values, K, D):
        
        onChainKeys=[]
        offChainKeys=[] 
        offChainValues=[] 
        replicatedIndex=0 # marker to separate the replicated value and non-replicated value
    
        for i in range(len(keys)):
            key = keys[i] 
            value = values[i] 
        
            if key in self.replicateMap and self.replicateMap[key]:             # on-chain state is valid  
                if key not in onChainKeys:
                    self.readCountersMap[key] += 1 # on-chain read is only counted once
                onChainKeys.append(key)
            else:
                if key not in offChainKeys:  # A duplicate read doesn't modify the counter
                    self.readCountersMap[key] += 1
                else:
                    print('find a duplicate key:', key, ', from:', offChainKeys)
    
                offChainKeys.append(key)
                offChainValues.append(value)
    
                if self.readCountersMap[key] >= K:
                    self.replicateMap[key] = True # update the local view
                    replicatedIndex += 1     # replicate decision move the marker back
    
        return onChainKeys, offChainKeys, offChainValues, replicatedIndex 
    
    '''
       For a write operation, check the previous replicate state in the map,
       if it is R, then this write will also be replicated, but reset the read counter. 
    '''
    
    def make_decision_for_write(self, keys, values, K, D):
    
        replicateKeys=[]
        replicateValues=[]
        invalidKeys=[]
        replicatedIndex=0  # marker to separate the replicated value and non-replicated value
    
        ret_keys=[]        # for those inserted keys or its onchain state is NR, we can omit the value in the transaction 
    
        for i in range(len(keys)):
            key = keys[i] 
     
            if key in self.replicateMap: 
                if not self.replicateMap[key]:        # the on-chain state is NR, we need to tell SS to invalidate it 
                        invalidKeys.append(key) 
                else:                                 # on-chain state is R, check the read counter
                    if self.readCountersMap[key] >= K: 
                        self.replicateMap[key] = True
                        replicateKeys.append(key)
                        replicatedIndex += 1
                        replicateValues.append(values[i])
                    else:
                        invalidKeys.append(key)       # the successor reads of the latest replicated write
                        self.replicateMap[key] = False
                self.readCountersMap[key] = 0         # reset the read counter
            else:
                # an insertion
                self.replicateMap[key] = False
                self.readCountersMap[key] = 0
     
        # merge the replicate keys with invalid keys
        ret_keys.extend(replicateKeys)
        ret_keys.extend(invalidKeys)
        
        return ret_keys, replicateValues, replicatedIndex 
    
    def initialize_state(self, loading_records):
        for key in loading_records:
            if key not in self.replicateMap:
                self.replicateMap[key] = False
                self.readCountersMap[key] = 0 
    
    def insert_state(self, keys):
        for key in keys:
            if key not in self.replicateMap:
                self.replicateMap[key] = False
                self.readCountersMap[key] = 0 
