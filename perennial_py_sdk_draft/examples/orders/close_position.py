from perennial_sdk.config import *
from perennial_sdk.main.orders.order_manager import close_position_in_market, commit_price_to_multi_invoker, withdraw_collateral

market_address = 'link'

# # Commit price for position closing.
tx_hash_commit = commit_price_to_multi_invoker(account_address, market_address)
print(f"Commit price transaction Hash: 0x{tx_hash_commit.hex()}")
#
# # Close the position.
tx_hash_update = close_position_in_market(account_address, market_address)
print(f"Update position transaction Hash: {tx_hash_update.hex()}")

# Withdraw remaining collateral.
tx_hash_withdraw = withdraw_collateral(account_address, market_address)
print(f"Withdraw collateral transaction Hash: {tx_hash_withdraw.hex()}")