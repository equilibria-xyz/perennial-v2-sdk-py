from perennial_sdk.config import *
from perennial_sdk.main.graph_queries.order_fetcher import *
from perennial_sdk.main.orders.order_manager import *


# Step 1: Set up the necessary parameters
market_address = 'bnb'             # Market address (e.g., 'bnb' for Binance Coin)
side = 2                           # Trade side: 1 = Buy; 2 = Short
price = 620                        # Limit price for the order in USDC
delta = 0.0001                   # Trade size in market units (e.g., -0.0001 for a small short position)
collateral_amount = 62.5              # Collateral amount in USDC (set to 0 if not providing collateral)

# # Step 2: Approve USDC spending if collateral is being used and deposit it.
approve_usdc_to_dsu(collateral_amount)
deposit_collateral(market_address, collateral_amount)
#
# # Step 3: Commit the price to the MultiInvoker contract
commit_price_to_multi_invoker(market_address)
#
# # Step 4: Place a limit order
tx_hash_place_limit_order = place_limit_order(market_address, side, price, delta)
print(f'Order placed position transaction hash: 0x{tx_hash_place_limit_order.hex()}')