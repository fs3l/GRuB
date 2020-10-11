pragma solidity ^0.4.25;
pragma experimental ABIEncoderV2;

/*
 Memoryless version
*/

contract Motivation_Offchain_Irrational{
    
    bytes32 root=0xc055e1dcf75e73ec3efb8c0535b465af6b154ff8ce9fd26de2c8c872b3e98909;

    mapping(uint256=>bytes32) record;
    mapping(uint256=>bool) Valid;
    mapping(uint256=>uint8) RCounter;  // start from 1 to reduce the high cost from zero -> non-zero
    
    // Read entry, off-chain SP knows the on-chain replica
    function read(uint256 start, uint256 end) public payable {
        bytes32 rets;
        for (uint256 i=start; i<end; ++i){
            if(Valid[i]){}
            rets = record[i];
        }
    }
    
    function read_offchain(uint256 offset, bytes32[] memory values, uint16 replicateIndex, uint256[] memory indices, bytes32[] memory proof, uint8 depth) public payable {
        
        
        bytes32 rets;
        // authenticate the proof
        verify(root, depth, indices, values, proof);

        for(uint256 i=0; i<values.length; ++i){
                
            // NR -> R
            if ( !Valid[i+offset] && i < replicateIndex ) {
                record[i+offset] = values[i];
                Valid[i+offset] = true;
            }else{
                // increment the counter
                RCounter[i+offset] += 1;
            }
            
            rets =values[i];
        }
    }
    
    // No replication for any write
    function write(uint256 start, uint256 end, uint256 offset, uint8[] memory counters, bytes32 digest) public {
        
        // check the counters uploaded in read_offchain
        for (uint256 i=0; i<counters.length; ++i){
            if (counters[i+offset] != RCounter[i+offset]) {}
           
        }
        
        for (uint256 j=start; j<end; ++j){
            // R -> NR
            if (Valid[j]){
                Valid[j] = false;
            }
            
            // reset the counter
            if ( RCounter[j] > 1) {
                 RCounter[j] = 1;
            }
        }
        
        root = digest;
    }
    
    // Loading record to make the replication cost 5000 gas for each record 
    function loading(uint256 start, uint256 end) public {
        for (uint256 i=start; i<end; ++i){
            record[i] = 0xc055e1dcf75e73ec3efb8c0535b465af6b154ff8ce9fd26de2c8c872b3e98909;
            RCounter[i] = 1;
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
