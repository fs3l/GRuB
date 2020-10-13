#! /usr/bin/python3.6

import json,sys
import web3

from web3 import Web3
from solc import compile_source
from web3.contract import ConciseContract

class PublicSmartContract(object):
    def __init__(self, account_index=0):
        self.get_web3_instance(account_index)
    
    def get_web3_instance(self, account_index):

        self.account_index = account_index
        accounts=['0x6bD1BaeeBD9708Eda2baA7aeecc52c8Efe03d217','0xDC9D8f57ED23E73D22C3AFb220A10c546AAfD024', '0x07576ddE1C9d9a2C264203aDa8c82Ccfe542982E', '0x6A40431d6DcC1CB63aE2cb83d677e9f4b95C097b', '0x27467D269860C6005f59C18c0e125FB573C6f6F5', '0xC974C3b50eA5C2403d41fD220a8B32771a5b478f', '0x0a7C56DD0A122342B76Ec1A20b35116748A4154c','0x5ea8FaC179ef9cbD626BBef21248CD1EFbFd33dB','0x1d47dB0B01C9E3A1c5b815a5aEeEc0319aD7513f']
        private_keys = ['FC357FC6C4B435A27F2FA1FB228122822B1641A94090BC1CE2981A3787881AA2','27AA669EEADA2B0DC54930F3247D95DDE380164F2EE088FEB1B381978B0473C5','BB0704A3ACDB89E3EDD273F7ACD1BD087C3B0D50E81F5667D44A2AD7C38FE8B5', 'D30383966BB6019FEA6680693F0B33A0E3187626D0607E3196C2EE01BCBD4D57', 'B17171E82ADC8F8ED0799D615667BFA933ED49771563E16E388EDBC1355D5CCE', 'C54A502C8A37FB453F50CB3E2F4AB3D125FA37C13F80CE98A3F8C34796DCBEAC','A730CC7904473F64D420873B7FA541859B22C84C672F59D5FB2F34E0454C5722','A17599AE97EDF65D5B34A3EAB0E6584363781541ADBBD587C02EAED83A683ADA','9364C895E631946AB86D3DD9D07DECDE8EEF7C1EDED998AFD168CD03D2601C6E']

        self.rpcUrl = "https://ropsten.infura.io/v3/64ddf5ce86494601b3f47ab4c4638d36"
        # web3.py instance
        self.w3 = Web3(Web3.HTTPProvider(self.rpcUrl))
        
        # set ropsten funded account as sender
        self.chainid = 3   # 1 for mainnet, 2 for kovan, 3 for ropsten
        self.w3.eth.defaultAccount = accounts[account_index] 
        self.private_key = private_keys[account_index] 
        
    def getTransactionReceipt(self, tx_id):
        return self.w3.eth.getTransactionReceipt(tx_id)

    def deploy_smart_contract(self, source_code_file):
        w3 = self.w3
        contract_address_file = source_code_file.split('.sol')[0] + '.address' + str(self.account_index)

        with open(source_code_file, 'r') as source_code:
            contract_source_code = source_code.read()

        nonce = w3.eth.getTransactionCount(w3.eth.defaultAccount, 'pending')

        contract_name = contract_source_code.strip('\n').split('{')[0].split('contract ')[1].strip('\n') 
        print ('deploying '+ contract_name + '...')

        compiled_sol = compile_source(contract_source_code) # Compiled source code
        contract_interface = compiled_sol['<stdin>:'+contract_name]

        # Instantiate and deploy contract
        Greeter = w3.eth.contract(abi=contract_interface['abi'], bytecode=contract_interface['bin'])

        # Submit the transaction that deploys the contract
        transaction = Greeter.constructor().buildTransaction({
            'from': w3.eth.defaultAccount,
            'nonce': nonce,
            'gas': 2000000,
            'chainId': 3, 
            'gasPrice': w3.toWei('2', 'gwei')})
        
        # Sign the transaction with the private key
        signed = w3.eth.account.signTransaction(transaction, self.private_key)
        tx_hash = w3.eth.sendRawTransaction(signed.rawTransaction) 

        # Wait for the transaction to be mined, and get the transaction receipt
        tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash, 30*60)
        print ('deployed contract address:' + tx_receipt.contractAddress)
        
        with open(contract_address_file, 'w') as caf:
            caf.write(tx_receipt.contractAddress)

    def get_contract_instance(self, source_code_file, txLogFile):
    
        # Get the deployed contract address 
        contract_address_file = source_code_file.split('.sol')[0] + '.address' + str(self.account_index)
        
        with open(source_code_file, 'r') as source_code:
            contract_source_code = source_code.read()
        
        contract_name = contract_source_code.strip('\n').split('{')[0].split('contract ')[1].strip('\n') 

        # Compiled source code
        compiled_sol = compile_source(contract_source_code) 
        
        contract_interface = compiled_sol['<stdin>:'+contract_name]
        
        # Instantiate deployed contract
        self.contract = self.w3.eth.contract(abi=contract_interface['abi'], bytecode=contract_interface['bin'])
        
        # Get the contract address from local file
        with open(contract_address_file, 'r') as caf:
            contract_address = caf.read()
        caf.close()
        source_code.close()
        print ('contract address:', contract_address)
        
        # Create the contract instance at the deployed address
        self.contractInstance = self.w3.eth.contract(
            address=contract_address,
            abi=contract_interface['abi'],
        )

        # Set the log file for recording the transactions
        self.txLogFile = txLogFile


    def sign_send_transactions(self, batchSize, RW):
        w3 = self.w3

        # Sign the transaction with the private key
        signed = w3.eth.account.signTransaction(self.transaction, self.private_key)
        tx_hash = w3.eth.sendRawTransaction(signed.rawTransaction)
        print ('tx Hash:', tx_hash.hex())
        
        # Wait for transaction to be mined...
        w3.eth.waitForTransactionReceipt(tx_hash, 30*60)
        receipt = w3.eth.getTransactionReceipt(tx_hash)

        TXLOG = open(self.txLogFile, 'a')

        if str(type(receipt)).split('\'')[1] == 'web3.datastructures.AttributeDict':
            print ('blockNumber:', receipt['blockNumber'], 'gasUsed:', receipt['gasUsed'])
            # write to the log file
            TXLOG.write(tx_hash.hex() + '\t' + str(receipt['blockNumber'])  + '\t' + str(receipt['gasUsed']) + '\t' +str(batchSize) + '\t'+ RW + '\n')
        else:
            TXLOG.write(tx_hash.hex() + '\t\t\t'+ str(batchSize) + '\t' + RW + '\n')

        TXLOG.close()

    def call_GRuB_Offchain_Reset_Insecure(self, function_index, arguments):
        # function index: 1 -> pre_write, 2 -> write, 3 -> read_offchain, 4 -> read
        w3 = self.w3
        nonce = w3.eth.getTransactionCount(w3.eth.defaultAccount, 'pending')

        if function_index == 1: # pre_write                                                                                  
            print ('calling pre_write ....') 
            digest = arguments[0]
                                                                                                                             
            self.transaction = self.contractInstance.functions.pre_write(digest).buildTransaction({
                'from': w3.eth.defaultAccount,
                'nonce': nonce,
                'chainId': self.chainid, 
                'gasPrice': w3.toWei('3', 'gwei')})
                                                                                                                             
        elif function_index == 2: # write
            print ('calling write ....') 
            keys = arguments[0]
            values = arguments[1]
            lastReplicateIndex = arguments[2]
            digest = arguments[3]
                                                                                                                             
            self.transaction = self.contractInstance.functions.write(keys, values, lastReplicateIndex, digest).buildTransaction({
                                'from': w3.eth.defaultAccount,
                                'nonce': nonce,
                                'chainId': self.chainid, 
                                'gasPrice': w3.toWei('3', 'gwei')})
                                                                                                                             
        elif function_index == 3: # read_offchain 
            if len(arguments[0]) == 0:
                return

            print ('calling read_offchain ....') 
            keys = arguments[0]
            values = arguments[1]
            lastRepicateIndex = arguments[2]
            indices = arguments[3]
            proofs = arguments[4]
            depth = arguments[5]
                                                                                                                             
            self.transaction = self.contractInstance.functions.read_offchain(keys, values, lastRepicateIndex, indices, proofs, depth).buildTransaction({
                                'from': w3.eth.defaultAccount,
                                'nonce': nonce,
                                'chainId': self.chainid, 
                                'gasPrice': w3.toWei('3', 'gwei')})

        elif function_index == 4: # read_onchain 
            if len(arguments[0]) == 0:
                return

            print ('calling read ....') 
            keys = arguments[0]

            self.transaction = self.contractInstance.functions.read(keys).buildTransaction({
                                'from': w3.eth.defaultAccount,
                                'nonce': nonce,
                                'chainId': self.chainid, 
                                'gasPrice': w3.toWei('3', 'gwei')})
            
    def call_GRuB_SS_OnChain_Reset(self, function_index, arguments):
        # function index: 1 -> pre_write, 2 -> write, 3 -> read_offchain, 4 -> read
        w3 = self.w3
        nonce = w3.eth.getTransactionCount(w3.eth.defaultAccount, 'pending')

        if function_index == 1: # pre_write                                                                                  
            print ('calling pre_write ....') 
            digest = arguments[0]
                                                                                                                             
            self.transaction = self.contractInstance.functions.pre_write(digest).buildTransaction({
                'from': w3.eth.defaultAccount,
                'nonce': nonce,
                'chainId': self.chainid, 
                'gasPrice': w3.toWei('3', 'gwei')})
                                                                                                                             
        elif function_index == 2: # write
            print ('calling write ....') 
            keys = arguments[0]
            values = arguments[1]
            digest = arguments[2]
                                                                                                                             
            self.transaction = self.contractInstance.functions.write(keys, values, digest).buildTransaction({
                                'from': w3.eth.defaultAccount,
                                'nonce': nonce,
                                'chainId': self.chainid, 
                                'gasPrice': w3.toWei('3', 'gwei')})
                                                                                                                             
        elif function_index == 3: # read_offchain 
            if len(arguments[0]) == 0:
                return

            print ('calling read_offchain ....') 
            keys = arguments[0]
            values = arguments[1]
            indices = arguments[2]
            proofs = arguments[3]
            depth = arguments[4]
                                                                                                                             
            self.transaction = self.contractInstance.functions.read_offchain(keys, values, indices, proofs, depth).buildTransaction({
                                'from': w3.eth.defaultAccount,
                                'nonce': nonce,
                                'chainId': self.chainid, 
                                'gasPrice': w3.toWei('3', 'gwei')})

        elif function_index == 4: # read_onchain 
            if len(arguments[0]) == 0:
                return

            print ('calling read ....') 
            keys = arguments[0]

            self.transaction = self.contractInstance.functions.read(keys).buildTransaction({
                                'from': w3.eth.defaultAccount,
                                'nonce': nonce,
                                'chainId': self.chainid, 
                                'gasPrice': w3.toWei('3', 'gwei')})
         
    def call_GRuB_SS_Always_OffChain(self, function_index, arguments):
        # function index: 1 -> pre_write, 2 -> write, 3 -> read_offchain, 4 -> read
        w3 = self.w3
        nonce = w3.eth.getTransactionCount(w3.eth.defaultAccount, 'pending')

        if function_index == 1: # write
            print ('calling write ....') 
            self.transaction = self.contractInstance.functions.write(*arguments).buildTransaction({
                                'from': w3.eth.defaultAccount,
                                'nonce': nonce,
                                'chainId': self.chainid, 
                                'gasPrice': w3.toWei('3', 'gwei')})
                                                                                                                             
        elif function_index == 2: # read_offchain 
            print ('calling read_offchain ....') 
            self.transaction = self.contractInstance.functions.read_offchain(*arguments).buildTransaction({
                                'from': w3.eth.defaultAccount,
                                'nonce': nonce,
                                'chainId': self.chainid, 
                                'gasPrice': w3.toWei('3', 'gwei')})
         
    def call_GRuB_SS_Always_OnChain(self, function_index, arguments):
        # function index: 1 -> pre_write, 2 -> write, 3 -> read_offchain, 4 -> read
        w3 = self.w3
        nonce = w3.eth.getTransactionCount(w3.eth.defaultAccount, 'pending')

        if function_index == 1: # write
            print ('calling write ....') 
            self.transaction = self.contractInstance.functions.write(*arguments).buildTransaction({
                                'from': w3.eth.defaultAccount,
                                'nonce': nonce,
                                'chainId': self.chainid, 
                                'gasPrice': w3.toWei('3', 'gwei')})
                                                                                                                             
        elif function_index == 2: # read 
            print ('calling read ....') 
            self.transaction = self.contractInstance.functions.read(*arguments).buildTransaction({
                                'from': w3.eth.defaultAccount,
                                'nonce': nonce,
                                'chainId': self.chainid, 
                                'gasPrice': w3.toWei('3', 'gwei')})

    def call_Motivation(self, function_index, arguments):
        # function index: 1 -> write_onchain, 2 -> read_onchain, 3 -> write_offchain, 4 -> read_offchain

        w3 = self.w3
        nonce = w3.eth.getTransactionCount(w3.eth.defaultAccount, 'pending')

        if function_index == 1: # write_onchain
            print ('calling on-chain write ....') 
            self.transaction = self.contractInstance.functions.write_onchain(*arguments).buildTransaction({
                                'from': w3.eth.defaultAccount,
                                'nonce': nonce,
                                'chainId': self.chainid, 
                                'gasPrice': w3.toWei('3', 'gwei')})
                                                                                                                             
        elif function_index == 2: # read_onchain 
            print ('calling on-chain read ....') 
            self.transaction = self.contractInstance.functions.read_onchain(*arguments).buildTransaction({
                                'from': w3.eth.defaultAccount,
                                'nonce': nonce,
                                'chainId': self.chainid, 
                                'gasPrice': w3.toWei('3', 'gwei')})

        elif function_index == 3: # write_offchain 
            print ('calling off-chain write ....') 
            self.transaction = self.contractInstance.functions.write_offchain(*arguments).buildTransaction({
                                'from': w3.eth.defaultAccount,
                                'nonce': nonce,
                                'chainId': self.chainid, 
                                'gasPrice': w3.toWei('3', 'gwei')})

        elif function_index == 4: # write_offchain 
            print ('calling off-chain read ....') 
            self.transaction = self.contractInstance.functions.read_offchain(*arguments).buildTransaction({
                                'from': w3.eth.defaultAccount,
                                'nonce': nonce,
                                'chainId': self.chainid, 
                                'gasPrice': w3.toWei('3', 'gwei')})

    def call_Memoryless(self, function_index, arguments):
        # function index: 0 -> loading, 1 -> write, 2 -> read_onchain, 3 -> read_offchain
        w3 = self.w3
        nonce = w3.eth.getTransactionCount(w3.eth.defaultAccount, 'pending')

        if function_index == 0: # loading
            print ('calling loading ....') 
            self.transaction = self.contractInstance.functions.loading(*arguments).buildTransaction({
                                'from': w3.eth.defaultAccount,
                                'nonce': nonce,
                                'chainId': self.chainid, 
                                'gasPrice': w3.toWei('3', 'gwei')})
                                                        
        elif function_index == 1: # write
            print ('calling write ....') 
            self.transaction = self.contractInstance.functions.write(*arguments).buildTransaction({
                                'from': w3.eth.defaultAccount,
                                'nonce': nonce,
                                'chainId': self.chainid, 
                                'gasPrice': w3.toWei('3', 'gwei')})
                                                                                                                             
        elif function_index == 2: # read_onchain 
            print ('calling on-chain read ....') 
            self.transaction = self.contractInstance.functions.read(*arguments).buildTransaction({
                                'from': w3.eth.defaultAccount,
                                'nonce': nonce,
                                'chainId': self.chainid, 
                                'gasPrice': w3.toWei('3', 'gwei')})

        elif function_index == 3: # read_offchain 
            print ('calling off-chain read ....') 
            self.transaction = self.contractInstance.functions.read_offchain(*arguments).buildTransaction({
                                'from': w3.eth.defaultAccount,
                                'nonce': nonce,
                                'chainId': self.chainid, 
                                'gasPrice': w3.toWei('3', 'gwei')})

    def send_transactions(self, contract_name, function_index, arguments, batchSize, RW):

        if contract_name == 'GRuB_SS_OffChain_Insecure_Reset':  
            self.call_GRuB_Offchain_Reset_Insecure(function_index, arguments)
        elif contract_name == 'GRuB_SS_OnChain_Reset':  
            self.call_GRuB_SS_OnChain_Reset(function_index, arguments)
        elif contract_name == 'GRuB_SS_Always_OffChain':  
            self.call_GRuB_SS_Always_OffChain(function_index, arguments)
        elif contract_name == 'GRuB_SS_Always_OnChain':  
            self.call_GRuB_SS_Always_OnChain(function_index, arguments)
        elif contract_name == 'Motivation':  
            self.call_Motivation(function_index, arguments)
        elif contract_name == 'Memoryless' or contract_name == 'Memorizing':  
            self.call_Memoryless(function_index, arguments)

        self.sign_send_transactions(batchSize, RW) 

'''            
# Test a non-payable function
print('calling read(): {}'.format(
    greeter.functions.read(['1','2']).call()
))
'''

'''
# When issuing a lot of reads, try this more concise reader:
reader = ConciseContract(greeter)
assert reader.greet() == "Nihao"
'''
