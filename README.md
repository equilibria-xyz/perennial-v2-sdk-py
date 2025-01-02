# Overview

This tool is designed to communicate with the Perennial exchange from Python and read/write the following data:

## Read account and market information:

1.  Open positions (Iterates through available markets -> checks for open positions -> prints them in the end)
2.  Open orders (Prints a list of open orders and their details, incl. nonces)
3.  Collaterals
4.  Maintenance margin requirements
5.  Pair prices
6.  Funding rate

## Execute market orders:

1.  Closing positions
2.  Placing market orders
3.  Placing limit orders
4.  Placing trigger orders
5.  Canceling orders

- When closing positions - Doesnt automatically withdraw the collateral, you should use the last step in the example to do so.
- When placing market/limit order - Approves collateral (62.5$ min), commits price to MultiInvoker, places order.
- When placing trigger orders -
  - Placing collateral is optional,
  - Commits price and places order.
  - If you are holding a Long position you should choose side 1 - Buy; Even though you need it to short. Same for short position.
  - The delta is with how much you want to reduce the position size , so it should be negative.
  - For full close delta = 0.
- To cancel orders, you will need the nonce fo the order (from MultiInvoker side). You can get this by using fetch_open_orders.py.

## Features

- Connects to an Arbitrum node using a provided RPC URL
- Retrieves oracle information for specified markets
- Fetches VAAs from the Pyth Network
- Creates market snapshots using a Lens contract
- Supports multiple markets and optional account specification
- Reads all needed information from the snapshot

## Prerequisites

- RPC URL (in .env)
- Wallet private key (in .env)
- Python 3.7+
- Required Libraries:
- `web3` library
- `python-dotenv` library
- `requests` library
- `eth-account` library
- `eht_abi` library

## Installation

### Using pip

You can install the SDK using pip:

```bash
pip install perennial_sdk==0.1.0
```

### Using Poetry

If you prefer using Poetry for dependency management, you can add the SDK to your project with:

```bash
poetry add perennial_sdk@0.1.0
```

## Development

If you are using Poetry, you can set up your environment with:

1. Install Poetry if you haven't already:

   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. Install dependencies:

   ```bash
   poetry install
   ```

3. Activate the virtual environment:
   ```bash
   poetry run python <command here>
   ```

## Example Usage

    Private key and RPC url will need to be added first to .env.

   As of the latest release, many functions now take 
   ```python
   def some_func(snapshot: dict = None)
   ```
   as an optional argument. the reason for this is to reduce the amount of calls made to the chain such that the total time required to call large amounts of data is reduced.\
   One example of how to use this effectively is found in the market info tests, where upon initialization of the tester class we have this:

   ```python
       def __init__(self):
        self.client = PerennialSDK()
        self.snapshots = self.client.market_info.get_all_snapshots()
   ```

   here we collect all the market snapshots at once via the above method, and store them as local state. Now, when we are calling all of the functions we want to test, we simply pass the relevant snapshot in as an argument like so:

   ```python
   for symbol, contract in arbitrum_markets.items():
                try:
                    snapshot: dict = self.snapshots[symbol]
                    rate_dict = client.market_info.fetch_market_funding_rate(symbol, snapshot)
                    if rate_dict:
                        rates.append(rate_dict)
                    else:
                        raise Exception
                except Exception as e:
                    logger.exception(f'test_funding_rates - Exception occurred while fetching rates for symbol {symbol}. Error: {e}', exc_info=True)
   ```

   note that if a snapshot argument is not passed, one will be fetched automatically. Also note that if a lot of calls are being made without pre-fetched snapshots this will quite quickly start to introduce a lot of latency. For individual trades, not passing a snapshot argument is fine; if one was to perform multiple calls on a single markets one can also call an individual snapshot at the start and use it for all of the market calls.

   
