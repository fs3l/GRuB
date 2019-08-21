#! /usr/bin/python3.6
import sys
import pickle
import numpy as np
from lib.merkle_multi_queries import hash_leaf,make_tree, getRoot, getProof,verify

############
####Main####
############
if (len(sys.argv) < 3 ):
	print ("Usage: ./build_mkb.py  logfile  recordcount")
	exit()

logfile = sys.argv[1]
record_num = int(sys.argv[2])

path_prefix = logfile.strip('\n').split('/')[0] + '/'
file_prefix = logfile.strip('\n').split('.')[1] 

MKBfile = path_prefix + 'mkb_' + file_prefix
leafsfile = path_prefix + 'leafs_' + file_prefix
mapfile_key_indice = path_prefix + 'map_key_indice_' + file_prefix 


LOG = open(logfile,"r").readlines()

# build Merkle tree
mt=[]
leafs=[]
key_indices={}

proofs=[]

for i in range(0,record_num,1):
    record_items = LOG[i].strip('\n').split('\t')
    key = record_items[0] 
    key_indices[key] = len(leafs)
    leafs.append(hash_leaf(key))

mt=make_tree(leafs)
print ('Merkle Tree #nodes:', len(mt))

with open(MKBfile, 'wb') as mkb:
    pickle.dump(mt, mkb)

with open(leafsfile, 'wb') as lff:
    pickle.dump(leafs, lff)

with open(mapfile_key_indice, 'wb') as mapfile:
    pickle.dump(key_indices, mapfile)
