# Perennial Markets Snapshot Tool

## Overview

This tool is designed to create snapshots of Perennial Markets on the Arbitrum network. It interacts with various smart contracts to gather market data, oracle information, and creates a snapshot using a Lens contract.

## Features

- Connects to an Arbitrum node using a provided RPC URL
- Retrieves oracle information for specified markets
- Fetches VAAs from the Pyth Network
- Creates market snapshots using a Lens contract
- Supports multiple markets and optional account specification

## Prerequisites

- Python 3.7+
- `web3` library
- `requests` library

## Installation

1. Clone this repository:

   ```
   git clone https://github.com/equilibria-xyz/perennial-v2-sdk-py
   cd perennial-v2-sdk-py
   ```

2. Install the required Python packages:

   ```
   pip install web3 requests
   ```

## Usage

Run the script using the following command:

```
python main.py --rpc [RPC_URL] --market [MARKET_SYMBOL] [--account? ACCOUNT_ADDRESS]
```

Arguments:

- `--rpc`: (Required) The URL of the Arbitrum RPC endpoint
- `--market`: (Required) The market symbol (e.g., 'BTC-USD')
- `--account`: (Optional) The account address to interact with

Example:

```
python main.py --rpc https://arb-mainnet.g.alchemy.com/v2/your-api-key --market btc --account 0x742d35Cc6634C0532925a3b844Bc454e4438f44e
```

## Note

This tool is designed for use with the Arbitrum network and Perennial Markets. Ensure you have the necessary permissions and understand the implications of interacting with these contracts.

## Contributing

Contributions to improve the tool are welcome. Please follow the standard fork-and-pull request workflow.

## License

...
