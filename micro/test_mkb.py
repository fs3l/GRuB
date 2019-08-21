#! /usr/bin/python3.6
import sys
from lib.pymerkletools import MerkleTools 

############
####Main####
############
if (len(sys.argv) < 2 ):
	print ("Usage: ./build_mkb.py  recordcount")
	exit()

record_num = int(sys.argv[1])

mk = MerkleTools()

for i in range(record_num):
    mk.add_leaf(str(i))

mk.make_tree()
mk.get_tree()

print(mk.get_proof([1,2,3,4]))
