from perennial_sdk.config import *
from perennial_sdk.main.orders.order_manager import *


account_address = account_address
market_address = 'link'
side  = 1                # Side: 1 = Buy; 2 = Short
price = 10               # Price in USDC
delta = 1                # Size in Market units (ex. 1 LINK)
collateral_amount = 65   # Collateral in USDC

tx_hash_place_limit_order = place_limit_order(account_address,market_address, side,price,delta,collateral_amount)
print(f'Order placed position transaction hash: 0x{tx_hash_place_limit_order.hex()}')

# tx_hash_withdraw = withdraw_collateral(account_address, market_address)
# print(f"Withdraw collateral transaction Hash: {tx_hash_withdraw.hex()}")