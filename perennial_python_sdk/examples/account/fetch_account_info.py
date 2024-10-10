from perennial_sdk.main.account.account_info import AccountInfo
from perennial_sdk.config import *


market_address = "link"  # Choose market


def print_account_info(market: str) -> None:
    """Fetch and display account information.
    Including
        - USDC balance
        - DSU balances
        - Open position details in the chosen market"""

    account_info = AccountInfo(account)  # Create an instance of AccountInfo

    usdc_balance = account_info.fetch_usdc_balance(account_address)
    dsu_balance = account_info.fetch_dsu_balance(account_address)

    print('-' * 46)
    print(f'USDC balance: {usdc_balance:.2f}')
    print('-' * 46)
    print(f'DSU balance: {dsu_balance:.2f}')
    print('-' * 46)

    open_position = account_info.fetch_open_positions(market)
    if open_position:
        print(open_position)  # Directly print the PositionDetails object
    else:
        print("No open positions.")
        print('-' * 46)

if __name__ == "__main__":
    print_account_info(market_address)
