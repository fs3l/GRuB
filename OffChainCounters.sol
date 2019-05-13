pragma solidity ^0.5.0;
pragma experimental ABIEncoderV2;

/*
  Store the counters off chain
  Algorithm:
    - DU issues a read request.
    - SP upload the record and attach the replication decision.
        - if it is replicate, store the record on-chain.
    - DO issues a write, to update the hash and invalidate the on-chain replica.
*/

contract offChainCounters{
    
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
    
    // SP uploads one record, and the replication decision;
    function upload(string memory key, string memory value, bool replicate) public {
        if (Digest[key] == keccak256(bytes(value)))
        {
            if (replicate){
                 Replica[key] = value;
                 IsLocal[key] = true;
            }else{
                 emit response(key,value);
            }
        }
    }
    
    // DO updates the digest of a data key, invalidate the local record
    function digest(string memory key, string memory value) public {
        Digest[key] = keccak256(bytes(value));
        IsLocal[key] = false;
    }
    
}
