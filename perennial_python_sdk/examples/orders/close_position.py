from perennial_sdk.config import *
import time
from perennial_sdk.main.orders.order_manager import close_position_in_market, commit_price_to_multi_invoker, withdraw_collateral


#Choose market.
market_address = 'link'

# Commit price for position closing.
tx_hash_commit = commit_price_to_multi_invoker(market_address)
print(f"Commit price transaction Hash: 0x{tx_hash_commit.hex()}")

# Close the position.
tx_hash_update = close_position_in_market(market_address)
print(f"Close position transaction Hash: {tx_hash_update.hex()}")

time.sleep(10)

# Withdraw remaining collateral if needed.
tx_hash_withdraw = withdraw_collateral(market_address)
print(f"Withdraw collateral transaction Hash: {tx_hash_withdraw.hex()}")