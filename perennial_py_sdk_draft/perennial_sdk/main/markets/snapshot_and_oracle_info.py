from perennial_sdk.constants import *
from perennial_sdk.artifacts.lens_abi import *
from perennial_sdk.utils.pyth_utils import *
from perennial_sdk.utils.decoder_utils import *
from perennial_sdk.config import *


# Function to extract oracle info:
def fetch_oracle_info(market_address, provider_id):
    """
    Retrieve oracle information for a given market address.

    This function interacts with several smart contracts to gather information
    about the oracle system associated with a specific market.

    Args:
        market_address (str): The Ethereum address of the market contract.

    Returns:
        tuple: A tuple containing (factory_address, min_valid_time, underlying_id).
    """

    # Create a contract instance for the market
    market_contract = web3.eth.contract(address=market_address, abi=market_abi)

    # Get the oracle address from the market contract
    oracle_address = market_contract.functions.oracle().call()

    # Create a contract instance for the oracle
    oracle_contract = web3.eth.contract(address=oracle_address, abi=oracle_abi)

    # Get the current and latest oracle versions
    global_function = getattr(oracle_contract.functions, "global")
    current_oracle, latest_oracle = global_function().call()

    # Retrieve oracle information for the current version
    oracles = oracle_contract.functions.oracles(current_oracle).call()

    # Extract the Pyth oracle address
    pyth_oracle_address = oracles[0]
    current_oracle_timestamp = oracles[1]

    # Create a contract instance for the Pyth oracle
    pyth_oracle_contract = web3.eth.contract(
        address=pyth_oracle_address, abi=pyth_oracle_abi
    )

    # Get the factory address from the Pyth oracle contract
    factory_address = pyth_oracle_contract.functions.factory().call()

    # Create a contract instance for the factory
    factory = web3.eth.contract(address=factory_address, abi=keeper_abi)

    # Get the minimum valid time from the factory contract
    min_valid_time = factory.functions.validFrom().call()

    # Get the underlying ID for the given provider ID
    underlying_id = factory.functions.toUnderlyingId(provider_id).call()

    # Return the collected information
    return (
        latest_oracle,
        current_oracle,
        current_oracle_timestamp,
        factory_address,
        min_valid_time,
        underlying_id)

# Function to create a market snapshot:
def fetch_market_snapshot(markets, account):
    lens_address = utls.get_create_address(account, cnstnts.MAX_INT)
    lens_contract = web3.eth.contract(address=lens_address, abi=lens_abi)

    price_commitments = []
    market_addresses = []

    for market in markets:
        latest_oracle,current_oracle,current_oracle_timestamp,factory_address,min_valid_time,underlying_id = fetch_oracle_info(
            arbitrum_markets[market], market_provider_ids[market]
        )

        vaa_data, publish_time = get_vaa(underlying_id.hex(), min_valid_time)

        price_commitments.append(
            {
                "keeperFactory": factory_address,
                "version": publish_time - min_valid_time,
                "value": 1,
                "ids": [Web3.to_bytes(hexstr=underlying_id.hex())],
                "updateData":Web3.to_bytes(hexstr='0x'+vaa_data)
            }
        )
        market_addresses.append(arbitrum_markets[market])

    calldata = lens_contract.encode_abi(
        abi_element_identifier="snapshot",
        args=[
            price_commitments,
            market_addresses,
            web3.to_checksum_address(account),
        ],
    )

    eth_call_payload = {
        "to": lens_address,
        "from": account,
        "data": calldata,
    }

    operator_storage = web3.solidity_keccak(
        ["bytes32", "bytes32"],
        [account, "0x0000000000000000000000000000000000000000000000000000000000000001"],
    )

    operator_storage_index = web3.solidity_keccak(
        ["bytes32", "bytes32"], [lens_address, operator_storage]
    )

    json_payload = (
        {
            "id": 1,
            "jsonrpc": "2.0",
            "method": "eth_call",
            "params": [
                eth_call_payload,
                "latest",
                {
                    lens_address: {
                        "code": lens_deployedbytecode,
                        "balance": "0x3635c9adc5dea00000",
                    },
                    market_factory_address: {
                        "stateDiff": {
                            web3.to_hex(
                                operator_storage_index
                            ): "0x0000000000000000000000000000000000000000000000000000000000000001"
                        }
                    },
                },
            ],
        },
    )

    r = requests.post(infura_url, json=json_payload)
    data = r.json()[0]["result"]

    return decodeCalldata(data, "snapshot", lens_abi)
