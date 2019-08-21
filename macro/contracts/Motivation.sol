pragma solidity ^0.4.25;
pragma experimental ABIEncoderV2;

contract Motivation{
    
    bytes32 root;
    mapping(uint256=>bytes32) record;
    
    // write range sorted objects 
    function write_onchain(uint256 start, uint256 end, bytes32[] memory values) public {
        for (uint256 i=start; i<end; ++i){
            record[i] = values[i-start];
        }
    }
    
    // read range sorted objects 
    function read_onchain(uint256 start, uint256 end) public payable {
        //bytes32[] memory rets = new bytes32[](keys.length);
        bytes32 ret;
        for (uint256 i=start; i<end; ++i){
            ret = record[i];
        }
    }
    
    // every 1000 data updates generate a digest
    function write_offchain(bytes32 digest) public{
        root = digest;
    }
    
    // read range sorted objects 
    function read_offchain(uint256 start, bytes32[] memory values, uint256[] memory indices, bytes32[] memory proof, uint8 depth) public payable {
        //bytes32[] memory rets = new bytes32[](values.length);
        bytes32 ret;
        
        verify(root, depth, indices, values, proof);
      
        for (uint256 i=0; i<values.length; ++i){
            // authenticate the proof
            ret = values[i];
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
