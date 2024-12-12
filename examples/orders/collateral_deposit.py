from perennial_sdk.config import *
from examples.example_utils import CLIENT


def deposit_collateral(
    symbol: str,
    collateral_amount: float
    ):

    try:
        CLIENT.tx_executor.approve_usdc_to_multi_invoker(collateral_amount)
        tx_hash_deposit = deposit_collateral(symbol,collateral_amount)
        print(f"Withdraw collateral transaction Hash: {tx_hash_deposit.hex()}")
    
    except Exception as e:
        print(f'Error encountered while depositing collateral to market {symbol}, Error: {e}')
        return None