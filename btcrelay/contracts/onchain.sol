/*
Copyright (c) <2020> <Kai Li, Yuzhe Tang, Zhehu Yuan>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
*/

pragma solidity ^0.4.25;
pragma experimental ABIEncoderV2;

contract BL1 {
    
    mapping(uint256 => bytes32) btcblocks;

    // onchain query
    function read(uint256[] memory indices) public payable {
      bytes32 ret;
      for (uint i=0; i<indices.length; ++i)
        ret = btcblocks[indices[i]];
    }

    // write 
    function write(uint256[] memory indices, bytes32[] memory values) public {
        for (uint i=0; i<indices.length; ++i){
              btcblocks[indices[i]] = values[i];
        }
    }

    // load 
    function load(uint256[] memory indices) public {
        for (uint i=0; i<indices.length; ++i){
              btcblocks[indices[i]] = 0xcf55e1dcf75e73ec3efb8c0535b465af6b154ff8ce9fd26de2c8c872b3e98909;
        }
    }
}
