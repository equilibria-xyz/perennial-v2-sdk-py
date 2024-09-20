from perennial_sdk import *


# Set current market
current_market_address = 'link'

# Get snapshot info
#snapshot = snapshot_markets([current_market_address], account_address)
print(snapshot)

# Set params
settlement_fee = snapshot["result"]["postUpdate"]["marketSnapshots"][0]["parameter"]["settlementFee"]
latest_oracle_version = snapshot["result"]["postUpdate"]["marketSnapshots"][0]["latestOracleVersion"]
latest_oracle_version_timestamp = latest_oracle_version["timestamp"]
current_timestamp = int(time.time())

# Extract params
factory_address, min_valid_time, underlying_id = get_oracle_info(arbitrum_markets[current_market_address],market_provider_ids[current_market_address])
vaa, publish_time = get_vaa(underlying_id.hex(), min_valid_time)
vaa_bytes = vaa.encode()

# Commit price function
def commit_price(oracle_provider_factory, value, ids, version, data, revert_on_failure):
    action = 6  # COMMIT_PRICE
    args = encode(
        ['address', 'uint256', 'bytes32[]', 'uint256', 'bytes', 'bool'],
        [oracle_provider_factory, value, ids, version, data, revert_on_failure]
    )
    return {'action': action, 'args': args}

# Commit price invocation
commit_price_invocation = commit_price(
    oracle_provider_factory=pyth_factory_address, #correct #from a successful trade
    value=1,
    ids=[underlying_id],  # Replace with actual oracle ID
    version=publish_time-min_valid_time, #timestamp here
    data=vaa_bytes,
    revert_on_failure=True)

commit_tx = multi_invoker_contract.functions.invoke([commit_price_invocation]).build_transaction({
    'from': account_address,
    'chainId': 42161,
    'gas': 2000000,
    'gasPrice': web3.to_wei('2', 'gwei'),
    'nonce': web3.eth.get_transaction_count(account_address),
})

# Sign and send the transaction
signed_commit_tx = web3.eth.account.sign_transaction(commit_tx,private_key)
tx_hash = web3.eth.send_raw_transaction(signed_commit_tx.raw_transaction)

print(f"Transaction sent with hash: {tx_hash.hex()}")

# Wait for the transaction receipt
tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
print(f'Transaction receipt: {tx_receipt}')




"""
def update_position(market, new_maker, new_long, new_short, collateral, wrap, interface_fee_one, interface_fee_two):
    action = 1  # UPDATE_POSITION
    args = encode(
        ['address', 'uint256', 'uint256', 'uint256', 'int256', 'bool', '(uint256,address,bool)', '(uint256,address,bool)'],
        [market, new_maker, new_long, new_short, collateral, wrap, interface_fee_one, interface_fee_two]
    )
    return {'action': action, 'args': args}

# Update position invocation to close the position
update_position_invocation = update_position(
    market=arbitrum_markets[current_market_address],
    new_maker=0,
    new_long=0,
    new_short=0,
    collateral=0,
    wrap=True,
    interface_fee_one=(0, '0x0000000000000000000000000000000000000000', False),
    interface_fee_two=(settlement_fee, factory_address, False))


# Combine invocations into a list
invocations = [commit_price_invocation, update_position_invocation]

# Prepare transaction
tx_data = multi_invoker_contract.functions.invoke(account_address,invocations).build_transaction({
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

"""

############################ Working approve USDC to DSU.
"""approve_tx = usdc_contract.functions.approve(multi_invoker_address,100000000).build_transaction({
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
print(f'Transaction receipt: {signed_tx_receipt}')"""