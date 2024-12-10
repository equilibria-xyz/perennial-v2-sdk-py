from perennial_sdk.config import *
from examples.example_utils import CLIENT

def deposit_collateral(symbol: str):
    try:
        tx_hash_withdraw = CLIENT.tx_executor.withdraw_collateral(symbol)
        print(f"Withdraw collateral transaction Hash: {tx_hash_withdraw.hex()}")
    
    except Exception as e:
        print(f'Error encountered while depositing collateral to market {symbol}, Error: {e}')
        return None
