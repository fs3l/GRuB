#! /usr/bin/python3.6
import sys
from random import randrange
'''
   For a read operation, increase the counter and compare it with K,
   if larger than K, make a positive decision, 
   otherwise make a negative decision 
'''

class MemorylessState(object):
    def __init__(self, loading_records=[]):
        self.reset_state()
 
        if len(loading_records) > 0:
            self.initialize_state(loading_records)

    def reset_state(self):
        self.countersMap = {} 
        self.replicateMap = {} 

    def make_decision_for_read(self, keys, values, K):
        
        onChainKeys=[]
        offChainKeys=[] 
        offChainValues=[] 
        replicatedIndex=0     # marker to separate the replicated value and non-replicated value
    
        for i in range(len(keys)):
            key = keys[i] 
            value = values[i] 
            if key not in self.replicateMap: 
                self.insert_state([key])
            else:
                if self.replicateMap[key]:            # on-chain state is valid  
                    onChainKeys.append(key)
                else:
                    if key not in offChainKeys: # A duplicate read doesn't modify the counter
                        self.countersMap[key] += 1
                    else:
                        print('find a duplicate key:', key, ', from:', offChainKeys)
    
                    offChainKeys.append(key)
                    offChainValues.append(value)
    
                    if self.countersMap[key] >= K:
                        self.replicateMap[key] = True
                        replicatedIndex += 1     # replicate decision move the marker back
    
        return onChainKeys, offChainKeys, offChainValues, replicatedIndex 
    
    '''
       For a write operation, reset the counter to 0,
       and invalidate the on-chain state if it is valid.
    '''
    
    def make_decision_for_write(self, keys, values, K):
      
        ret_keys=[]
        ret_values=[]
        replicateIndex=0

        for i in range(len(keys)):
            key = keys[i]
            if K >= 1:
                if key in self.replicateMap and self.replicateMap[key]: # the on-chain state is R 
                    self.replicateMap[key] = False
                    ret_keys.append(key)                               # needs to tell bkc to invalidate on-chain replica
                    self.countersMap[key] = 0                          # reset the counter 
            else:
                lowerbound = randrange(10) # randomize 0-9
                if (1-K)*10 > lowerbound:
                    self.replicateMap[key] = True
                    ret_keys.append(key)
                    ret_values.append(values[i])
                    replicateIndex += 1
                    self.countersMap[key] = 0

        return ret_keys, ret_values, replicateIndex
    
    def initialize_state(self, loading_keys):
        
        self.countersMap = dict() 
        self.replicateMap = dict()
       
        for key in loading_keys:
            self.replicateMap[key] = False
            self.countersMap[key] = 0
    
    def insert_state(self, keys):
        for key in keys:
            if key not in self.replicateMap:
                print('insert key:', key)
                self.replicateMap[key] = False
                self.countersMap[key] = 0
