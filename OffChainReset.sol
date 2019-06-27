pragma solidity ^0.5.9;
pragma experimental ABIEncoderV2;

contract GRuB_SS_OffChain_Secure_Reset{
    
    int K=2; // replicate threshold
    
    bytes32 root_hash;
    mapping (string=>string) Replica;
    mapping (string=>bool) Valid;
    mapping (string=>uint8) RCounter;  // start from 0
    
    // On-chain read
    function read(string[110] memory keys) public payable returns(string[110] memory) {
        string[110] memory rets;
        
        for (uint8 i=0; i<keys.length; ++i){
                rets[i] = Replica[keys[i]];
        }
        return rets;
    }
    
    // Off-chain read
    function read_offchain(string[110] memory keys, string[110] memory values, bytes32[10] memory path) public payable returns(string[110] memory) {
        string[110] memory rets;

        for(uint8 i=0; i<keys.length; ++i){
            // authenticate the proof
            
            bytes32  computedHash;      
            for(uint8 j=0; j<path.length; ++j){
                computedHash = keccak256(abi.encodePacked(computedHash,path[j]));
            }
            
            if (root_hash == computedHash)
            {
                //here we do nothing, just to simulate the real-world cost through the if clause.
            }
            
            // NR -> R
            if ( RCounter[keys[i]] >= K ) {
                Replica[keys[i]] = values[i];
                Valid[keys[i]] = true;
            }
            else {
                // increment the counter
                RCounter[keys[i]] += 1;
            }
            rets[i]=values[i];
        }
        
        return rets;
        // notify DU through event
        // emit event()
    }
    
    /* optimization 1: 
       Instead of passing the previous decision from off-chain, we choose to read it from on-chain map Valid. 
       This can reduce gas cost and reduce the input size and further yield space to the other arguments,
       See GetDecision.sol for the experiment conclusion.
    */
    function write(string[110] memory keys, string[110] memory values, bool[110] memory cur, uint8[110] memory counters, bytes32 digest) public {
        root_hash = digest;
        
        for (uint8 i=0; i<keys.length; ++i){
            
            // compare the off-chain read counter with on-chain view, testing the correctness of decision
            if (counters[i] != RCounter[keys[i]]) { 
                // report the inconsistency of read counter 
            }

            // prev: R
            if (Valid[keys[i]]) {   
                // R -> R
                if (cur[i]){
                    Replica[keys[i]] = values[i];
                }else 
                {
                    // R -> NR
                    Valid[keys[i]] = false;
                }
            }else // prev: NR
            {
                if (cur[i]){
                    Replica[keys[i]] = values[i];
                    // NR -> R
                    Valid[keys[i]] = true;
                }
            }
            
            // reset the counter
            RCounter[keys[i]] = 0;
        }
    }
    
    function pre_write(string[110] memory keys, string[110] memory values, bytes32 digest) public {
        root_hash = digest;
        for (uint8 i=0; i<keys.length; ++i){
            Replica[keys[i]] = values[i];
            Valid[keys[i]] = false;
        }
    }
    
    function pre_set_counter(string[110] memory keys) public {
        for (uint8 i=0; i<keys.length; ++i){
            RCounter[keys[i]] = 0;
        }
    }
}
