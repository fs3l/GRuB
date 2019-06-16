pragma solidity ^0.5.0;
pragma experimental ABIEncoderV2;

contract GRuB_SS_OffChain{
    
    bytes32 root_hash;
    mapping (string=>string) Replica;
    mapping (string=>bool) Valid;
    
    
    // prev: R, R -> R
    function read(string[142] memory keys) public payable returns(string[142] memory) {
        string[142] memory rets;
        
        for (uint8 i=0; i<keys.length; ++i){
                rets[i] = Replica[keys[i]];
        }
        return rets;
    }
    
    // prev: NR
    function read_offchain(string[142] memory keys, string[142] memory values, bool[142] memory cur,  bytes32[10] memory path) public payable returns(string[142] memory) {
        string[142] memory rets;

        for(uint8 i=0; i<values.length; ++i){
            // authenticate the proof
            bytes32  computedHash;      
            for(uint8 j=0; j<path.length; ++j){
                computedHash = keccak256(abi.encodePacked(computedHash, path[j]));
            }
            
            if (root_hash == computedHash)
            {
                //here we do nothing, just to simulate the real-world cost through the if clause.
            }
            
            // NR -> R
            if (cur[i]) {
                Replica[keys[i]] = values[i];
                Valid[keys[i]] = true;
            }
            // NR -> NR, do nothing
            else{
                
            }
            rets[i]=values[i];
        }
        return rets;
        // notify DU through event
        // emit event()
    }
    
    /* optimization 1: 
       Instead of passing the previous decision from off-chain, we choose to read it from on-chain map Valid. This can reduce gas cost, 
       and reduce the input size and further yield space to the other arguments.
       See GetDecision.sol for the experiment conclusion.
     */
    function write(string[] memory keys, string[] memory values, bool[] memory cur, bytes32 digest) public {
        root_hash = digest;
        
        for (uint8 i=0; i<keys.length; ++i){
            // prev: R
            if (Valid[keys[i]]) {
                
                // R -> R, replicate
                if (cur[i]) {
                    Replica[keys[i]] = values[i];
                }
                // R -> NR, invalidate old version
                else{
                    Valid[keys[i]] = false;
                }
            }
            // prev: NR,  NR -> NR, do nothing
            else{
            }
        }
    }
    
    function pre_write(string[142] memory keys, string[142] memory values, bytes32 digest) public {
     
        root_hash = digest;
        for (uint8 i=0; i<keys.length; ++i){
            Replica[keys[i]] = values[i];
            Valid[keys[i]] = true;
        }
    }
}
