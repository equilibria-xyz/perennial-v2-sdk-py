from perennial_sdk.constants import *
from perennial_sdk.abi import *
from perennial_sdk.artifacts.lens_abi import *
from perennial_sdk.utils.pyth_utils import *
from perennial_sdk.utils.decoder_utils import *
from perennial_sdk.config import *
from web3.contract import Contract
from operator import attrgetter
from perennial_sdk.utils import logger
from concurrent.futures import ThreadPoolExecutor

def fetch_oracle_info(market_address: str, provider_id: str) -> dict:
    try:
        market_contract: Contract = web3.eth.contract(address=market_address, abi=MARKET_ABI)

        with ThreadPoolExecutor() as executor:
            future_risk_param = executor.submit(market_contract.functions.riskParameter().call)
            future_oracle_address = executor.submit(market_contract.functions.oracle().call)
            
            riskParameter = future_risk_param.result()
            oracle_address = future_oracle_address.result()

        oracle_contract: Contract = web3.eth.contract(address=oracle_address, abi=ORACLE_ABI)

        with ThreadPoolExecutor() as executor:
            futures = {
                "global_function": executor.submit(getattr(oracle_contract.functions, "global").call),
                "oracle_name": executor.submit(oracle_contract.functions.name().call),
                "oracle_factory_address": executor.submit(oracle_contract.functions.factory().call)
            }
            global_function, oracle_name, oracle_factory_address = [
                futures[key].result() for key in ["global_function", "oracle_name", "oracle_factory_address"]
            ]
        
        current_oracle, latest_oracle = global_function
        oracle_factory_contract: Contract = web3.eth.contract(address=oracle_factory_address, abi=ORACLE_FACTORY_ABI)

        with ThreadPoolExecutor() as executor:
            future_id = executor.submit(oracle_factory_contract.functions.ids(oracle_address).call)
            future_keeper_oracle_address = executor.submit(oracle_contract.functions.oracles(current_oracle).call)
            
            id = future_id.result()
            keeper_oracle_address = future_keeper_oracle_address.result()[0]

        keeper_oracle_contract: Contract = web3.eth.contract(address=keeper_oracle_address, abi=KEEPER_ORACLE_ABI)
        sub_oracle_factory_address = keeper_oracle_contract.functions.factory().call()
        sub_oracle_factory: Contract = web3.eth.contract(address=sub_oracle_factory_address, abi=KEEPER_FACTORY_ABI)

        with ThreadPoolExecutor() as executor:
            futures = {
                "parameter": executor.submit(sub_oracle_factory.functions.parameter().call),
                "underlying_id": executor.submit(sub_oracle_factory.functions.toUnderlyingId(id).call),
                "sub_oracle_factory_type": executor.submit(sub_oracle_factory.functions.factoryType().call),
                "commitment_gas_oracle": executor.submit(sub_oracle_factory.functions.commitmentGasOracle().call),
                "settlement_gas_oracle": executor.submit(sub_oracle_factory.functions.settlementGasOracle().call),
            }
            parameter, underlying_id, sub_oracle_factory_type, commitment_gas_oracle, settlement_gas_oracle = [
                futures[key].result() for key in futures
            ]

        return {
            "id": id,
            "oracleName": oracle_name,
            "oracleFactoryAddress": oracle_factory_address,
            "oracleAddress": oracle_address,
            "subOracleFactoryAddress": sub_oracle_factory_address,
            "subOracleAddress": sub_oracle_factory_address,
            "subOracleFactoryType": sub_oracle_factory_type,
            "underlyingId": underlying_id,
            "minValidTime": int(parameter[4]), 
            "staleAfter": int(riskParameter[11]), 
            "commitmentGasOracle": commitment_gas_oracle,
            "settlementGasOracle": settlement_gas_oracle,
        }

    except Exception as e:
        logger.error(f'snapshot_and_oracle_info.py/fetch_oracle_info() - Error while fetching oracle info for market address {market_address}. Error: {e}', exc_info=True)
        return None

def fetch_market_snapshot(markets: list):
    try:
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
            abi_element_identifier = 'snapshot',
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
                        MARKET_FACTORY_ADDRESS: {
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
    
    except Exception as e:
        logger.error(f'snapshot_and_oracle_info.py/fetch_market_snapshot(); Failed to fetch market snapshot for markets {markets}. Error: {e}', exc_info=True)
        return None
