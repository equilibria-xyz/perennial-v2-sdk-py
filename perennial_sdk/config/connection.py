import os
from web3 import Web3
from dotenv import load_dotenv
from eth_account import Account

load_dotenv()
rpc_url = os.getenv('RPC_URL')
private_key = os.getenv('PRIVATE_KEY')
chain_id = os.getenv('CHAIN_ID')

pyth_url = "https://hermes.pyth.network/v2/updates/price/latest"
arbitrum_graph_url = 'https://subgraph.perennial.finance/arbitrum'
web3 = Web3(Web3.HTTPProvider(rpc_url))
account = Account.from_key(private_key)
account_address = account.address
network_id = web3.net.version
