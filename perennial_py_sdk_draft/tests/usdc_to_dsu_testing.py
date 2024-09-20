from eth_account import Account
from web3 import Web3

from perennial_sdk.abi.dsu_abi import dsu_abi
from perennial_sdk.abi.usdc_abi import usdc_abi
from perennial_sdk.constants.contract_addresses import usdc_address, dsu_address

# Connect to an Ethereum node provider (links/gives access to a node) (e.g., Infura).
infura_url = "https://arbitrum-mainnet.infura.io/v3/d8eaa7b40bbf4359ba4bd8a3659dca93"
web3 = Web3(Web3.HTTPProvider(infura_url))
private_key = "62fd39147037c7f63c836d5d134f46979ece3794e491f14c0f269c1a5ccf3b7c"
account = Account.from_key(private_key)
account_address = account.address
network_id = web3.net.version

usdc_contract = web3.eth.contract(address=usdc_address,abi=usdc_abi)
dsu_contract = web3.eth.contract(address=dsu_address,abi=dsu_abi)
"""
tx = usdc_contract.functions.approve(dsu_address, 100).build_transaction({
    'chainId': 42161,  # Change to Arbitrum chainId
    'gas': 70000,  # Estimated gas limit
    'gasPrice': web3.to_wei('10', 'gwei'),  # Gas price in gwei
    'nonce': web3.eth.get_transaction_count(account_address),
})
"""
tx = dsu_contract.functions.mint(100).build_transaction({
    'chainId': 42161,  # Change to Arbitrum chainId
    'from': account_address,
    'gas': 70000,  # Estimated gas limit
    'gasPrice': web3.to_wei('10', 'gwei'),  # Gas price in gwei
    'nonce': web3.eth.get_transaction_count(account_address),
})

# Sign transaction
signed_tx = web3.eth.account.sign_transaction(tx, private_key=private_key)

# Send the transaction
tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)

# Wait for the transaction to be mined
tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

# Return the transaction receipt
print(tx_receipt)