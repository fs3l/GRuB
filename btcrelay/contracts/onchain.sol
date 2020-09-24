pragma solidity ^0.4.25;
pragma experimental ABIEncoderV2;

contract BL1 {
    
    mapping(uint256 => bytes32) btcblocks;

    // onchain query
    function read(uint256[] memory indices) public payable {
      bytes32 ret;
      for (uint i=0; i<indices.length; ++i)
        ret = btcblocks[indices[i]];
    }

    // write 
    function write(uint256[] memory indices, bytes32[] memory values) public {
        for (uint i=0; i<indices.length; ++i){
              btcblocks[indices[i]] = values[i];
        }
    }

    // load 
    function load(uint256[] memory indices) public {
        for (uint i=0; i<indices.length; ++i){
              btcblocks[indices[i]] = 0xcf55e1dcf75e73ec3efb8c0535b465af6b154ff8ce9fd26de2c8c872b3e98909;
        }
    }
}
