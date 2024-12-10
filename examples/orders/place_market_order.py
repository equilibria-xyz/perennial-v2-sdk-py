from perennial_sdk.config import *
import time
from examples.example_utils import CLIENT

def close_position_in_market(symbol: str):
    try:
        collateral_amount = 85   # example value, above min collateral value
        long_amount = 1
        short_amount = 0
        maker_amount = 0

        signed_approve_tx_hash = CLIENT.tx_executor.approve_usdc_to_multi_invoker(collateral_amount)
        print(f'Approve USDC tx hash: {signed_approve_tx_hash}')

        tx_hash_commit = CLIENT.tx_executor.commit_price_to_multi_invoker(symbol)
        print(f"Commit price tx hash: {tx_hash_commit}")

        tx_hash_update = CLIENT.tx_executor.place_market_order(
            symbol,
            long_amount,
            short_amount,
            maker_amount,
            collateral_amount
            )
        print(f"Place market order tx hash: {tx_hash_update}")
    
    except Exception as e:
        print(f'Error encountered while placing market order in market {symbol}, Error: {e}')
        return None

