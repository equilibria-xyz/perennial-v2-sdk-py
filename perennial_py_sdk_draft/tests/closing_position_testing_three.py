from web3 import Web3
from eth_account import Account
from eth_abi import encode
from perennial_sdk.abi.dsu_abi import dsu_abi
from perennial_sdk.abi.multi_invoker_abi import multi_invoker_abi
from perennial_sdk.abi.usdc_abi import usdc_abi
from perennial_sdk.constants.contract_addresses import usdc_address, dsu_address, multi_invoker_address
from perennial_sdk.constants.market_addresses import arbitrum_markets
import time

from perennial_sdk.constants.market_provider_ids import market_provider_ids
from perennial_sdk.main import get_oracle_info
from perennial_sdk.utils.pyth_utils import get_vaa

# Connect to an Ethereum node provider (links/gives access to a node) (e.g., Infura).
infura_url = "https://arbitrum-mainnet.infura.io/v3/d8eaa7b40bbf4359ba4bd8a3659dca93"
web3 = Web3(Web3.HTTPProvider(infura_url))
private_key = "62fd39147037c7f63c836d5d134f46979ece3794e491f14c0f269c1a5ccf3b7c"
account = Account.from_key(private_key)
account_address = account.address
network_id = web3.net.version

# Initialise contracts.
usdc_contract = web3.eth.contract(address=usdc_address,abi=usdc_abi)
dsu_contract = web3.eth.contract(address=dsu_address,abi=dsu_abi)
multi_invoker_contract = web3.eth.contract(address=multi_invoker_address,abi=multi_invoker_abi)
current_timestamp = int(time.time())

link_address = arbitrum_markets['sol']
link_provider_id = market_provider_ids['sol']




# Define Perennial Actions for MultiInvoker.

def commit_price(oracle_provider_factory, value, ids, version, data, revert_on_failure):
    action = 6  # COMMIT_PRICE
    args = encode(
        ['address', 'uint256', 'bytes32[]', 'uint256', 'bytes', 'bool'],
        [oracle_provider_factory, value, ids, version, data, revert_on_failure]
    )
    return {'action': action, 'args': args}

def update_position(market, new_maker, new_long, new_short, collateral, wrap, interfaceFee1, interfaceFee2):
    action = 1  # UPDATE_POSITION
    args = encode(
        ['address', 'uint256', 'uint256', 'uint256', 'int256', 'bool', '(uint256,address,bool)', '(uint256,address,bool)'],
        [market, new_maker, new_long, new_short, collateral, wrap, interfaceFee1, interfaceFee2]
    )
    return {'action': action, 'args': args}


# Params needed fpr commit price
factory_address, min_valid_time, underlying_id =get_oracle_info(link_address,link_provider_id)
vaa, publishTime = get_vaa(underlying_id.hex(), min_valid_time)
vaa_bytes = vaa.encode()

# Commit price invocation
commit_price_invocation = commit_price(
    oracle_provider_factory=factory_address, #not sure
    value=1,
    ids=[underlying_id],  # Replace with actual oracle ID
    version=publishTime-min_valid_time, #timestamp here
    data=vaa_bytes,
    revert_on_failure=False
)

# Update position invocation to close the position
update_position_invocation = update_position(market=link_address, new_maker=0, new_long=1, new_short=0, collateral=100000000,
                                             wrap=False,
                                             interfaceFee1=(0, '0x0000000000000000000000000000000000000000', False),
                                             interfaceFee2=(2000000, '0x8CDa59615C993f925915D3eb4394BAdB3feEF413', False))


# Combine invocations into a list
invocations = [commit_price_invocation, update_position_invocation]

approve_tx = usdc_contract.functions.approve(multi_invoker_address,100000000).build_transaction({
    'from': account_address,
    'nonce': web3.eth.get_transaction_count(account_address),
    'gas': 2000000,
    'gasPrice': web3.to_wei('2', 'gwei')
})

signed_approve_tx = web3.eth.account.sign_transaction(approve_tx,private_key)
signed_tx_hash = web3.eth.send_raw_transaction(signed_approve_tx.raw_transaction)
print(f"Transaction sent with hash: {signed_tx_hash.hex()}")

# Wait for the transaction receipt
signed_tx_receipt = web3.eth.wait_for_transaction_receipt(signed_tx_hash)
print(f'Transaction receipt: {signed_tx_receipt}')

# Prepare transaction
tx_data = multi_invoker_contract.functions.invoke(invocations).build_transaction({
    'from': account_address, # might need to remove
    'chainId': 42161, # might need to remove
    'gas': 2000000,
    'gasPrice': web3.to_wei('2', 'gwei'),
    'nonce': web3.eth.get_transaction_count(account_address),
})

# Sign and send the transaction
signed_tx = web3.eth.account.sign_transaction(tx_data,private_key)
tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)

print(f"Transaction sent with hash: {tx_hash.hex()}")

# Wait for the transaction receipt
tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
print(f'Transaction receipt: {tx_receipt}')
