from perennial_sdk.config import *
from perennial_sdk.main.graph_queries.order_fetcher import fetch_latest_order_nonce
from perennial_sdk.main.orders.order_manager import commit_price_to_multi_invoker, approve_usdc_to_dsu, place_market_order
import time

# Step 1: Set up the necessary parameters
market_address = 'link'
collateral_amount = 65   # Min 62.5$
long_amount = 1
short_amount = 0
maker_amount = 0

# Step 2: Approve USDC spending if collateral is being used and deposit it.
signed_approve_tx_hash = approve_usdc_to_dsu(collateral_amount)
print(f'\nApprove USDC transaction hash:{signed_approve_tx_hash.hex()}')

# Step 3: Commit the price to the MultiInvoker contract
tx_hash_commit = commit_price_to_multi_invoker(market_address)
print(f"Commit price transaction Hash: 0x{tx_hash_commit.hex()}")

# Step 4: Place a market order
tx_hash_place_market_order = place_market_order(market_address, long_amount, short_amount, maker_amount, collateral_amount)
print(f'Open position transaction hash: {tx_hash_place_market_order.hex()}')
