pragma solidity ^0.4.25;
pragma experimental ABIEncoderV2;

/*
 Memorizing version
*/

contract Never_Replicate{
    
    bytes32 root=0xc055e1dcf75e73ec3efb8c0535b465af6b154ff8ce9fd26de2c8c872b3e98909;

    // off-chain range query
    function read(uint256 start, bytes32[] memory values, uint256[] memory indices, bytes32[] memory proof, uint8 depth) public payable {
        
        bytes32 rets;
        // authenticate the proof
        verify(root, depth, indices, values, proof);

       
        for(uint256 i=0;  i<values.length; ++i){
            rets=values[i];
        }
    }
    
    // update the digest on-chain
    function write( bytes32 digest) public {
        root = digest;
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
