pragma solidity ^0.5.0;
pragma experimental ABIEncoderV2;


contract Motivation{
    
    bytes32 root;
    mapping(string=>string) record;
    
    function write_onChain(string[168] memory keys, string[168] memory values) public {
        for (uint8 i=0; i<keys.length; ++i){
            record[keys[i]] = values[i];
        }
    }
    
    function write_offChain(bytes32 digest) public{
        root = digest;
    }
    
    function read_onchain(string[168] memory keys) public payable returns(string[168] memory) {
        string[168] memory rets;
        for (uint8 i=0; i<keys.length; ++i){
            rets[i] = record[keys[i]];
        }
        return rets;
    }
    
    function read_offchain(string[168] memory keys, string[168] memory values, bytes32[10] memory proof) public payable returns(string[168] memory) {
        string[168] memory rets;
        
        for (uint8 i=0; i<values.length; ++i){
            
            bytes32 computedHash;        
            for(uint8 j=0; j<proof.length; ++j){
                computedHash = keccak256(abi.encodePacked(computedHash, proof[j]));
            }
            
            rets[i] = values[i];
        }
        
        return rets;
    }
}

