pragma solidity ^0.4.25;
pragma experimental ABIEncoderV2;

contract BL2{
    
    bytes32 root=0xcf55e1dcf75e73ec3efb8c0535b465af6b154ff8ce9fd26de2c8c872b3e98909;
   
    function write(bytes32 digest) public{
        root = digest;
    }
   
    function read_offchain(uint256 key, uint128[] memory values, uint256[] memory indices, bytes32[] memory proof, uint8 depth) public payable {
        // authenticate the proof
        verify(root, depth, indices, values, proof);
        uint128 ret = values[0];
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
    
    function verify(bytes32 root, uint8 depth, uint256[] memory indices, uint128[] memory values,
        bytes32[] memory proof
    ) 
    internal returns(bool) 
    {
        bytes32 computedHash = hash_leaf(bytes32(values[0]));
        for (uint16 i=1; i<values.length; ++i){
	    uint256 index = indices[i];
            computedHash=hash_node(computedHash, hash_leaf(bytes32(values[i])));
        }
        
        for (uint16 j=0; j<proof.length; ++j){
            computedHash = hash_node(computedHash, proof[j]);
        }
        return root == computedHash;
    }

    function verify_nomerge(bytes32 root, bytes32[] memory values,
        bytes32[] memory proof, uint256 depth 
    ) 
    internal returns(bool) 
    {
        bool pass = true;
        bytes32 computedHash = 0x0;
        for (uint16 i=0; i<values.length; ++i){
            for (uint16 j=0; j<depth; ++j){
                computedHash = hash_node(computedHash, proof[i*depth+j]);
	        }
	        if (computedHash != root){
		        pass = false;	
	        }
        }
        return pass;
    }
}
