#! /usr/bin/python3.6
import sys
import pickle

'''
   For a read operation, increase the read counter by 1 and compare it with write counter,
   if read counter is larger than or equal to write counter times K and plus D, 
   make a positive decision, otherwise make a negative decision 
'''
class MemorizingState(object):
    def __init__(self, loading_records=[]):
        self.reset_state()
 
        if len(loading_records) > 0:
            self.initialize_state(loading_records)

    def reset_state(self):
        self.readCountersMap = {} 
        self.writeCountersMap = {} 
        self.replicateMap = {} 

    def make_decision_for_read(self, keys, values, K, D):
        
        onChainKeys=[]
        offChainKeys=[] 
        offChainValues=[] 
        replicatedIndex=0 # marker to separate the replicated value and non-replicated value
    
        for i in range(len(keys)):
            key = keys[i] 
            value = values[i] 
        
            if self.replicateMap[key]:            # on-chain state is valid  
                onChainKeys.append(key)
                self.readCountersMap[key] += 1    # read on-chain, also increase the read counter
            else:
                if key not in offChainKeys:  # A duplicate read doesn't modify the counter
                    self.readCountersMap[key] += 1
                else:
                    print('find a duplicate key:', key, ', from:', offChainKeys)
    
                offChainKeys.append(key)
                offChainValues.append(value)
    
                if self.readCountersMap[key] >= K*(self.writeCountersMap[key]) + D:
                    self.replicateMap[key] = True # update the local view
                    replicatedIndex += 1     # replicate decision move the marker back
    
        return onChainKeys, offChainKeys, offChainValues, replicatedIndex 
    
    '''
       For a write operation, increase the write counter by 1 and compare it with read counter,
       if write counter times K is larger than read counter plus D, 
       make a negative decision, otherwise make a positive decision 
    '''
    
    def make_decision_for_write(self, keys, values, K, D):
      
        replicateKeys=[]
        replicateValues=[]
        invalidKeys=[]
        replicatedIndex=0  #marker to separate the replicated items with non-replicated items 
    
        ret_keys=[]        # for those inserted keys or keys' onchain state is NR, we can omit it in the transaction 
    
        for i in range(len(keys)):
            key = keys[i] 
            self.writeCountersMap[key] += 1
            #print(key, 'write count:', writeCountersMap[key], 'read count:', readCountersMap[key])
     
            if key in self.replicateMap: 
                if K*(self.writeCountersMap[key]) > self.readCountersMap[key] + D: # R -> NR
                    if self.replicateMap[key]:      # the on-chain state is R, we need to tell SS to invalidate it 
                        invalidKeys.append(key)
                        self.replicateMap[key] = False
                else:
                    self.replicateMap[key] = True
                    replicateKeys.append(key)
                    replicatedIndex += 1
                    replicateValues.append(values[i])
            else:
                # an insertion
                self.replicateMap[key] = False
                self.writeCountersMap[key] = 0
                self.readCountersMap[key] = 0
     
        # merge the replicate keys with invalid keys
        ret_keys.extend(replicateKeys)
        ret_keys.extend(invalidKeys)
        
        return ret_keys, replicateValues, replicatedIndex 
    
    def initialize_state(self, loading_records):
        for key in loading_records:
            self.replicateMap[key] = False
            self.readCountersMap[key] = 0 
            self.writeCountersMap[key] = 0
    
    def insert_state(self, keys):
    
        for key in keys:
            if key not in self.replicateMap: 
                self.replicateMap[key] = False
                self.readCountersMap[key] = 0
                self.writeCountersMap[key] = 0
