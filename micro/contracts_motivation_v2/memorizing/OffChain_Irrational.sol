pragma solidity ^0.4.25;
pragma experimental ABIEncoderV2;

contract OnChain_Memorizing_Irrational{

    bytes32 root=0xc055e1dcf75e73ec3efb8c0535b465af6b154ff8ce9fd26de2c8c872b3e98909;
    mapping (uint256=>bytes32) record;
    mapping(uint256=>uint8) Valid;    // 1 -> invalid, 2-> valid, using integer instead of using boolean
    mapping (uint256=>uint8) RCounter;  // Read counter

    // on-chain read entry 
    function read(uint256 start, uint256 end) public payable {
        
        bytes32 rets;
        
        for (uint256 i=start; i<end; ++i){
            if(Valid[i] == 2){}
            
            // add read counter
            RCounter[i]++;
            rets = record[i];
        }
    }
    
    // off-chain read entry
    function read_offchain(uint256 start, bytes32[] memory values, uint16 replicateIndex, uint256[] memory indices, bytes32[] memory proof, uint8 depth) public payable {
           bytes32 rets;
        // authenticate the proof
        verify(root, depth, indices, values, proof);
        
        for(uint256 i=0; i<values.length; ++i){
             //prev: NR,   W*Y + K <= R cur: R
            RCounter[i+start] += 1;
            if ( Valid[i+start] != 2 && i < replicateIndex ){
                 record[i+start] = values[i];
                 Valid[i+start] = 2;
            }else{
                 // increment the counter
            }
            
            rets=values[i];
        }
    }
    
    // Write entry
    function write(uint256 start, uint256 end, uint256 offset, bytes32[] memory values, uint8[] memory counters, bytes32 digest) public {
        
        root = digest;
       
        // check the counters uploaded in read_offchain
        for (uint256 i=0; i<counters.length; ++i){
            if (counters[i+start] != RCounter[i+start]) {}
        }
       
        for (uint256 j=start; j<end; ++j){
            
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
    
    // Loading record to make the replication cost 5000 gas for each record 
    function loading(uint256 start, uint256 end) public {
        for (uint256 i=start; i<end; ++i){
            record[i] = 0xc055e1dcf75e73ec3efb8c0535b465af6b154ff8ce9fd26de2c8c872b3e98909;
            RCounter[i] = 1; // start from 1
            Valid[i] = 1;    // initialize to invalid
        }
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