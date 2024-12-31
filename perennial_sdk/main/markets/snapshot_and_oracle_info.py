from perennial_sdk.constants import *
from perennial_sdk.abi import *
from perennial_sdk.artifacts.lens_abi import *
from perennial_sdk.utils.pyth_utils import *
from perennial_sdk.utils.decoder_utils import *
from perennial_sdk.utils.global_utils import *
from perennial_sdk.config import *
from web3.contract import Contract
from operator import attrgetter
from perennial_sdk.utils.logger import logger
from concurrent.futures import ThreadPoolExecutor, as_completed
from web3.datastructures import AttributeDict
from multicall import Call, Multicall
from tests.test_utils import time_function_call

@time_function_call
def fetch_oracle_info(market_address: str, provider_id: str) -> dict:
    """
    Retrieve oracle information for a given market address using multicall with explicit tuple unpacking.

    Args:
        market_address (str): The Ethereum address of the market contract.
        provider_id (str): The provider ID of the smart contract.

    Returns:
        dict: A dictionary containing various oracle and market information.
    """
    try:
        def market_calls():
            return Multicall([
                Call(
                    market_address,
                    ["riskParameter()(uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,int256,int256,uint256,uint256,uint256,bool)"],
                    [
                        ["riskParameter.margin", None],
                        ["riskParameter.maintenance", None],
                        ["riskParameter.linearFee", None],
                        ["riskParameter.proportionalFee", None],
                        ["riskParameter.adiabaticFee", None],
                        ["riskParameter.scale1", None],
                        ["riskParameter.makerLinearFee", None],
                        ["riskParameter.makerProportionalFee", None],
                        ["riskParameter.scale2", None],
                        ["riskParameter.scale3", None],
                        ["riskParameter.efficiencyLimit", None],
                        ["riskParameter.liquidationFee", None],
                        ["riskParameter.minRate", None],
                        ["riskParameter.maxRate", None],
                        ["riskParameter.targetRate", None],
                        ["riskParameter.targetUtilization", None],
                        ["riskParameter.controllerK", None],
                        ["riskParameter.controllerMin", None],
                        ["riskParameter.controllerMax", None],
                        ["riskParameter.minMargin", None],
                        ["riskParameter.minMaintenance", None],
                        ["riskParameter.staleAfter", None],
                        ["riskParameter.makerReceiveOnly", None],
                    ]
                ),
                Call(market_address, ["oracle()(address)"], [["oracleAddress", None]]),
            ], _w3=web3)

        @time_function_call
        def oracle_calls(oracle_address):
            return Multicall([
                Call(oracle_address, ["global()(uint256,uint256)"], [["global", None]]),
                Call(oracle_address, ["name()(string)"], [["oracleName", None]]),
                Call(oracle_address, ["factory()(address)"], [["oracleFactoryAddress", None]]),
            ], _w3=web3)

        @time_function_call
        def factory_calls(oracle_factory_address, oracle_address, current_oracle):
            return Multicall([
                Call(oracle_factory_address, ["ids(address)(bytes32)",oracle_address], [["id", None]]),
                Call(oracle_address, ["oracles(uint256)(address)",current_oracle], [["keeperOracleAddress",None]]),
            ], _w3=web3)

        @time_function_call
        def sub_oracle_calls(sub_oracle_factory_address, id):
            return Multicall([
                Call(sub_oracle_factory_address, ["parameter()(uint256[5])"], [["parameter", None]]),
                Call(sub_oracle_factory_address, ["toUnderlyingId(bytes32)(bytes32)",id], [["underlyingId", None]]),
                Call(sub_oracle_factory_address, ["factoryType()(uint256)"], [["subOracleFactoryType", None]]),
                Call(sub_oracle_factory_address, ["commitmentGasOracle()(uint256)"], [["commitmentGasOracle", None]]),
                Call(sub_oracle_factory_address, ["settlementGasOracle()(uint256)"], [["settlementGasOracle", None]])
            ], _w3=web3)

        with ThreadPoolExecutor() as executor:
            future_market = executor.submit(market_calls)
            market_results = future_market.result()()

            riskParameter = {
                key.split(".")[-1]: value for key, value in market_results.items() if key.startswith("riskParameter")
            }
            oracle_address: str = web3.to_checksum_address(market_results["oracleAddress"])

            future_oracle = executor.submit(oracle_calls, oracle_address)
            oracle_results = future_oracle.result()()

            oracle_contract = web3.eth.contract(address=oracle_address, abi=ORACLE_ABI)
            global_function = getattr(oracle_contract.functions, "global")
            current_oracle, latest_oracle = global_function().call()
            oracle_name = oracle_results["oracleName"]
            oracle_factory_address = oracle_results["oracleFactoryAddress"]

            future_factory = executor.submit(factory_calls, oracle_factory_address, oracle_address, current_oracle)
            factory_results = future_factory.result()()

            id = factory_results["id"]
            keeper_oracle_address = web3.to_checksum_address(factory_results["keeperOracleAddress"])

            keeper_oracle_contract = web3.eth.contract(address=keeper_oracle_address, abi=KEEPER_ORACLE_ABI)
            sub_oracle_factory_address = keeper_oracle_contract.functions.factory().call()

            future_sub_oracle = executor.submit(sub_oracle_calls, sub_oracle_factory_address, id)
            sub_oracle_results = future_sub_oracle.result()()

        parameter = sub_oracle_results["parameter"]
        underlying_id = sub_oracle_results["underlyingId"]
        sub_oracle_factory_type = sub_oracle_results["subOracleFactoryType"]
        commitment_gas_oracle = sub_oracle_results["commitmentGasOracle"]
        settlement_gas_oracle = sub_oracle_results["settlementGasOracle"]

        return {
            **riskParameter,
            "oracle_name": oracle_name,
            "factory_address": oracle_factory_address,
            "oracle_address": oracle_address,
            "sub_oracle_factory_address": sub_oracle_factory_address,
            "sub_oracle_address": sub_oracle_factory_address,
            "sub_oracle_factory_type": sub_oracle_factory_type,
            "underlying_id": underlying_id,
            "min_valid_time": int(parameter[4]),
            "commitment_gas_oracle": commitment_gas_oracle,
            "settlement_gas_oracle": settlement_gas_oracle,
        }

    except Exception as e:
        logger.error(
            f"snapshot_and_oracle_info.py/fetch_oracle_info() - Error while fetching oracle info for market address {market_address}. Error: {e}",
            exc_info=True,
        )
        return None

@time_function_call
def fetch_market_snapshot(markets: list) -> dict:
    """
Fetch market snapshots for the specified markets.

Args:
    markets (list): A list of market names to fetch snapshots for.

Returns:
    dict: A dictionary containing decoded snapshot data for the specified markets.

    None: If an error occurs or the snapshot data cannot be fetched.
"""
    try:
        lens_address = utls.get_create_address(account_address, cnstnts.MAX_INT)
        lens_contract = web3.eth.contract(address=lens_address, abi=lens_abi)

        price_commitments = []
        market_addresses = []

        def process_market(market):
            try:
                oracle_info = fetch_oracle_info(
                    arbitrum_markets[market], market_provider_ids[market]
                )
                vaa_data, publish_time = get_vaa(oracle_info['underlying_id'].hex(), oracle_info['min_valid_time'])

                return {
                    "priceCommitment": {
                        "keeperFactory": oracle_info['sub_oracle_factory_address'],
                        "version": publish_time - oracle_info['min_valid_time'],
                        "value": 1,
                        "ids": [Web3.to_bytes(hexstr=oracle_info['underlying_id'].hex())],
                        "updateData": Web3.to_bytes(hexstr='0x' + vaa_data)
                    },
                    "marketAddress": arbitrum_markets[market]
                }
            except Exception as e:
                logger.error(
                    f"snapshot_and_oracle_info.py/process_market() - Error processing market {market}. Error: {e}",
                    exc_info=True,
                )
                return None

        with ThreadPoolExecutor() as executor:
            futures = {executor.submit(process_market, market): market for market in markets}
            for future in as_completed(futures):
                result = future.result()
                if result:
                    price_commitments.append(result["priceCommitment"])
                    market_addresses.append(result["marketAddress"])

        calldata = lens_contract.encode_abi(
            abi_element_identifier='snapshot',
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

        json_payload = {
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
                    MARKET_FACTORY_ADDRESS: {
                        "stateDiff": {
                            web3.to_hex(
                                operator_storage_index
                            ): "0x0000000000000000000000000000000000000000000000000000000000000001"
                        }
                    },
                },
            ],
        }

        r = requests.post(rpc_url, json=json_payload)
        data = r.json()["result"]

        return decode_call_data(data, "snapshot", lens_abi)

    except Exception as e:
        logger.error(
            f"snapshot_and_oracle_info.py/fetch_market_snapshot() - Error while fetching snapshots for markets {markets}. Error: {e}",
            exc_info=True,
        )
        return None