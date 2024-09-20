from perennial_sdk.main.account.account_info import AccountInfo
from perennial_sdk.config import *


market_address = "link"  # Choose market
account_address = account_address # Your account address here


def print_account_info(account_address, market):

    usdc_balance = AccountInfo.fetch_usdc_balance(account,account_address)

    print('----------------------------------------------')
    print(f'USDC balance: {usdc_balance:.2f}')
    print('----------------------------------------------')
    dsu_balance = AccountInfo.fetch_dsu_balance(account,account_address)
    print(f'DSU balance: {dsu_balance:.2f}')

    open_position = AccountInfo.fetch_open_positions(account,account_address, market)
    if open_position:
        print('----------------------------------------------')
        print(f"Open position on {open_position['market']}")
        print('----------------------------------------------')
        print(f"Side: {open_position['side']}")
        print(f"Amount: {open_position['amount']}")
        print(f"Opened at: {open_position['timestamp']}")
        print(f"Collateral (Pre-update): {open_position['pre_update_collateral']} USD")
        print(f"Collateral (Post-update): {open_position['post_update_collateral']} USD")
        print('----------------------------------------------')
    else:
        print('----------------------------------------------')
        print("No open positions.")
        print('----------------------------------------------')



        # Print on separate lines:

print(print_account_info(account_address, market_address))
