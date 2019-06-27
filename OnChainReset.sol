pragma solidity ^0.5.0;
pragma experimental ABIEncoderV2;

contract GRuB_SS_OnChain_Reset{
    
    int8 K = 2;  // replicate threshold  

    bytes32 root_hash;
    mapping (string=>string) Replica;
    mapping (string=>bool) Valid;
    mapping (string=>int8) Counters;
    
    // Read entry 
    function read(string[164] memory keys) public payable returns(string[164] memory) {
        
        string[164] memory rets;
        
        for (uint8 i=0; i<keys.length; ++i){
            // cur: R
            if (Valid[keys[i]]) {
                rets[i] = Replica[keys[i]];
            }
            // cur: NR
            else{
                Counters[keys[i]]++;
                // notify SP through event
                // emit event(); 
            }
        }
        return rets;
    }
    
    // Read off-chain entry
    function read_offchain(string[164] memory keys, string[164] memory values, bytes32[10] memory path) public payable returns(string[164] memory
) {
        string[164] memory rets;

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
    
    // Write entry
    function write(string[164] memory keys, string[164] memory values, bytes32 digest) public {
        
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
                
                
            }// prev: NR
            else{
                 
            }
            // reset the counter
            Counters[keys[i]] = 0;
        }
    }
    
    function pre_write(string[164] memory keys, string[164] memory values, bytes32 digest) public {
        root_hash = digest;
        for (uint8 i=0; i<keys.length; ++i){
            Counters[keys[i]] = 0;
            Replica[keys[i]]=values[i];
            Valid[keys[i]] = false;
        }
    }
}
