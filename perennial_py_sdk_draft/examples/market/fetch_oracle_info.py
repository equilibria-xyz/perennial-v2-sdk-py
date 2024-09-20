from perennial_sdk.main.markets.snapshot_and_oracle_info import *
from perennial_sdk.config import *


market_address = 'jpy'
account_address = account_address

oracle_info = fetch_oracle_info(arbitrum_markets[market_address],market_provider_ids[market_address])
print(f'\nLatest oracle:{oracle_info[0]}'
      f'\nCurrent oracle:{oracle_info[1]}'
      f'\nCurrent oracle timestamp:{oracle_info[2]}'
      f'\nFactory address: {oracle_info[3]}'
      f'\nMin valid time: {oracle_info[4]}'
      f'\nUnderlying ID: 0x{oracle_info[5].hex()}')
