#! /usr/bin/python3.6

import hashlib
import math
from sha3 import keccak_256

def hash_leaf(leaf_value):
    '''Convert a leaf value to a digest'''
    #assert(leaf_value < 2**256)
    #return leaf_value.to_bytes(32, 'big')
    leaf_value = leaf_value.encode('utf-8')
    leaf_value = keccak_256(leaf_value).hexdigest()
    return leaf_value

def hash_node(left_hash, right_hash):
    '''Convert two digests to their Merkle node's digest'''
    return keccak_256((left_hash + right_hash).encode('utf-8')).hexdigest()

def make_tree(leafs):
    '''Compute the Merkle tree of a list of values.
    The result is returned as a list where each value represents one hash in the
    tree. The indices in the array are as in a bbinary heap array.
    '''
    num_leafs = len(leafs)
    depth = int(math.log(num_leafs,2))
    assert(num_leafs == 2**depth)
    num_nodes = 2 * num_leafs
    tree = [None] * num_nodes
    for i in range(num_leafs):
        #tree[2**depth + i] = hash_leaf(leafs[i])
        tree[2**depth + i] = leafs[i]
    for i in range(2**depth - 1, 0, -1):
        tree[i] = hash_node(tree[2*i], tree[2*i + 1])
    return tree

def update_tree(leafs, indices, values):

    for i in range(len(values)):
        leafs[indices[i]] = values[i]
    tree = make_tree(leafs)
    return tree,leafs

def getRoot(tree):
    return tree[1]

def getDepth(tree):
    return int(math.log(len(tree),2)) - 1 

def getProof(tree, indices):
    '''Given a Merkle tree and a set of indices, provide a list of decommitments
    required to reconstruct the merkle root.'''
    depth = int(math.log(len(tree),2)) - 1
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
            decommitment += [tree[2*i + 1]]
        if not left and right:
            decommitment += [tree[2*i]]
        known[i] = left or right
    return decommitment

def verify(root, depth, values, decommitment, debug_print=False):
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
        hash = hash_leaf(values[index])
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
            queue += [(index // 2, hash_node(hash, decommitment[0]))]
            decommitment = decommitment[1:]
        
        # Odd nodes can get merged with their neighbour
        elif len(queue) > 0 and queue[0][0] == index - 1:
                # Take the sibbling node from the stack
                (_, sibbling_hash) = queue[0]
                queue = queue[1:]

                # Merge the two nodes
                queue += [(index // 2, hash_node(sibbling_hash, hash))]
        
        # Remaining odd nodes are merged with a decommitment on the left
        else:
            # Merge with a decommitment hash on the left
            queue += [(index // 2, hash_node(decommitment[0], hash))]
            decommitment = decommitment[1:]
