pragma solidity ^0.4.25;
pragma experimental ABIEncoderV2;

contract OnChain_Memorizing{
    
    uint8 K=3;
    uint8 D=1;

    bytes32 root=0xc055e1dcf75e73ec3efb8c0535b465af6b154ff8ce9fd26de2c8c872b3e98909;
    mapping (uint256=>bytes32) record;
    mapping (uint256=>uint8) Valid;
    
    mapping (uint256=>uint8) RCounter;  // Read counter
    mapping (uint256=>uint8) WCounter;  // Write counter

    // on-chain read entry 
    function read(uint256 start, uint256 end) public payable {
        
        bytes32 rets;
        
        for (uint256 i=start; i<end; ++i){
            
            if(Valid[i] == 2){}

            // add read counter
            RCounter[i]++;

            rets = record[i];
        }
    }
    
    // off-chain read entry
    function read_offchain(uint256 offset, bytes32[] memory values, uint256[] memory indices, bytes32[] memory proof, uint8 depth) public payable {
           bytes32 rets;
        // authenticate the proof
        verify(root, depth, indices, values, proof);
        
        for(uint256 i=0; i<values.length; ++i){
            // increment the counter
            RCounter[i+offset] += 1;
            
            //prev: NR,   W*Y + K <= R cur: R
            if ( Valid[i+offset] != 2 && K*WCounter[i+offset] + D <= RCounter[i+offset] ){
                 record[i+offset] = values[i];
                 Valid[i+offset] = 2;
            }
            
            rets=values[i];
        }
    }
    
    // Write entry
    function write(uint256 start, uint256 end, bytes32[] memory values, bytes32 digest) public {
        
        
        for (uint256 i=start; i<end; ++i){
            
            // increment write counter
            WCounter[i]++;
            
            // W*Y - K > R,  cur: NR
            if (K*WCounter[i]> RCounter[i] + D ) {
                if (Valid[i] != 1) 
                     Valid[i] = 1;
            }
            // then W*Y+K <= R, cur: R
            else{
                record[i] = values[i];
            }
        }
        root = digest;
    }
    
     // Loading record to make the replication cost 5000 gas for each record 
    function loading(uint256 start, uint256 end) public {
        for (uint256 i=start; i<end; ++i){
            record[i] = 0xc055e1dcf75e73ec3efb8c0535b465af6b154ff8ce9fd26de2c8c872b3e98909;
            RCounter[i] = 1;
            WCounter[i] = 1;
            Valid[i] = 1;
        }
    }
    
    //// reference to https://gist.github.com/Recmo/0dbbaa26c051bea517cd3a8f1de3560a
    function hash_leaf(bytes32 value)
        internal pure
        returns (bytes32 hash)
    {
        return keccak256(abi.encodePacked(value));
    }

    function hash_node(bytes32 left, bytes32 right)
        internal
        returns (bytes32 hash)
    {
        assembly {
            mstore(0x00, left)
            mstore(0x20, right)
            hash := keccak256(0x00, 0x40)
        }
        return hash;
    }
    
    function verify(bytes32 root, uint8 depth, uint256[] memory indices, bytes32[] memory values,
        bytes32[] memory proof
    ) 
    internal returns(bool) 
    {
        computedHash = hash_leaf(values[0]);
        for (uint16 i=1; i<values.length; ++i){
            bytes32 computedHash=hash_node(computedHash, hash_leaf(values[i]));
        }
        
        for (uint16 j=0; j<proof.length; ++j){
            computedHash = hash_node(computedHash, proof[j]);
        }
        return root == computedHash;
    }
}
