#! /usr/bin/python3.6
import sys

from lib.testnet_smart_contract import PublicSmartContract
from lib.local_smart_contract import PrivateSmartContract

##################
###### main ######
##################

if (len(sys.argv) < 2 ):
	print ("Usage: ./deploy_smart_contract.py contract_code_file account_index(default=0)")
	exit()

code_file = sys.argv[1]
account_index=0

if len(sys.argv) == 3:
     account_index = int(sys.argv[2])

#SC = PublicSmartContract(account_index)
SC = PrivateSmartContract(account_index)
SC.deploy_smart_contract(code_file)
