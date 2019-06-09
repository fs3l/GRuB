pragma solidity ^0.5.0;
pragma experimental ABIEncoderV2;

contract GRuB_SS_OffChain{
    
    bytes32 root_hash;
    mapping (string=>string) Replica;
    mapping (string=>bool) Valid;
    
    
    // prev: R, R -> R
    function read(string[] memory keys) public payable returns(string[] memory) {
        string[] memory rets = new string[](keys.length);
        
        for (uint8 i=0; i<keys.length; ++i){
                rets[i] = Replica[keys[i]];
        }
        return rets;
    }
    
    // prev: NR
    function read_offchain(string[] memory keys, string[] memory values, bool[] memory cur,  bytes32[] memory path) public {
        for(uint8 i=0; i<keys.length; ++i){
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
        }
        
        // notify DU through event
        // emit event()
    }
    
    function write(string[] memory keys, string[] memory values, bool[] memory prev, bool[] memory cur, bytes32 digest) public {
        root_hash = digest;
        
        for (uint8 i=0; i<keys.length; ++i){
            // prev: R
            if (prev[i]) {
                
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
}
