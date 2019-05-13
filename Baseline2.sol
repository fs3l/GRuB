pragma solidity ^0.5.0;
pragma experimental ABIEncoderV2;

/*
  Baseline 2: No replication 
    Protocol:
    - DO updates the on-chain digest.
    - DU issues a read request
    - SP uploads the record, SS verifies it through the on-chain digest.
*/


contract noReplicate{
    
    mapping (string=>bytes32) Digest;
    event response(string, string);
    event request(string);
    
    // DU issues a read
    function get(string memory key) public {
        emit request(key); 
    }
    
    // SP uploads one record
    function upload(string memory key, string memory value) public {
        if (Digest[key] == keccak256(bytes(value)))
        {
             emit response(key, value);
        }
    }
    
    // DO updates the digest of a data key
    function digest(string memory key, string memory value) public {
        Digest[key] = keccak256(bytes(value));
    }
}
