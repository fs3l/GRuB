pragma solidity ^0.4.25;
pragma experimental ABIEncoderV2;

/*
 Memoryless version
*/
contract Motivation_OnChain_Reset{
    
    uint16 K = 3;  // replicate threshold  
 
    bytes32 root=0xc055e1dcf75e73ec3efb8c0535b465af6b154ff8ce9fd26de2c8c872b3e98909;

    mapping (uint256=>bytes32) record;
    mapping (uint256=>bool) Valid;
    mapping (uint256=>uint8) RCounter;
    
    // set K
    function setK(uint16 k) public {
        K = k;
    }
    
    // Read entry, SP knows the on-chain replica
    function read(uint256 start, uint256 end) public payable {
        bytes32 rets;
        for (uint256 i=start; i<end; ++i){
            if(Valid[i]){}
            rets = record[i];
        }
    }
    
    // Offchain read entry, SP knows the on-chain replica
    function read_offchain(uint256 offset, bytes32[] memory values, uint256[] memory indices, bytes32[] memory proof, uint8 depth) public payable {
        
        bytes32 rets;
        // authenticate the proof
        verify(root, depth, indices, values, proof);
        
        
        for(uint256 i=0; i<values.length; ++i){

            // NR -> R
            if ( !Valid[i+offset] && RCounter[i+offset] >= K ) {
                record[i+offset] = values[i];
                Valid[i+offset] = true;
            }else{
                 // increment the counter
                 RCounter[i+offset] += 1;
            }
            
            rets=values[i];
        }
    }
    
    // No replication for any write
   function write(uint256 start, uint256 end, bytes32 digest) public {
        for (uint256 i=start; i<end; ++i){
            if (Valid[i]){
                Valid[i] = false;
            }
            
            // reset the counter
            if (RCounter[i] > 1){
                RCounter[i] = 1;
            }
        }
        root = digest;
    }
    
    // Loading record to make the replication cost 5000 gas per record 
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
