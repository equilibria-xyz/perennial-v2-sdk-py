from perennial_sdk.main.markets.snapshot_and_oracle_info import *
from perennial_sdk.config import *

# Choose market address:
market_address = 'bnb'

# Prints the snapshot unformatted.
snapshot = fetch_market_snapshot([market_address])
print(snapshot)