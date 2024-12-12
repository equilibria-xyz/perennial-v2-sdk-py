from perennial_sdk.config import *
from examples.example_utils import CLIENT

SYMBOL = "eth"

def get_account_info(symbol: str) -> dict:
    try:

        usdc_balance = CLIENT.account_info.fetch_usdc_balance(account_address)
        dsu_balance = CLIENT.account_info.fetch_dsu_balance(account_address)

        account_info = {
            'usdc_balance': usdc_balance,
            'dsu_balance': dsu_balance
        }

        return account_info

    except Exception as e:
        print(f'Error encountered while calling account info for market {symbol}, Error: {e}')
        return None

