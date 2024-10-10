from perennial_sdk.config import *
from perennial_sdk.main.orders.order_manager import withdraw_collateral, deposit_collateral,approve_usdc_to_dsu


# Choose market and deposit amount.
market_address = 'sol'
collateral_amount = 62.5

# Approve USDC spending if collateral is being used and deposit it.
approve_usdc_to_dsu(collateral_amount)

# Deposit collateral.
tx_hash_deposit = deposit_collateral(market_address,collateral_amount)
print(f"Withdraw collateral transaction Hash: {tx_hash_deposit.hex()}")