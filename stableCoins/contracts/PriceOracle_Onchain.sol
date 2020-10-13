pragma solidity ^0.4.25;
pragma experimental ABIEncoderV2;

contract Onchain{
    
    mapping(uint256=>uint128) prices; // price of tokens

    // onchain query
    function read(uint256[] memory keys) public payable {
      uint128 ret;
      for (uint i=0; i<keys.length; ++i)
        ret = prices[keys[i]];
    }

    // off-chain point write
    function write(uint256[] memory keys, uint128[] values) public {
        for (uint256 i=0; i<keys.length; ++i){
            prices[keys[i]] = values[i];
        }
    }
    
    // initialize the storage
    function load(uint256[] memory keys) public {
        for (uint256 i=0; i<keys.length; ++i){
            prices[keys[i]] = 1;
        }
    }
}
