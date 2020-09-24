pragma solidity ^0.4.25;
pragma experimental ABIEncoderV2;

contract PriceFeed {
    bytes32 root=0xcf55e1dcf75e73ec3efb8c0535b465af6b154ff8ce9fd26de2c8c872b3e98909;

    // from price feeder
    function gPut(bytes32 digest) public{
        root = digest;
    }
   
    function gGet(uint256 marketID, uint128[] memory values, uint256[] memory indices, bytes32[] memory proof, uint8 depth) public returns (bool) {
        // authenticate the proof
        verify(root, depth, indices, values, proof);
        return true;
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
    
    function verify(bytes32 root, uint8 depth, uint256[] memory indices, uint128[] memory values,
        bytes32[] memory proof
    ) 
    internal returns(bool) 
    {
        bytes32 computedHash = hash_leaf(bytes32(values[0]));
        for (uint16 i=1; i<values.length; ++i){
	    uint256 index = indices[i];
            computedHash=hash_node(computedHash, hash_leaf(bytes32(values[i])));
        }
        
        for (uint16 j=0; j<proof.length; ++j){
            computedHash = hash_node(computedHash, proof[j]);
        }
        return root == computedHash;
    }
}

contract SCoin is PriceFeed {
    
    struct collateral {
       uint256 secondPlace;
       uint128 issuedPrice;
    }
    
    mapping(uint256=>mapping(address=>uint256)) Balance;
    mapping(address=>collateral) Collaterals;
   
    function issue(uint256 assetID, uint128[] price, uint256[] indices, bytes32[] proof, uint8 depth ) external payable {
        uint256 firstPlace = (msg.value * 2) /3;
        if(PriceFeed.gGet(assetID, price, indices, proof, depth)){
            Balance[assetID][msg.sender] += firstPlace * price[0];
            Collaterals[msg.sender].secondPlace += msg.value-firstPlace;
            Collaterals[msg.sender].issuedPrice = price[0];
        }
    }


    function redeem(uint256 assetID, uint128[] memory price, uint256[] memory indices, bytes32[] memory proof, uint8 depth){
        if (PriceFeed.gGet(assetID, price, indices, proof, depth)){
            if ((Collaterals[msg.sender].issuedPrice * 2)/3 > price[0]){
                // under-collateraled
                liquidation();
            }else{
                //safe position
                uint256 firstPlace = Balance[assetID][msg.sender] / price[0];
                uint256 refunds = firstPlace + Collaterals[msg.sender].secondPlace;
         	    if (msg.sender.send(refunds)) {
                  Balance[assetID][msg.sender]=0;
         	    } 
            }
        }
    }

    // initalize the records to make later updates cost 5000 gas
    function load(uint256[] memory marketID) public {
        for (uint i=0; i<marketID.length; ++i){
                Balance[marketID[i]][msg.sender]=1000000000000000000000000;
                Collaterals[msg.sender].secondPlace=1;
                Collaterals[msg.sender].issuedPrice=1;
        }
    }

    // TODO
    function liquidation() public {
    }
}
