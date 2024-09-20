from perennial_sdk.main.markets.snapshot_and_oracle_info import *
from perennial_sdk.config import *


market_address = 'jpy'
account_address = account_address

snapshot = fetch_market_snapshot([market_address], account_address)
print(snapshot)