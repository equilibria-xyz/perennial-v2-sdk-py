from perennial_sdk.config import *
from perennial_sdk.main.orders.order_manager import commit_price_to_multi_invoker, approve_usdc_to_dsu, place_market_order

market_address = 'link'
collateral_amount = 100   # Min 100$
long_amount = 1
short_amount = 0
maker_amount = 0

# Approve USDC to be used for collateral (as DSU).
signed_approve_tx_hash = approve_usdc_to_dsu(account_address,collateral_amount)
print(f'\nApprove USDC transaction hash:{signed_approve_tx_hash.hex()}')

# Commit price for position closing.
tx_hash_commit = commit_price_to_multi_invoker(account_address, market_address)
print(f"Commit price transaction Hash: 0x{tx_hash_commit.hex()}")


tx_hash_place_market_order = place_market_order(account_address, market_address, long_amount, short_amount, maker_amount, collateral_amount)
print(f'Open position transaction hash: {tx_hash_place_market_order.hex()}')