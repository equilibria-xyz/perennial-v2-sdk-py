from perennial_sdk.main.markets import *
from perennial_sdk.utils.calc_funding_rate_draft_two import calculate_funding_and_interest_for_sides

class MarketInfo:
    def __init__(self):
        pass

    def fetch_market_price(symbol: str, snapshot: dict = None) -> float:
        try:
            if not snapshot:
                snapshot = fetch_market_snapshot([symbol])

            pre_update_market_price = float(snapshot["result"]["preUpdate"]["marketSnapshots"][0]["global"]["latestPrice"]) / BIG_6_DIVISOR
            latest_market_price = float(snapshot["result"]["postUpdate"]["marketSnapshots"][0]["global"]["latestPrice"]) / BIG_6_DIVISOR

            return {
                    "market": symbol.upper(),
                    "pre_update_market_price": pre_update_market_price,
                    "latest_market_price": latest_market_price
                }
        
        except Exception as e:
            logger.error(f'market_info.py/fetch_market_price() - Error while fetching latest market price for market {symbol}. Error: {e}', exc_info=True)
            return None

    def fetch_market_funding_rate(symbol: str, snapshot: dict = None):
        try:
            if not snapshot:
                snapshot = fetch_market_snapshot([symbol])

            raw_funding_dict = calculate_funding_and_interest_for_sides(snapshot)
            hourly_net_rate_long = float(raw_funding_dict['long']['funding_rate_long_hourly']) - (raw_funding_dict['long']['funding_fee_long_hourly'] + raw_funding_dict['long']['interest_fee_long_hourly'])
            hourly_net_rate_short = float(raw_funding_dict['long']['funding_rate_short_hourly']) - (raw_funding_dict['short']['funding_fee_short_hourly'] + raw_funding_dict['short']['interest_fee_short_hourly'])

            return {
                "net_rate_long_1hr": hourly_net_rate_long,
                "net_rate_short_1hr": hourly_net_rate_short
            }

        except Exception as e:
            logger.error(f'market_info.py/fetch_market_funding_rate() - Error while fetching latest market price for market {symbol}. Error: {e}', exc_info=True)
            return None

    def fetch_margin_maintenance_info(symbol: str, snapshot: dict = None):
        try:
            if not snapshot:
                snapshot = fetch_market_snapshot([symbol])

            margin_fee = snapshot["result"]["postUpdate"]["marketSnapshots"][0]["riskParameter"]["margin"] / 1e4
            min_margin = snapshot["result"]["postUpdate"]["marketSnapshots"][0]["riskParameter"]["minMargin"] / BIG_6_DIVISOR
            maintenance_fee = snapshot["result"]["postUpdate"]["marketSnapshots"][0]["riskParameter"]["maintenance"] / 1e4
            min_maintenance = snapshot["result"]["postUpdate"]["marketSnapshots"][0]["riskParameter"]["minMaintenance"] / BIG_6_DIVISOR

            return {
                "market": symbol.upper(),
                "margin_fee": margin_fee,
                "min_margin": min_margin,
                "maintenance_fee": maintenance_fee,
                "min_maintenance": min_maintenance
            }
        
        except Exception as e:
            logger.error(f'market_info.py/fetch_margin_maintenance_info() - Error while fetching latest market price for market {symbol}. Error: {e}', exc_info=True)
            return None
