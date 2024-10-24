from perennial_sdk.main.account.account_info import AccountInfo
from perennial_sdk.constants import *


def print_account_info_for_all_markets() -> None:

    # List to store open positions
    open_positions = []

    # Loop through all markets
    for market_name, market_address in arbitrum_markets.items():
        print(f'Checking market: {market_name.upper()} ({market_address})')

        # Use the market name when fetching the snapshot
        try:
            open_position = AccountInfo.fetch_open_positions(market_name)
        except KeyError as e:
            print(f'Error fetching position for market {market_name}: {e}')
            continue

        if open_position:
            open_positions.append(open_position)
            print("Open position found! Will be printed in the end.")
            print('----------------------------------------------')
        else:
            print(f'No open positions in {market_name.upper()}.')
            print('----------------------------------------------')

    # Print all open positions
    if open_positions:
        print(f'Found {len(open_positions)} open position(s):')
        for position in open_positions:
            print('----------------------------------------------')
            print(position)
    else:
        print("No open positions in any market.")
        print('----------------------------------------------')


# Now call the function with the account address
print_account_info_for_all_markets()
