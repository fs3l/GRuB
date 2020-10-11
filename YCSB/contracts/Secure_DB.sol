pragma solidity ^0.4.25;
pragma experimental ABIEncoderV2;

contract Secure_DB{
    
    bytes32 root=0xc055e1dcf75e73ec3efb8c0535b465af6b154ff8ce9fd26de2c8c872b3e98909;
    mapping(uint256=>bytes32) record;
    mapping(uint256=>uint8) Valid;    // 1 -> invalid, 2-> valid, using integer instead of using boolean
    uint256 boundary=0;

    // on-chain range query
    function read(uint256 start, uint256 end) public payable {
        bytes32 rets;

        if (end >= start){
            for (uint256 i=start; i<=end; ++i){
                if(Valid[i] == 2){}

                rets = record[i];
            }
        }else{
            for ( i=start; i<boundary; ++i){
                if(Valid[i] == 2){}
                rets = record[i];
            }
            
            for ( i=0; i<=end; ++i){
                if(Valid[i] == 2){}
                rets = record[i];
            }
        }
    }
    
    // Off-chain range query
    function read(uint256 start, uint256 end, bytes32[] memory values, uint16 replicateIndex, uint256[] memory indices, bytes32[] memory proof, uint8 depth) public payable {
        
        bytes32 rets;
        
        // authenticate the proof
        if (indices.length > 0){
            verify(root, depth, indices, values, proof);
        }
       
        uint256 next = 0;
        if (end >= start){
            for (uint256 i=start; i<=end; ++i){
                if(Valid[i] == 2){
                    // read on-chain replica 
                    rets = record[i];
                }else{
                    // read off-chain data
                    if (next < values.length){
                        rets = values[next];
                        if (next < replicateIndex && Valid[i] != 2){
                           record[i] = rets;
                           Valid[i] = 2;
                        }
                        next++;
                    }
                }
            }
        }else{
            
            //[start, boundary]
            for (i=start; i<= boundary; ++i){
                if (Valid[i] == 2){
                    rets = record[i];
                }else{
                    if (next < values.length){
                        rets = values[next];
                        next++;
                        if (next < replicateIndex && Valid[i] != 2){
                           record[i] = rets;
                           Valid[i] = 2;
                        }
                    }
                }
            }
            
            // [0, end]
            for (i=0; i<= end; ++i){
                if (Valid[i] == 2){
                    rets = record[i];
                }else{
                    if (next < values.length){
                        rets = values[next];
                        next++;
                        if (next < replicateIndex && Valid[i] != 2){
                           record[i] = rets;
                           Valid[i] = 2;
                        }
                    }
                }
            }
        }
    }
    
    // Update the digest on-chain, all values shall be replicated, need to tell the offset of values in the range [start, end]
    function write(uint256 start, uint256 end, uint256 offset, bytes32[] memory values, bytes32 digest) public {
        
        root = digest;
        
        for (uint256 j=start; j<=end; ++j){
            
            if ( j < offset){
                 // R -> NR
                if (Valid[j+offset] == 2){
                    Valid[j+offset] = 1;
                }
            }else{
                  if (j >= offset && values.length > 0 && j-offset < values.length ){ 
                       record[j] = values[j-offset];
 
                       if (Valid[j+offset] != 2){
                           Valid[j+offset] = 2;
                       }
                  }
                  else {
                       if (Valid[j+offset] != 1){
                           Valid[j+offset] = 1;
                       }
                 } 
            }
        }
    }
    
    // Requirements: indices are sorted from replicate to non-relicate.
    function write_1(uint256[] memory indices, bytes32[] memory values, uint256 replicateIndex, bytes32 digest) public {
        root = digest;
        
        for(uint256 i=0; i<indices.length; ++i){
            
            if (i < replicateIndex){
                record[indices[i]] = values[i];
                if (Valid[indices[i]] != 2){
                    Valid[indices[i]] =2;
                }
            }else{
               if (Valid[indices[i]] != 1){
                    Valid[indices[i]] = 1;
                }
            }
        }
    }

    // Insert a range
    function insert(uint256 start, uint256 end, bytes32[] memory values, bytes32 digest) public {
        
        root = digest;
        if ( start > boundary) {
           for (uint256 j=start; j<=end; ++j){
               record[j] = values[j-start];
               Valid[j] = 1; 
           }
           if (end > boundary)
               boundary = end; 
        }
    }

    // Insert a range
    function insert_1(bytes32 digest) public {
        root = digest;
    }
    
    // function index 6
    function update_digest(bytes32 digest) public {
        root = digest;
    }
    
    // Loading record to make the replication write cost 5000 gas for each record 
    function loading(uint256 start, uint256 end, uint256 max_range) public {
        for (uint256 i=start; i<=end; ++i){
            record[i] = 0xc055e1dcf75e73ec3efb8c0535b465af6b154ff8ce9fd26de2c8c872b3e98909;
            Valid[i] = 1;
        }
        
        boundary = max_range;
    }
    
    //// reference to https://gist.github.com/Recmo/0dbbaa26c051bea517cd3a8f1de3560a
    function hash_leaf(bytes32 value)
        internal pure
        returns (bytes32 hash)
    {
        return keccak256(abi.encodePacked(value));
    }

    function hash_node(bytes32 left, bytes32 right)
        internal
        returns (bytes32 hash)
    {
        assembly {
            mstore(0x00, left)
            mstore(0x20, right)
            hash := keccak256(0x00, 0x40)
        }
        return hash;
    }
    
    function verify(bytes32 root, uint8 depth, uint256[] memory indices, bytes32[] memory values,
        bytes32[] memory proof
    ) 
    internal returns(bool) 
    {
        computedHash = hash_leaf(values[0]);
        for (uint16 i=1; i<values.length; ++i){
            bytes32 computedHash=hash_node(computedHash, hash_leaf(values[i]));
        }
        
        for (uint16 j=0; j<proof.length; ++j){
            computedHash = hash_node(computedHash, proof[j]);
        }
        return root == computedHash;
    }
    
}
