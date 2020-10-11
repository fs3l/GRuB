#! /usr/bin/python3.6
import sys
sys.path.insert(0, "./lib")
from memoryless import MemorylessState 
from utils import process, process_scan, order_by_decision, trim_by_decision
from public_bkc import PublicSmartContract
from private_bkc import PrivateSmartContract
from pymerkletools import MerkleTools 

class GRuB(object):
    def __init__(self, logfile, app_type, account_index=0, K=2):
        self.K = K
        self.mt = MerkleTools()
        self.onChainState = MemorylessState()
        #self.SC = PublicSmartContract(account_index)
        self.SC = PrivateSmartContract(account_index)
        self.TXLogFile = logfile + '_' + app_type +'_'+ str(K) 
        self.Contract_type = 'GRuB_Range_Query'
        if app_type == 'CT':
            self.SC.get_contract_instance('./contracts/CT/GRuB_CT.sol', self.TXLogFile)
            self.SC.set_callback_address('./contracts/CT/App_CT.sol') 
        elif app_type == 'Token':
            self.SC.get_contract_instance('./contracts/token/GRuB_Token.sol', self.TXLogFile)
            self.SC.set_callback_address('./contracts/token/App_Token.sol') 
        else:
            print('Unsupported application')
            sys.exit()

    # Interface for CT clients
    def signature_verify(self, ct):
        #TODO
        return True

    def CT_log_update(self, domain_names, certs, w_index=0):
        for ct in certs:
            self.signature_verify(ct)
        self.Puts(domain_names, certs, w_index)

    def CT_log_read(self, domain_names, conditions):
        self.GetQ(domain_names, conditions) 

    # Interface for Token 
    def DO_transfer(self, senders, receivers, tokens, transfer_index = 0):
        uniq_senders = list(dict.fromkeys(senders))
        uniq_receivers = list(dict.fromkeys(receivers))
        balances = self.SC.log_parser('balance', self.GetQ(uniq_senders, ''), len(uniq_senders))
        balances = {} 
        for key in uniq_senders: 
            balances[key] = self.mt.get_values(key) 
        for key in uniq_receivers: 
            balances[key] = self.mt.get_values(key) 
            
        print(balances)
        for sender in senders:
            balance = balances[sender]
            token = tokens[senders.index(sender)]
            while (balance < token ):
                print('Insufficient balance:', balance, 'transfering amount:', token, 'from:', sender, 'to:', receivers[senders.index(sender)])
                balances[sender] += token
                balance = balances[sender]
                #sys.exit(0) 
            balances[sender] -= token
            balances[receivers[senders.index(sender)]] += token
               
        return self.TokenPuts(senders, receivers, tokens, transfer_index)

    def DU_balanceOf(self, owners):
        return self.SC.log_parser('balance', self.GetQ(owners, ''), len(owners))

    def loading_state(self, addresses, balances):
        self.mt.insert_leaves(addresses, balances, False)
        self.onChainState.initialize_state(addresses)
        
    # Interface of GRuB
    def GetQ(self, keys, conditions):

        values = [self.mt.get_values(key) for key in keys ]
        onChainKeys, offChainKeys, offChainValues, lastReplicateIndex = self.onChainState.make_decision_for_read(keys, values, self.K)
        indices = self.mt.get_indices_by_keys(keys)

        # call read
        offChainKeysIndices = []
        if len(offChainKeys) > 0:
            offChainKeysIndices = self.mt.get_indices_by_keys(offChainKeys)
        depth = self.mt.get_depth()
        root = self.mt.get_root()
        proof = self.mt.get_proof(offChainKeysIndices)
        #print('Read:', keys, 'offChain:', offChainKeys, 'offChainValues:', offChainValues)
        return self.SC.send_transactions(self.Contract_type, 2, [keys, offChainValues, lastReplicateIndex, offChainKeysIndices, proof, depth], len(keys), 'R')
    
    def Puts(self, keys, values, w_index=0):
        # values = self.mt.hash_leaves(values)
        # update the merkle tree
        self.mt.update_leaves(keys, values, False)
        self.onChainState.insert_state(keys)
        submitKeys, submitValues, replicateIndex = self.onChainState.make_decision_for_write(keys, values, self.K)
        indices = self.mt.get_indices_by_keys(submitKeys)
        root = self.mt.get_root()
        print('submited indices:', indices, 'replicateIndex:',replicateIndex, 'new root:', root)

        # upload the merkle root 
        return self.SC.send_transactions(self.Contract_type, 1, [indices, root], len(keys), 'Write' + str(w_index))

    def TokenPuts(self, senders, receivers, amounts, transfer_index):
        # retrieve the balance 
        users = list(dict.fromkeys(senders + receivers))
        balances = {} 
        for user in users: 
            balances[user] = self.mt.get_values(user) 
        
        # update the balance 
        for i in range(len(amounts)):
            balances[senders[i]] -= amounts[i]
            balances[receivers[i]] += amounts[i]
        values = [balances[user] for user in users] 
        self.mt.update_leaves(users, values, False)

        self.onChainState.insert_state(users)
        submitKeys, submitValues, replicateIndex = self.onChainState.make_decision_for_write(users, values, self.K)
        indices = self.mt.get_indices_by_keys(submitKeys)
        root = self.mt.get_root()
        print('submited keys:', submitKeys, 'replicateIndex:',replicateIndex, 'new root:', root)

        # upload the merkle root 
        return self.SC.send_transactions(self.Contract_type, 1, [submitKeys, root], len(users), 'transfer' + str(transfer_index))
