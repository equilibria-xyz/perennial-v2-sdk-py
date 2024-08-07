from web3 import Web3, utils, constants

import base64
import json
import requests
from typing import List

import argparse

# Custom Functions
from pyth_utils import get_vaa
from decoder_utils import decodeCalldata

# Load ABIs
market_abi = json.load(open("./abi/Market.json"))
orcale_abi = json.load(open("./abi/Oracle.json"))
pyth_oracle_abi = json.load(open("./abi/PythOracle.json"))
keeper_abi = json.load(open("./abi/Keeper.json"))
lens_artifact = json.load(open("./artifacts/Lens.json"))

# Constants
chainId = 42161
market_factory = "0x8D8903B294B358BA1B5d91FB838e5dC35370c7D2"
arbitrum_markets = {
    "eth": "0x90A664846960AaFA2c164605Aebb8e9Ac338f9a0",
    "btc": "0xcC83e3cDA48547e3c250a88C8D5E97089Fd28F60",
    "sol": "0x02258bE4ac91982dc1AF7a3D2C4F05bE6079C253",
    "matic": "0x7e34B5cBc6427Bd53ECFAeFc9AC2Cad04e982f78",
    "tia": "0x2CD8651b0dB6bE605267fdd737C840442A96fAFE",
    "rlb": "0x708B750f9f5bD23E074a5a0A64EF542585906e85",
    "link": "0xD9c296A7Bee1c201B9f3531c7AC9c9310ef3b738",
    "bnb": "0x362c6bC2A4EA2033063bf20409A4c5E8C5754056",
    "xrp": "0x2402E92f8C58886F716F5554039fA6398d7A1EfB",
    "arb": "0x3D1D603073b3CEAB5974Db5C54568058a9551cCC",
    "msqBTC": "0x768a5909f0B6997efa56761A89344eA2BD5560fd",
    "cmsqETH": "0x004E1Abf70e4FF99BC572843B63a63a58FAa08FF",
    "jup": "0xbfa99F19a376F25968865983c41535fa368B28da",
    "xau": "0x1A1745e9cc740269D3e75b506e1AbF7Cbf1fE7d3",
    "mog": "0xc8b73eCFdb775cB9899A0d22fFc8d11228Ac35CB",
}

market_provider_ids = {
    "btc": "0xe62df6c8b4a85fe1a67db44dc12de5db330f7ac66b72dc658afedf0f4a415b43",
    "eth": "0xff61491a931112ddf1bd8147cd1b641375f79f5825126d665480874634fd0ace",
    "arb": "0x3fa4252848f9f0a1480be62745a4629d9eb1322aebab8a791e344b3b9c1adcf5",
    "sol": "0xef0d8b6fda2ceba41da15d4095d1da392a0d2f8ed0c6c7bc0f4cfac8c280b56d",
    "matic": "0x5de33a9112c2b700b8d30b8a3402c103578ccfa2765696471cc672bd5cf6ac52",
    "tia": "0x09f7c1d7dfbb7df2b8fe3d3d87ee94a2259d212da4f30c1f0540d066dfa44723",
    "rlb": "0x2f2d17abbc1e781bd87b4a5d52c8b2856886f5c482fa3593cebf6795040ab0b6",
    "link": "0x8ac0c70fff57e9aefdf5edf44b51d62c2d433653cbb2cf5cc06bb115af04d221",
    "bnb": "0x2f95862b045670cd22bee3114c39763a4a08beeb663b145d283c31d7d1101c4f",
    "xrp": "0xec5d399846a9209f3fe5881d70aae9268c94339ff9817e8d18ff19fa05eea1c8",
    "msqBTC": "0x403d2f23c2015aee67e9311896907cc05c139b2c771a92ae48a2c0e50e6883a4",
    "cmsqETH": "0x002aa13b58df1c483e925045e9a580506812ed5bc85c188d3d8b501501294ad4",
    "jup": "0x0a0408d619e9380abad35060f9192039ed5042fa6f82301d0e48bb52be830996",
    "xau": "0x765d2ba906dbc32ca17cc11f5310a89e9ee1f6420508c63861f2f8ba4ee34bb2",
    "mog": "0x17894b9fff49cd07efeab94a0d02db16f158efe04e0dee1db6af5f069082ce83",
}


def get_oracle_info(marketAddress, provider_id):
    """
    Retrieve oracle information for a given market address.

    This function interacts with several smart contracts to gather information
    about the oracle system associated with a specific market.

    Args:
        marketAddress (str): The Ethereum address of the market contract.

    Returns:
        tuple: A tuple containing (factoryAddress, min_valid_time, underlyingId).
    """

    # Create a contract instance for the market
    marketContract = w3.eth.contract(address=marketAddress, abi=market_abi)

    # Get the oracle address from the market contract
    oracle_address = marketContract.functions.oracle().call()

    # Create a contract instance for the oracle
    oracleContract = w3.eth.contract(address=oracle_address, abi=orcale_abi)

    # Get the current and latest oracle versions
    current_oracle, latest_oracle = oracleContract.functions["global"]().call()

    # Retrieve oracle information for the current version
    oracles = oracleContract.functions.oracles(current_oracle).call()

    # Extract the Pyth oracle address
    pyth_oracle_address = oracles[0]

    # Create a contract instance for the Pyth oracle
    pythOracleContract = w3.eth.contract(
        address=pyth_oracle_address, abi=pyth_oracle_abi
    )

    # Get the factory address from the Pyth oracle contract
    factoryAddress = pythOracleContract.functions.factory().call()

    # Create a contract instance for the factory
    factory = w3.eth.contract(address=factoryAddress, abi=keeper_abi)

    # Get the minimum valid time from the factory contract
    min_valid_time = factory.functions.validFrom().call()

    # Get the underlying ID for the given provider ID
    underlyingId = factory.functions.toUnderlyingId(provider_id).call()

    # Return the collected information
    return (
        factoryAddress,
        min_valid_time,
        underlyingId,
    )


def snapshot_markets(markets, account):
    lens_address = utils.get_create_address(account, constants.MAX_INT)
    lensContract = w3.eth.contract(address=lens_address, abi=lens_artifact["abi"])

    priceCommitments = []
    marketAddresses = []

    for market in markets:
        factoryAddress, min_valid_time, underlyingId = get_oracle_info(
            arbitrum_markets[market], market_provider_ids[market]
        )

        vaa, publishTime = get_vaa(underlyingId.hex(), min_valid_time)

        priceCommitments.append(
            {
                "keeperFactory": factoryAddress,
                "version": publishTime - min_valid_time,
                "value": 1,
                "ids": [underlyingId],
                "updateData": "0x" + base64.b64decode(vaa).hex(),
            }
        )
        marketAddresses.append(arbitrum_markets[market])

    calldata = lensContract.encodeABI(
        fn_name="snapshot",
        args=[
            priceCommitments,
            marketAddresses,
            Web3.to_checksum_address(account),
        ],
    )

    ethCallPayload = {
        "to": lens_address,
        "from": account,
        "data": calldata,
    }

    operatorStorage = Web3.solidity_keccak(
        ["bytes32", "bytes32"],
        [account, "0x0000000000000000000000000000000000000000000000000000000000000001"],
    )

    operatorStorageIndex = Web3.solidity_keccak(
        ["bytes32", "bytes32"], [lens_address, operatorStorage]
    )

    json_payload = (
        {
            "id": 1,
            "jsonrpc": "2.0",
            "method": "eth_call",
            "params": [
                ethCallPayload,
                "latest",
                {
                    lens_address: {
                        "code": lens_artifact["deployedBytecode"],
                        "balance": "0x3635c9adc5dea00000",
                    },
                    market_factory: {
                        "stateDiff": {
                            Web3.to_hex(
                                operatorStorageIndex
                            ): "0x0000000000000000000000000000000000000000000000000000000000000001"
                        }
                    },
                },
            ],
        },
    )

    r = requests.post(rpc, json=json_payload)
    data = r.json()[0]["result"]

    return decodeCalldata(data, "snapshot", lens_artifact["abi"])


def main(markets: List[str], account: str):
    """
    Process multiple markets to create a snapshot.

    Args:
        markets (List[str]): A list of market addresses to process.

    Returns:
        str: The encoded calldata for the snapshot function.
    """

    snapshot = snapshot_markets(markets, account)
    print(snapshot)


# Set up the argument parser
parser = argparse.ArgumentParser(description="Snapshot Perennial Markets")

# Add arguments
parser.add_argument("--rpc", help="The URL of the RPC endpoint")
parser.add_argument("--market", help="The market symbol (e.g., 'BTC-USD')")
parser.add_argument(
    "--account", help="The account address to interact with", required=False
)

# Parse the arguments
args = parser.parse_args()

if args.rpc == None:
    print("Please provide the RPC URL via --rpc")
    exit()

print(f"Connecting to RPC: {args.rpc}")
rpc = args.rpc


# Connect to the Ethereum node
w3 = Web3(Web3.HTTPProvider(rpc))

# Check if connected
if w3.is_connected:
    print("Connected to Arbitrum node")
else:
    print("Failed to connect to Arbitrum node")
    exit()

print(f"Snapshotting the {args.market} market")
main([args.market], args.account or "0x0000000000000000000000000000000000000000")
