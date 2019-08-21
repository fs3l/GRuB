import hashlib
import binascii
from web3 import Web3

class MerkleTools(object):
    def __init__(self):
        self.reset_tree()

    def _to_hex(self, x):
        try:  # python3
            return x.hex()
        except:  # python2
            return binascii.hexlify(x)

    def reset_tree(self):
        self.leaves = list()
        self.levels = None
        self.is_ready = False
        self.map_key_indices={}
        self.map_key_values={}

    def recover_leaves(self, leaves):
        self.leaves = leaves
        self.make_tree()

    def hash_node(self, left, right):
        v = Web3.soliditySha3(['bytes32', 'bytes32'], [left, right])
        return v.hex()

    def hash_leaf(self, value):
        v = Web3.soliditySha3(['string'], [value])
        return v.hex()
 
    def hash_leaves(self, values):
        ret_values=[]
        for value in values:
            v = Web3.soliditySha3(['string'], [value])
            ret_values.append(v.hex())
        return ret_values

    def add_leaf(self, values, do_hash=True):
        self.is_ready = False
        # check if single leaf
        if not isinstance(values, tuple) and not isinstance(values, list):
            values = [values]
        for v in values:
            self.map_key_indices[v] = self.get_leaf_count() 
            self.map_key_values[v] = v 
            if do_hash:
                 v = Web3.soliditySha3(['string'], [v]).hex()
            self.leaves.append(v)

    def update_leaves(self, keys, values):
        for i in range(len(keys)):
            self.leaves[self.map_key_indices[keys[i]]] = Web3.soliditySha3(['string'], [values[i]]).hex()
        self.make_tree()

    def insert_leaves(self, keys, values):
        for i in range(len(keys)):
            if keys[i] not in map_key_indices:
                self.map_key_indices[keys[i]] = self.get_leaf_count()
                self.map_key_values[keys[i]] = self.hash_leaf(values[i])
                self.leaves.append(self.hash_leaf(values[i]))
        self.make_tree()

    def get_leaf(self, index):
        return self.leaves[index]
 
    def get_tree(self):
        nodes=[]
        for x in range(len(self.levels) - 1, 0, -1):
            level_len = len(self.levels[x])
            print('level:',x, 'len:',level_len)
            nodes += self.levels[x]
        return nodes

    def get_leaf_count(self):
        return len(self.leaves)

    def get_tree_ready_state(self):
        return self.is_ready

    def _calculate_next_level(self):
        solo_leave = None
        N = len(self.levels[0])  # number of leaves on the level
        if N % 2 == 1:  # if odd number of leaves on the level
            solo_leave = self.levels[0][-1]
            N -= 1

        new_level = []
        for l, r in zip(self.levels[0][0:N:2], self.levels[0][1:N:2]):
            new_level.append(self.hash_node(l,r))
        if solo_leave is not None:
            new_level.append(solo_leave)
        self.levels = [new_level, ] + self.levels  # prepend new level

    def make_tree(self):
        self.is_ready = False
        if self.get_leaf_count() > 0:
            self.levels = [self.leaves, ]
            while len(self.levels[0]) > 1:
                self._calculate_next_level()
        self.is_ready = True

    def get_all_keys(self):
        print(self.map_key_indices)
        return self.map_key_indices.keys()

    def get_indices_by_keys(self, keys):
        return list(self.map_key_indices[key] for key in keys)

    def get_key_indices_map(self):
        return self.map_key_indices

    def get_key_values_map(self):
        return self.map_key_values

    def get_depth(self):
        return len(self.levels)-1

    def get_root(self):
        if self.is_ready:
            if self.levels is not None:
                return self.levels[0][0]
            else:
                return None
        else:
            return None

    def get_proof(self, indices):
        if self.levels is None:
            return None
        else:
            lowest_level = len(self.levels)-1
            known={}
            known[lowest_level]={}
            for index in indices:
                known[lowest_level][index] = True
            proof = []
            for index in indices:
                if not self.is_ready or index > len(self.leaves)-1 or index < 0:
                    return None
                for x in range(len(self.levels) - 1, 0, -1):
                    level_len = len(self.levels[x])
                    if (index == level_len - 1) and (level_len % 2 == 1):  # skip if this is an odd end node
                        index = int(index / 2.)
                        continue
                    is_right_node = index % 2
                    sibling_index = index - 1 if is_right_node else index + 1
                    sibling_pos = "left" if is_right_node else "right"
                    sibling_value = self.levels[x][sibling_index]
                    proof.append(sibling_value)
                    index = int(index / 2.)

            proof = list(dict.fromkeys(proof))
            print('proof length:',len(proof))
            return proof

    def validate_proof(self, proof, target_hash, merkle_root):
        merkle_root = bytearray.fromhex(merkle_root)
        target_hash = bytearray.fromhex(target_hash)
        if len(proof) == 0:
            return target_hash == merkle_root
        else:
            proof_hash = target_hash
            for p in proof:
                try:
                    # the sibling is a left node
                    sibling = bytearray.fromhex(p['left'])
                    proof_hash = self.hash_function(sibling + proof_hash).digest()
                except:
                    # the sibling is a right node
                    sibling = bytearray.fromhex(p['right'])
                    proof_hash = self.hash_function(proof_hash + sibling).digest()
            return proof_hash == merkle_root

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
