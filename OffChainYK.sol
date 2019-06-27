pragma solidity ^0.5.9;
pragma experimental ABIEncoderV2;

contract GRuB_SS_OffChain_InSecure_YK{
    
    
    uint8 Y;
    uint8 K;
    
    bytes32 root_hash;
    mapping (string=>string) Replica;
    mapping (string=>bool) Valid;
    
    mapping (string=>uint8) OnChainReadCounter;
    mapping (string=>uint8) OffChainReadCounter;

    // On-chain read entry
    function read(string[110] memory keys) public payable returns(string[110] memory) {
        string[110] memory rets;
        
        for (uint8 i=0; i<keys.length; ++i){
            // increment the onchain counter
            OnChainReadCounter[keys[i]]++;
            rets[i] = Replica[keys[i]];
        }
        return rets;
    }
    
    // Off-chain read entry
    function read_offchain(string[110] memory keys, string[110] memory values, uint8[110] memory WC, bytes32[10] memory path) public payable returns(string[110] memory) {
        string[110] memory rets;

        for(uint8 i=0; i<keys.length; ++i){
            
            // increment the off-chain counter
            OffChainReadCounter[keys[i]]++;
            
            // authenticate the proof
            bytes32  computedHash;      
            for(uint8 j=0; j<path.length; ++j){
                computedHash = keccak256(abi.encodePacked(computedHash,path[j]));
            }
            
            if (root_hash != computedHash)
            {
                // report the invalid proof
                // emit event();
            }
            
            // prev: NR
            uint8 readcount = OnChainReadCounter[keys[i]] + OffChainReadCounter[keys[i]];
            if (WC[i] * Y + K <= readcount ) {
                // new: R
                Replica[keys[i]] = values[i];
                Valid[keys[i]] = true;
            }
            else{
                // new: NR
            }
                
            rets[i]=values[i];
        }
        
        return rets;
        // notify DU through event
        // emit event();
    }
    
    // Write entry
    function write(string[110] memory keys, string[110] memory values, bool[110] memory earlyDecision, uint8[110] memory RC, uint8[110] memory WC, bytes32 digest) public {
        root_hash = digest;
        
        for (uint8 i=0; i<keys.length; ++i){
            
            // verify the RC
            if (RC[i] != OnChainReadCounter[keys[i]]) { 
                // report the inconsistent off-chain counter
                // emit event();
            }

            // cur: R
            if (Valid[keys[i]]) {
                if (! earlyDecision[i]){
                    // earlyDecision is NR, must recheck
                    uint8 readcount = OnChainReadCounter[keys[i]] + RC[i];

                    if (WC[i] * Y > readcount + K) {
                        // new: NR
                        Valid[keys[i]] = false;
                    }else{
                        // new: R
                        Replica[keys[i]] = values[i];
                    }
                }else{
                    // earlyDecision is R, no need to check the condition
                    Replica[keys[i]] = values[i];
                }
            }else{
            // cur: NR    
                if ( !earlyDecision[i]) {
                    // earlyDecision is NR, must recheck
                    uint8 readcount = OnChainReadCounter[keys[i]] + RC[i];
                    if (WC[i] * Y + K <= readcount ) {
                        // new: R
                        Replica[keys[i]] = values[i];
                        Valid[keys[i]] = true;
                    }
                }else{
                    // new: R
                    Replica[keys[i]] = values[i];
                    Valid[keys[i]] = true;
                }
            }
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
            OnChainReadCounter[keys[i]] = 0;
            OffChainReadCounter[keys[i]] = 0;
        }
    }
}
