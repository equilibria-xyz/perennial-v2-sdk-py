from perennial_sdk.config import *
from perennial_sdk.main.orders.order_manager import withdraw_collateral

# Choose market.
market_address = 'bnb'

# Withdraw remaining collateral.
tx_hash_withdraw = withdraw_collateral(market_address)
print(f"Withdraw collateral transaction Hash: {tx_hash_withdraw.hex()}")