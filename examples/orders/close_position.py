from perennial_sdk.config import *
import time
from examples.example_utils import CLIENT


def close_position_in_market(symbol: str):
    try:

        tx_hash_commit = CLIENT.tx_executor.commit_price_to_multi_invoker(symbol)
        print(f"Commit price transaction Hash: 0x{tx_hash_commit.hex()}")

        tx_hash_update = CLIENT.tx_executor.close_position_in_market(symbol)
        print(f"Close position transaction Hash: {tx_hash_update.hex()}")

        time.sleep(5)

        tx_hash_withdraw = CLIENT.tx_executor.withdraw_collateral(symbol)
        print(f"Withdraw collateral transaction Hash: {tx_hash_withdraw.hex()}")
    
    except Exception as e:
        print(f'Error encountered while closing position in market {symbol}, Error: {e}')
        return None