pragma solidity ^0.4.25;
pragma experimental ABIEncoderV2;

contract PriceFeed {
    bytes32 root=0xcf55e1dcf75e73ec3efb8c0535b465af6b154ff8ce9fd26de2c8c872b3e98909;
    mapping(uint256=>uint128) prices; // prices of tokens, stored by hybrid storage
    mapping(uint256=>uint8) Valid;    // 1 -> invalid, 2-> valid, using integer to save cost

    // from price feeder
    function gPut(uint256[] memory keys, bytes32 digest) public {
        root = digest;
        for (uint256 i=0; i<keys.length; ++i){
            if (Valid[keys[i]] == 2){
                Valid[keys[i]] = 1;
            }
        }
    }
   
    // peek from StableCoin
    function gGet1(uint256 marketID) public returns(uint128){
        return prices[marketID];
    }
    
    // peek from StableCoin
    function gGet(uint256 marketID, uint128[] memory values, bool R, uint256[] memory indices, bytes32[] memory proof, uint8 depth) public returns (bool) {
        if (indices.length > 0){
            verify(root, depth, indices, values, proof);
        }
        
        if (R){
            prices[marketID] = values[0];
            if (Valid[marketID] == 1)
                Valid[marketID] = 2;
        }
        
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
   
    function issue(uint256 assetID, uint128[] price, bool R, uint256[] indices, bytes32[] proof, uint8 depth) external payable {
        uint256 firstPlace = (msg.value * 2) /3;
        if(PriceFeed.gGet(assetID, price, R, indices, proof, depth)){
            Balance[assetID][msg.sender] += firstPlace * price[0];
            Collaterals[msg.sender].secondPlace += msg.value-firstPlace;
            Collaterals[msg.sender].issuedPrice = price[0];
        }
    }
   
    function issue(uint256 assetID) external payable {
        uint256 firstPlace = (msg.value * 2) / 3;
        uint128 price =PriceFeed.gGet1(assetID);
        Balance[assetID][msg.sender] += firstPlace * price;
        Collaterals[msg.sender].secondPlace += msg.value-firstPlace;
        Collaterals[msg.sender].issuedPrice = price;
    }

    function redeem(uint256 assetID) {
       uint128 price =PriceFeed.gGet1(assetID);
        if ( (Collaterals[msg.sender].issuedPrice * 2)/3 > price){
            // under-collateraled
            liquidation();
        }else{
            //safe position
            uint256 firstPlace = Balance[assetID][msg.sender] / price;
            uint256 refunds = firstPlace + Collaterals[msg.sender].secondPlace;
         	if (msg.sender.send(refunds)) {
                Balance[assetID][msg.sender]=0;
         	} 
        }
    }

    function redeem(uint256 assetID, uint128[] memory price, bool R,  uint256[] memory indices, bytes32[] memory proof, uint8 depth){
        if (PriceFeed.gGet(assetID, price, R, indices, proof, depth)){
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

    // initalize the prices to be non-zero value 
    function load(uint256[] memory marketID) public {
        for (uint i=0; i<marketID.length; ++i){
                prices[marketID[i]] = 1;
                Balance[marketID[i]][msg.sender]=10000000000000000000000000000;
                Collaterals[msg.sender].secondPlace=1;
                Collaterals[msg.sender].issuedPrice=1;
        }
    }

    // TODO
    function liquidation() public {
    }
}
