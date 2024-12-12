from examples.example_utils import CLIENT
from perennial_sdk.config import *

def get_market_price(symbol: str) -> float:
    try:
        price_dict = CLIENT.market_info.fetch_market_price(symbol)
        latest_market_price = float(price_dict['latest_market_price'])

        return latest_market_price
    
    except Exception as e:
        print(f'Error encountered while calling latest price for asset {symbol}, Error: {e}')
        return None

def get_market_funding_rate(symbol: str) -> dict:
    try:
        funding = CLIENT.market_info.fetch_market_funding_rate(symbol)

        return funding
    
    except Exception as e:
        print(f'Error encountered while calling funding rates for market {symbol}, Error: {e}')
        return None

def get_margin_maintenance_info(symbol: str) -> dict:
    try:
        maintenance_margin = CLIENT.market_info.fetch_margin_maintenance_info(symbol)

        return maintenance_margin
    
    except Exception as e:
        print(f'Error encountered while calling funding rates for market {symbol}, Error: {e}')
        return None