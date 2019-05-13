pragma solidity ^0.5.0;
pragma experimental ABIEncoderV2;

/*
  Baseline 3: Always replication 
  Protocol:
    - DO updates the on-chain digest, to invalidate the local replica.
    - DU issues a read request, if the local replica exist, read from the replica.
    - SP uploads the record, SS verifies it through the on-chain digest and replicate the record
    
*/

contract alwaysReplicate{
    
    mapping (string=>bytes32) Digest;
    mapping (string=>string) Replica;
    mapping (string=>bool) IsLocal;
    
    event response(string, string);
    event request(string);
    
    // DU issues a read
    function get(string memory key) public returns(string memory) {
        if (IsLocal[key]) {
            string memory res = Replica[key];
            return res;
        }else{
            emit request(key); 
        }
    }
    
    // SP uploads one record, replicate the record;
    function upload(string memory key, string memory value) public {
        if (Digest[key] == keccak256(bytes(value)))
        {
             Replica[key] = value;
             IsLocal[key] = true;
        }
    }
    
    // DO updates the digest of a data key, invalidate the local record
    function digest(string memory key, string memory value) public {
        Digest[key] = keccak256(bytes(value));
        IsLocal[key] = false;
    }
}
