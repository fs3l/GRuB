pragma solidity ^0.4.25;
pragma experimental ABIEncoderV2;

contract Always_Replicate{
    
    mapping (uint256=>bytes32) record;
    uint256 boundary=0;
     
    // on-chain range query
    function read(uint256 start, uint256 end) public payable {
        bytes32 rets;

        if (end >= start){
            for (uint256 i=start; i<=end; ++i){

                rets = record[i];
            }
        }else{
            for ( i=start; i<=boundary; ++i){
                rets = record[i];
            }
            
            for ( i=0; i<=end; ++i){
                rets = record[i];
            }
        }
    }
    
    // Write entry
    function write(uint256 start, uint256 end, bytes32[] memory values) public {
        for (uint256 i=start; i<end; ++i){
           record[i] = values[i-start];
        }
    }
    
    function write_1(uint256[] memory indices, bytes32[] memory values) public {
        
        for(uint256 i=0; i<indices.length; ++i){
           record[indices[i]] = values[i];
        }
    }
    
    // Loading record to make the replication write cost 5000 gas for each later write operation 
    function loading(uint256 start, uint256 end, uint256 max_range) public {
        for (uint256 i=start; i<=end; ++i){
            record[i] = 0xc055e1dcf75e73ec3efb8c0535b465af6b154ff8ce9fd26de2c8c872b3e98909;
        }
        
        boundary = max_range;
    }
}
