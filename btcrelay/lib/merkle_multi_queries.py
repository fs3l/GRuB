#! /usr/bin/python3.6

import hashlib
import math
import binascii
from web3 import Web3

class MerkleTools(object):
    def __init__(self, hash_type="sha256"):
        self.reset_tree()

    def reset_tree(self):
        self.leaves = list()
        self.tree = list()
        self.is_ready = False
        self.map_key_indices=dict()
        self.map_key_values=dict()

    def hash_leaf(self, value):
        v = Web3.soliditySha3(['string'], [value])
        return v.hex()

    def hash_node(self, left, right):
        '''Convert two digests to their Merkle node's digest'''
        v = Web3.soliditySha3(['bytes32', 'bytes32'], [left, right])
        return v.hex()

    def make_tree(self):
        '''Compute the Merkle tree of a list of values.
        The result is returned as a list where each value represents one hash in the
        tree. The indices in the array are as in a bbinary heap array.
        '''
        num_leafs = len(self.leaves)
        depth = int(math.log(num_leafs,2))
        assert(num_leafs == 2**depth)
        num_nodes = 2 * num_leafs
        self.tree = [None] * num_nodes
        for i in range(num_leafs):
            self.tree[2**depth + i] = self.leaves[i]
        for i in range(2**depth - 1, 0, -1):
            self.tree[i] = self.hash_node(self.tree[2*i], self.tree[2*i + 1])
    
    def update_tree(self, indices, values):
    
        for i in range(len(values)):
            self.leaves[indices[i]] = values[i]
        self.make_tree()

    def get_root(self):
        return self.tree[1]

    def get_depth(self):
        return int(math.log(len(self.tree),2)) - 1 

    def get_proof(self, indices):
        '''Given a Merkle tree and a set of indices, provide a list of decommitments
        required to reconstruct the merkle root.'''
        depth = int(math.log(len(self.tree),2)) - 1
        num_leafs = 2**depth
        num_nodes = 2*num_leafs
        known = [False] * num_nodes
        decommitment = []
        for i in indices:
            known[2**depth + i] = True
        for i in range(2**depth - 1, 0, -1):
            left = known[2*i]
            right = known[2*i + 1]
            if left and not right:
                decommitment += [self.tree[2*i + 1]]
            if not left and right:
                decommitment += [self.tree[2*i]]
            known[i] = left or right
        return decommitment

    def verify(self, root, depth, values, decommitment, debug_print=False):
        '''Verify a set of leafs in the Merkle tree.
        
        Parameters
        ------------------------
        root
            Merkle root that is commited to.
        depth
            Depth of the Merkle tree. Equal to log2(number of leafs)
        values
            Mapping leaf index => value of the values we want to decommit.
        decommitments
            List of intermediate values required for deconstruction.
        '''
        
        # Create a list of pairs [(tree_index, leaf_hash)] with tree_index decreasing
        queue = []
        for index in sorted(values.keys(), reverse=True):
            tree_index = 2**depth + int(index)
            hash = self.hash_leaf(values[index])
            queue += [(tree_index, hash)]
        while True:
            assert(len(queue) >= 1)
    
            # Take the top from the queue
            (index, hash) = queue[0]
            queue = queue[1:]
            if debug_print:
                print(index, hash)
    
            # The merkle root has tree index 1
            if index == 1:
                return hash == root
            
            # Even nodes get merged with a decommitment hash on the right
            elif index % 2 == 0:
                queue += [(index // 2, self.hash_node(hash, decommitment[0]))]
                decommitment = decommitment[1:]
            
            # Odd nodes can get merged with their neighbour
            elif len(queue) > 0 and queue[0][0] == index - 1:
                    # Take the sibbling node from the stack
                    (_, sibbling_hash) = queue[0]
                    queue = queue[1:]
    
                    # Merge the two nodes
                    queue += [(index // 2, self.hash_node(sibbling_hash, hash))]
            
            # Remaining odd nodes are merged with a decommitment on the left
            else:
                # Merge with a decommitment hash on the left
                queue += [(index // 2, self.hash_node(decommitment[0], hash))]
                decommitment = decommitment[1:]


    def get_all_keys(self):
        return self.map_key_indices.keys()

    def get_indices_by_keys(self, keys):
        return list(self.map_key_indices[key] for key in keys)

    def get_key_indices_map(self):
        return self.map_key_indices

    def get_key_values_map(self):
        return self.map_key_values

    def build_from_file(self, logfile, record_num, use_key_from_file=False):
        LOG = open(logfile,"r").readlines()

        # build Merkle tree
        for i in range(record_num):
            record_items = LOG[i].strip('\n').split(' ')
            key = i 
            if use_key_from_file:
                key = record_items[2] 
            value = record_items[4] 
            value = self.hash_leaf(value)
            self.map_key_indices[key] = i 
            self.map_key_values[key] = value 
            self.leaves.append(value)

        self.make_tree()
        print('mkt length:', len(self.tree))

    def update_leaves(self, keys, values):
        for i in range(len(keys)):
            self.leaves[self.map_key_indices[keys[i]]] = Web3.soliditySha3(['string'], [values[i]]).hex()
        self.make_tree()
