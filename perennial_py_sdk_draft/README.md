Perennial Python SDK

# Overview
This tool is designed to communicate with the Perennial exchange from Python and read/write the following data:

## Read account and market information:
   1. Open positions
   2. Collaterals
   3. Maintenance margin requirements
   4. Pair prices
   5. Funding rate

## Execute market orders:
   1. Closing positions
   2. Placing market 
   3. Placing limit orders
   4. Calculate fees

## Features
- Connects to an Arbitrum node using a provided RPC URL
- Retrieves oracle information for specified markets
- Fetches VAAs from the Pyth Network
- Creates market snapshots using a Lens contract
- Supports multiple markets and optional account specification
- Reads all needed information from the snapshot

## Prerequisites
-  Python 3.7+
- `web3` library
- `requests` library

## Example:

This example(/examples/read_account_info_example.py): 
    1. Checks if the account provided has an open position.
        1.1. If yes -> prints position market/side/amount/date and collateral.
        1.2. If no  -> prints "No open positions on the market!" and continues to 2.
    2. Prints pre & post update market price.
    3. Prints funding rate (needs visual update based on client requirements).
    4. Margin and maintenance fees.
    5. Min margin and maintenance requirements.

By changing the values in main(['eth'], '0xAD80D737e09b421E044c466313EfC5D046837a0f') you can get info for desired market and account.
Available markets are: eth,btc,sol,matic,tia,rlb,link,bnb,xrp,arb,msqBTC,cmsqETH,jup,xau,mog.
* jpy and mkr to be implemented soon.
* 
The account provided only has a Short position in LINK for 1.                                0

```
python -c "from examples.read_account_info_example import main; main(['eth'], '0xAD80D737e09b421E044c466313EfC5D046837a0f')"

```