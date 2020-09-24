pragma solidity ^0.4.25;
pragma experimental ABIEncoderV2;

contract Secure_DB{
    
    bytes32 root=0xcf55e1dcf75e73ec3efb8c0535b465af6b154ff8ce9fd26de2c8c872b3e98909;
    mapping(uint256=>uint128) prices; // price of tokens
    mapping(uint256=>uint8) Valid;    // 1 -> invalid, 2-> valid, using integer to save cost
    
    // onchain query
    function read(uint256[] memory keys) public payable {
      uint128 ret;
      for (uint i=0; i<keys.length; ++i)
        ret = prices[keys[i]];
    }

    // off-chain point query
    function read(uint256 key, uint128[] memory values, bool R, uint256[] memory indices, bytes32[] memory proof, uint8 depth) public payable {
	    uint128 ret;
	    // authenticate the proof
	    if (indices.length > 0){
		    verify(root, depth, indices, values, proof);
	    }

	    if (values.length>=1){
		    if (R){
			    prices[key] = values[0];
			    if (Valid[key] == 1)
				    Valid[key] = 2;
		    }
	    }

	    else{
		    // record onchain
		    ret = prices[key];
	    }
    }
    
    // off-chain point write
    function write(uint256[] memory keys, bytes32 digest) public {
        root = digest;
        for (uint256 i=0; i<keys.length; ++i){
            if (Valid[keys[i]] == 2){
                Valid[keys[i]] = 1;
            }
        }
    }
    
    // initialize the storage
    function load(uint256[] memory keys) public {
        for (uint256 i=0; i<keys.length; ++i){
            Valid[keys[i]] = 1;
            prices[keys[i]] = 1;
        }
    }
    
    // if no on-chain record needs to be invalidated
    function update_digest(bytes32 digest) public {
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
}
