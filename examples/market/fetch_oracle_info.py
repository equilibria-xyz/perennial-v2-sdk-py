from perennial_sdk.main.markets.snapshot_and_oracle_info import *


SYMBOL = 'eth'


oracle_info = fetch_oracle_info(arbitrum_markets[SYMBOL],market_provider_ids[SYMBOL])
print(oracle_info)
