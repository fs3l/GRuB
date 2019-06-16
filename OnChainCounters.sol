pragma solidity ^0.5.0;
pragma experimental ABIEncoderV2;

contract GRuB_SS_OnChain{
    
    int8 K = 4;  // upperbound of counter to replication  
    int8 X = 1;  // decrement of counter by an update to an object
    
    bytes32 root_hash;
    mapping (string=>string) Replica;
    mapping (string=>bool) Valid;
    mapping (string=>int8) Counters;
    
    // DU sends batched reads
    function read(string[142] memory keys) public payable returns(string[142] memory) {
        
        string[142] memory rets;
        
        for (uint8 i=0; i<keys.length; ++i){
            // prev: R
            if (Valid[keys[i]]) {
                rets[i] = Replica[keys[i]];
                Counters[keys[i]]++;
            }
            // prev: NR
            else{
                Counters[keys[i]]++;
                // notify SP through event
                // emit event(); 
            }
        }
        return rets;
    }
    
    // SP uploads the requested objects, SS will replicates the record according to the current counter value
    function read_offchain(string[142] memory keys, string[142] memory values, bytes32[10] memory path) public payable returns(string[142] memory
) {
        string[142] memory rets;

        for(uint8 i=0; i<keys.length; ++i){
            // authenticate the proof
            bytes32  computedHash;      
            for(uint8 j=0; j<path.length; ++j){
                computedHash = keccak256(abi.encodePacked(computedHash, path[j]));
            }
            
            if (root_hash == computedHash)
            {
              // here we do nothing, just to simulate the real-world cost through if clause.
            }
            
            //  replicate the records
            if (Counters[keys[i]] >= K){
                 Replica[keys[i]] = values[i];
                 Valid[keys[i]] = true;
            }
            
            rets[i] = values[i];
        }
        
        // notify DU through event
        // emit event()
    }
    
    // DO call write() to submit the latest digest, SS will store the latest digest and invalidates part of the on-chain replicas. 
    function write(string[142] memory keys, string[142] memory values, bytes32 digest) public {
        
        root_hash = digest;
        
        for (uint8 i=0; i<keys.length; ++i){
            // prev: R
            if (Valid[keys[i]]) {
                 
                 // cur: R, R -> R
                if (Counters[keys[i]] >= K) {
                    Replica[keys[i]] = values[i];
                }// cur: NR, R -> NR
                else{
                    Valid[keys[i]] = false;
                }
                // decrease by X
                Counters[keys[i]] -= X;
                
            }// prev: NR, NR -> NR
            else{
                  if (Counters[keys[i]] >= X) {
                      Counters[keys[i]] -= X;
                  }else{
                      Counters[keys[i]] = 0;
                }
            }
        }
    }
    
    function pre_write(string[142] memory keys, string[142] memory values, bytes32 digest) public {
        root_hash = digest;
        for (uint8 i=0; i<keys.length; ++i){
            Counters[keys[i]] = 0;
            Replica[keys[i]]=values[i];
            Valid[keys[i]] = false;
        }
    }
}
