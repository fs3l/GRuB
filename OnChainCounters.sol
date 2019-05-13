pragma solidity ^0.5.0;
pragma experimental ABIEncoderV2;

/*
  Store the counters on chain
    Protocol:
    - DO updates the on-chain digest, and decreases the counter by X.
    - DU issues a read request, and increase the counter by 1.
    - SP uploads the record, SS verifies it through the on-chain digest and 
      take replication action according the counter value;
    - Replication action:
      The upper bound of counter to trigger the replication action is K.
*/

contract onChainCounters{
    
    uint8 K = 3;  // upper bound
    uint8 X = 1;  // decrements
    
    mapping (string=>bytes32) Digest;
    mapping (string=>string) Replica;
    mapping (string=>bool) IsLocal;
    mapping (string=>uint8) Counters;
    
    event response(string, string);
    event request(string);
    
    // DU issues a read
    function get(string memory key) public returns(string memory) {
        if (IsLocal[key]) {
            string memory res = Replica[key];
            return res;
        }else{
            Counters[key]++;
            emit request(key); 
        }
    }
    
    // SP uploads one record, replicate the record;
    function upload(string memory key, string memory value) public {
        if (Digest[key] == keccak256(bytes(value)))
        {
            if (Counters[key] >= K){
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
        
        Counters[key] = Counters[key]>=X?Counters[key]-X:0;
    }
    
    function getCounter(string memory key) view public returns(uint8, bool) {
        return (Counters[key], IsLocal[key]);
    }
}
