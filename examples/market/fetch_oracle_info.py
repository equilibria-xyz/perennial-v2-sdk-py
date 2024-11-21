from perennial_sdk.main.markets.snapshot_and_oracle_info import *


market_address = 'bnb'

oracle_info = fetch_oracle_info(arbitrum_markets[market_address],market_provider_ids[market_address])
print(f'\nLatest oracle: {oracle_info["oracleName"]}'
      f'\nCurrent oracle: {oracle_info}'
      f'\nCurrent oracle timestamp: {oracle_info["staleAfter"]}'
      f'\nFactory address: {oracle_info["oracleFactoryAddress"]}'
      f'\nMin valid time: {oracle_info["minValidTime"]}'
      f'\nUnderlying ID: 0x{oracle_info["underlyingId"].hex()}')
