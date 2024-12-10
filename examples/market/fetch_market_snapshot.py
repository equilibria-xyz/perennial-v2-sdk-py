from perennial_sdk.main.markets.snapshot_and_oracle_info import *
from perennial_sdk.config import *

SYMBOL = 'eth'

snapshot = fetch_market_snapshot([SYMBOL])
print(snapshot)