#! /usr/bin/python3.6

import json,sys
import web3

from web3 import Web3
from solc import compile_source
from web3.contract import ConciseContract

class PrivateSmartContract(object):
    def __init__(self, account_index):
        self.get_web3_instance(account_index)

    def get_web3_instance(self, account_index):
        self.rpcUrl = "http://127.0.0.1:8545"
        # web3.py instance
        self.w3 = Web3(Web3.HTTPProvider(self.rpcUrl))

        # set ropsten funded account as sender
        self.w3.eth.defaultAccount = self.w3.eth.accounts[account_index]
        #self.w3.eth.personal.unlockAccount(self.w3.eth.defaultAccount, '', 1000000000)
        self.account_index = account_index

    def getTransactionReceipt(self, tx_id):
        return self.w3.eth.getTransactionReceipt(tx_id)

    def deploy_smart_contract(self, source_code_file):
        w3 = self.w3
        contract_address_file = source_code_file.split('.sol')[0] + '.address' + str(self.account_index)

        with open(source_code_file, 'r') as source_code:
            contract_source_code = source_code.read()

        contract_name = contract_source_code.strip('\n').split('{')[0].split('contract ')[1].strip('\n')
        print ('deploying '+ contract_name + '...')

        compiled_sol = compile_source(contract_source_code) # Compiled source code
        contract_interface = compiled_sol['<stdin>:'+contract_name]

        # Instantiate and deploy contract
        Greeter = w3.eth.contract(abi=contract_interface['abi'], bytecode=contract_interface['bin'])

        # Submit the transaction that deploys the contract
        tx_hash = Greeter.constructor().transact()

        # Wait for the transaction to be mined, and get the transaction receipt
        tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
        print ('deployed contract address:' + tx_receipt.contractAddress)

        with open(contract_address_file, 'w') as caf:
            caf.write(tx_receipt.contractAddress)

    def log_parser(self, function_name, tx_receipt, length):
        if function_name == 'balance':
            ret=[]
            if len(tx_receipt['logs']) > 0:
                for i in range(length):
                    #print(tx_receipt['logs'][i])
                    log_data = tx_receipt['logs'][i]['data']
                    user = log_data[2:66]
                    balance = log_data[66:130]
                    ret.append(int(balance,16))
            return ret 

    def set_callback_address(self, source_code_file):
        contract_address_file = source_code_file.split('.sol')[0] + '.address' + str(self.account_index)
        # Get the contract address from local file
        with open(contract_address_file, 'r') as caf:
            contract_address = caf.read() 
   
        print('app callback address:', contract_address)       
        self.send_transactions('GRuB_Range_Query', 6, [contract_address], 0, 'set callback address')

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

    def call_GRuB_Range_Query(self, function_index, arguments):
        # function index: 0 -> loading, 1 -> write, 2 -> read_offchain, 3 -> read, 4 -> write_1
        w3 = self.w3

        if function_index == 0: # loading                                                                                  
            print ('calling loading ....') 
            return self.contractInstance.functions.loading(*arguments).transact()
                                                                                                                            
        elif function_index == 1: # write
            print ('calling write ....') 
            return self.contractInstance.functions.write(*arguments).transact()                                                                                                                             
        elif function_index == 2: # read_offchain 
            print ('calling read ....') 
            return self.contractInstance.functions.read(*arguments).transact()

        elif function_index == 3: # read_onchain 
            print ('calling read_onchain ....') 
            return self.contractInstance.functions.read(*arguments).transact()

        elif function_index == 4: # write_1
            print ('calling write_1 ....') 
            return self.contractInstance.functions.write_1(*arguments).transact()                                                                                                                             
        elif function_index == 7: # write_1
            print ('calling write_1 ....') 
            return self.contractInstance.functions.insert_1(*arguments).transact()                                                                                                                             
        elif function_index == 5: # write_1
            print ('calling update_digest ....') 
            return self.contractInstance.functions.update_digest(*arguments).transact()                                                                                                                             
        elif function_index == 6: # write_1
            print ('calling set_callback_address ....') 
            return self.contractInstance.functions.set_callback_address(*arguments).transact()                                                                                                                             

    def call_Motivation_Range_Query(self, function_index, arguments):
        # function index: 0 -> write_onchain, 1 -> read_onchain, 2 -> write_offchain 3 -> read_offchain
        w3 = self.w3

        if function_index == 0: # write_onchain                                                                                  
            print ('calling write_onchain ....') 
            return self.contractInstance.functions.write_onchain(*arguments).transact()
                                                                                                                            
        elif function_index == 1: # read_onchain 
            print ('calling read_onchain ....') 
            return self.contractInstance.functions.read_onchain(*arguments).transact()                                                                                                                             

        elif function_index == 2: # write_offchain 
            print ('calling write_offchain ....') 
            return self.contractInstance.functions.write_offchain(*arguments).transact()

        elif function_index == 3: # read_offchain 
            print ('calling read_offchain ....') 
            return self.contractInstance.functions.read_offchain(*arguments).transact()

    def send_transactions(self, contract_name, function_index, arguments, batchSize, RW='default', waitInclusion=False):
        w3 = self.w3

        if contract_name == 'GRuB_Range_Query':  
            tx_hash = self.call_GRuB_Range_Query(function_index, arguments)
        elif contract_name == 'Motivation':  
            tx_hash = self.call_Motivation_Range_Query(function_index, arguments)

        # Wait for transaction to be mined...
        print("tx",tx_hash.hex())
        #print(receipt)
        with open(self.txLogFile, 'a') as TXLOG: 
            try:
                if waitInclusion:
                    w3.eth.waitForTransactionReceipt(tx_hash, 20*60)
                    receipt = w3.eth.getTransactionReceipt(tx_hash)
                    print ('blockNumber:', receipt['blockNumber'], 'gasUsed:', receipt['gasUsed'])
                # write to the log file
                    TXLOG.write(tx_hash.hex() + '\t' + str(receipt['blockNumber'])  + '\t' + str(receipt['gasUsed']) + '\t' +str(batchSize) +'\t' + RW + '\r\n')
                else:
                    TXLOG.write(tx_hash.hex() + '\t\t\t'+ str(batchSize) + '\t' + RW + '\n') 
            except:
                print (receipt)
                TXLOG.write(tx_hash.hex() + '\t\t\t'+ str(batchSize) + '\t' + RW + '\tERR\n')
            TXLOG.flush()
