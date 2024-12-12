from perennial_sdk.utils import logger
from perennial_sdk.constants import *

def get_symbol_for_market_address(market_address: str) -> str:
    try:
        for symbol, address in arbitrum_markets.items():
            if address.lower() == market_address.lower():
                return symbol

        raise ValueError(f"global_utils.py/get_symbol_for_market_address() - Market address '{market_address}' not found in arbitrum_markets.")

    except Exception as e:
        logger.error(f"global_utils.py/get_symbol_for_market_address() - Error fetching symbol for market address {market_address}: {e}")
        return None

def from_wei(value):
    return value / 1e18

def decode_bytes32_to_string(bytes32: bytes):
    try:
        bytes32 = bytes32.hex().rstrip("0")
        if len(bytes32) % 2 != 0:
            bytes32 = bytes32 + '0'
        decoded_string = bytes.fromhex(bytes32).decode('utf8')
        return decoded_string
    except Exception as e:
        logger.error(f"global_utils.py/decode_bytes32_to_string() - Failed to decode bytes32 to string: {e}", exc_info=True)
        return None