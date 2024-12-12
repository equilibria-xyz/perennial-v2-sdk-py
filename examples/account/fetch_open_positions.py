from examples.example_utils import CLIENT
from perennial_sdk.constants import *


def fetch_all_open_positions() -> list:
    try:
        open_positions = []

        for market_name, market_address in arbitrum_markets.items():
            try:
                open_position = CLIENT.account_info.fetch_open_positions(market_name)
            except KeyError as e:
                print(f'KeyError fetching position for market {market_name}: {e}')
                continue

            if open_position:
                open_positions.append(open_position)

        if len(open_positions) > 0:
            return open_positions
        else:
            print("No open positions in any market. Returning None.")
            return None
    
    except Exception as e:
        print(f'Error encountered while fetching open positions. Error: {e}')
        return None
