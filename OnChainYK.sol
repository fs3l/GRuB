pragma solidity ^0.5.0;
pragma experimental ABIEncoderV2;

contract GRuB_SS_OnChain_YK{
    
    int8 T = 2;  // replication threshold  
    int Y;
    int K;

    bytes32 root_hash;
    mapping (string=>string) Replica;
    mapping (string=>bool) Valid;
    
    mapping (string=>int8) RCounters;  // Read counter
    mapping (string=>int8) WCounters;  // Write counter

    
    // Read entry 
    function read(string[164] memory keys) public payable returns(string[164] memory) {
        
        string[164] memory rets;
        
        for (uint8 i=0; i<keys.length; ++i){
            
            // increment read counter
            RCounters[keys[i]]++;

            // cur: R
            if (Valid[keys[i]]) {
                rets[i] = Replica[keys[i]];
            }
            // cur: NR
            else{
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
            
            if (root_hash != computedHash)
            {
              // report the illegitimate proof
              // emit event
            }
            
            // prev: R, cur must be R
            if (Valid[keys[i]]) {
                Replica[keys[i]] = values[i];
            }
            // prev: NR,   W*Y + K <= R cur: R
            else if ( WCounters[keys[i]] + K <= RCounters[keys[i]] ){
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
            
            // increment write counter
            WCounters[keys[i]]++;
            
            // prev: R
            if (Valid[keys[i]]) {
                 
                 // W*Y - K > R,  cur: NR
                if (WCounters[keys[i]] - K > RCounters[keys[i]] ) {
                    Valid[keys[i]] = false;
                    
                }
                // then W*Y+K <= R, cur: R
                else{
                    Replica[keys[i]] = values[i];
                }
            }
            
            // prev: NR, then cur must be NR
            else{
                 
            }
        }
    }
    
    function pre_write(string[164] memory keys, string[164] memory values, bytes32 digest) public {
        root_hash = digest;
        for (uint8 i=0; i<keys.length; ++i){
            RCounters[keys[i]] = 0;
            WCounters[keys[i]] = 0;

            Replica[keys[i]]=values[i];
            Valid[keys[i]] = false;
        }
    }
}
