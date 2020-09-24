#! /usr/bin/python3.6

import sys

def update_key_value_map(keys, values, map_key_value):
    
    for i in range(len(keys)):
        map_key_value[keys[i]] = values[i]

def order_by_decision(keys, values, decisions):
    #print ('before order:', keys, values, decisions)
    ret_keys=[]
    ret_values=[]
   
    left_keys=[] 
    left_values=[] 
    for i in range(len(decisions)):
        if decisions[i]:
            ret_keys.append(keys[i])
            ret_values.append(values[i])
        else:
            left_keys.append(keys[i])   
            left_values.append(values[i])   
   
    replicateIndex = len(ret_keys)
    ret_keys.extend(left_keys)
    ret_values.extend(left_values)

    #print('after order:', ret_keys, ret_values, replicateIndex)
    return ret_keys, ret_values, replicateIndex

def trim_by_decision(keys, values, decisions):
    #print('before trim:', keys, values, decisions)
    ret_keys=[]
    ret_values=[]

    for i in range(len(decisions)):
        if decisions[i]:
            ret_keys.append(keys[i])
            ret_values.append(values[i])
    #print('after trim:', ret_keys,ret_values)
    return ret_keys, ret_values

def process(logfile, loading_len, max_range):
    LOG = open(logfile,"r").readlines()

    Batches=[]
    Loading_keys=[]

    ReadBatch=[]
    WriteBatch=[]
    WriteBatchKeys=[]

    for i in range(loading_len, len(LOG), 1):
        record_items = LOG[i].strip('\n').split(' ')
        record = []
        record.append(record_items[0])  # op_type
        record.append(record_items[2])  # key
        record.append(record_items[3])  # recordcount for scan operation
        record.append(record_items[4])  # value
        Batches, ReadBatch, WriteBatch, WriteBatchKeys = partition(record, Batches, max_range, ReadBatch, WriteBatch, WriteBatchKeys)

    # collect the last batch if any 
    if len(WriteBatch) > 0:
        Batches.append(WriteBatch)
    if len(ReadBatch) > 0:
        Batches.append(ReadBatch)

    #print(Batches)
    return Batches #, Loading_keys

def pre_loading(record, loading_keys):
    key = record[1]
    if key not in loading_keys:
        loading_keys.append(key)

# since the update operations are not sequential, one update operation forms a write batch
def partition(record, Batches, BatchSize, ReadBatch, WriteBatch, WriteBatchKeys):
    op_type = record[0]
    key = record[1]
    value = record[3]
    if op_type == 'READ':
        item = []
        item.append(op_type)
        item.append(key)
        ReadBatch.append(item)
        if len(ReadBatch) >= BatchSize:
            print ("Read batch size:",len(ReadBatch))
            Batches.append(ReadBatch)
            ReadBatch=[]

    elif op_type == 'SCAN':
        item = []
        item.append(op_type)
        item.append(key)
        item.append(record[2])

        if len(WriteBatch) > 0:
            Batches.append(WriteBatch)
            WriteBatch=[]
        ReadBatch.append(item)
        Batches.append(ReadBatch)
        ReadBatch=[]

    else:
        item = []
        item.append(op_type)
        item.append(key)
        item.append(value)
        if len(ReadBatch) > 0:  # some reads happens before the write
            print ("Read batch size:",len(ReadBatch))
            Batches.append(ReadBatch)
            ReadBatch=[]
        WriteBatch.append(item)

        # Batch multiple write         
        if len(WriteBatch) >= BatchSize:
            Batches.append(WriteBatch)
            WriteBatch=[]

    return Batches, ReadBatch, WriteBatch, WriteBatchKeys

def process_scan(batch, map_key_indices, map_key_values):
    ret_keys=[]
    ret_values=[]

    indices_list=list(map_key_indices.values())
    key_list = list(map_key_indices.keys())

    for item in batch:
        key = item[1]
        record_count = int(item[2]) 
        index = map_key_indices[key]
        for i in range(index, index+record_count):
            if i in indices_list:
                key = list(map_key_indices.keys())[list(map_key_indices.values()).index(i)]
                value = map_key_values[key]
                ret_keys.append(key)
                ret_values.append(value)
                #print('index:',i,'key:',key, 'value:',value)
    return ret_keys, ret_values


def get_writes(logfile, offset, max_range):
    num=0
    ret=[]
    LOG = open(logfile,"r").readlines()
    for i in range(offset, len(LOG), 1):
        items = LOG[i].strip('\n').split(' ')
        if  items[0] == 'UPDATE':
            ret.append(items[2])
            num += 1
            if num >= max_range:
                break
    return ret

def get_reads(logfile, offset, max_range):
    num=0
    ret=[]
    LOG = open(logfile,"r").readlines()
    for i in range(offset, len(LOG), 1):
        items = LOG[i].strip('\n').split(' ')
        if  items[0] == 'READ' or items[0] == 'SCAN':
            #record = []
            #record.append(items[2])
            #record.append(items[3])
            #ret.append(record)
            ret.append(items[2])
            num += 1
            if num >= max_range:
                break
    return ret

'''
def partition(record, Batches, BatchSize, ReadBatch, WriteBatch, WriteBatchKeys):
    op_type = record[0]
    key = record[1]
    value = record[2]
    if op_type == 'READ' or op_type == 'SCAN':
        ReadBatch.append(key)
        if len(ReadBatch) >= BatchSize:
            print ("Read batch size:",len(ReadBatch))
            Batches.append(ReadBatch)
            ReadBatch=[]
    else:
         if key in ReadBatch:  # a read happens before the write
             print ("Read batch size:",len(ReadBatch))
             Batches.append(ReadBatch)
             ReadBatch=[]
         if key in WriteBatchKeys:
             Batches.append(WriteBatch)
             print ("Write batch size:",len(WriteBatch))
             WriteBatch=[]
             WriteBatchKeys=[]
             WriteBatch.append({key:value})
             WriteBatchKeys.append(key)
         else:
             WriteBatch.append({key:value})
             WriteBatchKeys.append(key)
             if len(WriteBatch) >= BatchSize:
                 print ("Write batch size:",len(WriteBatch))
                 Batches.append(WriteBatch)
                 WriteBatch=[]
                 WriteBatchKeys=[]
    return Batches, ReadBatch, WriteBatch, WriteBatchKeys
'''
