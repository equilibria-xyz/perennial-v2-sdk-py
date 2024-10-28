from perennial_sdk.constants import *
from perennial_sdk.artifacts.lens_abi import *
from perennial_sdk.utils.pyth_utils import *
from perennial_sdk.utils.decoder_utils import *
from perennial_sdk.config import *
from operator import attrgetter


def fetch_oracle_info(market_address: str, provider_id: str) -> dict:
    """
    Retrieve oracle information for a given market address.

    This function interacts with several smart contracts to gather information
    about the oracle system associated with a specific market.

    Args:
        market_address (str): The Ethereum address of the market contract.
        provider_id (str): The provider ID of the smart contract.

    Returns:
        dict: A dictionary containing various oracle and market information.
    """

    # Create a contract instance for the market
    market_contract = web3.eth.contract(address=market_address, abi=market_abi)

    # Fetch risk parameter and oracle address concurrently
    riskParameter = market_contract.functions.riskParameter().call()
    oracle_address = market_contract.functions.oracle().call()

    # Fetch oracle data
    oracle_contract = web3.eth.contract(address=oracle_address, abi=oracle_abi)
    global_function = getattr(oracle_contract.functions, "global")
    current_oracle, latest_oracle = global_function().call()
    oracle_name = oracle_contract.functions.name().call()
    
    # Get the factory address from the keeper oracle contract
    oracle_factory_address = oracle_contract.functions.factory().call()
    oracle_factory_contract = web3.eth.contract(address=oracle_factory_address, abi=oracle_factory_abi)
    id = oracle_factory_contract.functions.ids(oracle_address).call()

    # Retrieve oracle information for the current version
    keeper_oracle_address = oracle_contract.functions.oracles(current_oracle).call()[0]
    keeper_oracle_contract = web3.eth.contract(address=keeper_oracle_address, abi=keeper_oracle_abi)
    sub_oracle_factory_address = keeper_oracle_contract.functions.factory().call()
    
    sub_oracle_factory = web3.eth.contract(address=sub_oracle_factory_address, abi=keeper_factory_abi)

    # Fetch parameters and IDs concurrently
    parameter = sub_oracle_factory.functions.parameter().call()
    underlying_id = sub_oracle_factory.functions.toUnderlyingId(id).call()
    sub_oracle_factory_type = sub_oracle_factory.functions.factoryType().call()
    commitment_gas_oracle = sub_oracle_factory.functions.commitmentGasOracle().call()
    settlement_gas_oracle = sub_oracle_factory.functions.settlementGasOracle().call()

    # Return the collected information as a dictionary
    return {
        "id": id,
        "oracleName": oracle_name,
        "oracleFactoryAddress": oracle_factory_address,
        "oracleAddress": oracle_address,
        "subOracleFactoryAddress": sub_oracle_factory_address,
        "subOracleAddress": sub_oracle_factory_address,
        "subOracleFactoryType": sub_oracle_factory_type,
        "underlyingId": underlying_id,
        "minValidTime": int(parameter[4]), # validFrom is at index 4
        "staleAfter": int(riskParameter[11]),  # Assuming staleAfter is at index 11
        "commitmentGasOracle": commitment_gas_oracle,
        "settlementGasOracle": settlement_gas_oracle,
    }

# Function to create a market snapshot:
def fetch_market_snapshot(markets):
    lens_address = utls.get_create_address(account_address, cnstnts.MAX_INT)
    lens_contract = web3.eth.contract(address=lens_address, abi=lens_abi)

    price_commitments = []
    market_addresses = []

    for market in markets:

        oracle_info = fetch_oracle_info(
            arbitrum_markets[market], market_provider_ids[market]
        )
        vaa_data, publish_time = get_vaa(oracle_info['underlyingId'].hex(), oracle_info['minValidTime'])

        price_commitments.append(
            {
                "keeperFactory": oracle_info['subOracleFactoryAddress'],
                "version": publish_time - oracle_info['minValidTime'],
                "value": 1,
                "ids": [Web3.to_bytes(hexstr=oracle_info['underlyingId'].hex())],
                "updateData":Web3.to_bytes(hexstr='0x'+vaa_data)
            }
        )
        market_addresses.append(arbitrum_markets[market])

    calldata = lens_contract.encode_abi(
        abi_element_identifier="snapshot",
        args=[
            price_commitments,
            market_addresses,
            web3.to_checksum_address(account_address),
        ],
    )

    eth_call_payload = {
        "to": lens_address,
        "from": account_address,
        "data": calldata,
    }

    operator_storage = web3.solidity_keccak(
        ["bytes32", "bytes32"],
        [account_address, "0x0000000000000000000000000000000000000000000000000000000000000001"],
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

    r = requests.post(rpc_url, json=json_payload)
    data = r.json()[0]["result"]

    return decode_call_data(data, "snapshot", lens_abi)
