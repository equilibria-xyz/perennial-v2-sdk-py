import os
from web3 import Web3
from dotenv import load_dotenv
from eth_account import Account

load_dotenv()
infura_url = os.getenv('infura_url')
private_key = os.getenv('private_key')

web3 = Web3(Web3.HTTPProvider(infura_url))
account = Account.from_key(private_key)
account_address = account.address
network_id = web3.net.version
