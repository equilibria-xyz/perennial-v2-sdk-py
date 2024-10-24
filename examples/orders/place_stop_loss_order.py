from perennial_sdk.config import *
from perennial_sdk.main.graph_queries.order_fetcher import fetch_latest_order_nonce
from perennial_sdk.main.orders.order_manager import *


# Step 1: Set up the necessary parameters
market_address = 'link'
side  = 1                # If long position = 1; If short position = 2
price = 10              # Price in USDC
delta = -0.0001          # Size in Market units (ex. 1 LINK)
collateral_amount = 0    # Collateral in USDC

# Step 2: Commit the price to the MultiInvoker contract
commit_price_to_multi_invoker(market_address)

# Step 3: Place a stop-loss order
tx_hash_place_stop_loss_order = place_stop_loss_order(market_address, side,price,delta)
print(f'Stop-loss order placed.\nTransaction hash: 0x{tx_hash_place_stop_loss_order.hex()}')