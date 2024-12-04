from perennial_sdk.sdk import PerennialSDK
from perennial_sdk.constants import *
from perennial_sdk.utils import *
from perennial_sdk.main.markets.snapshot_and_oracle_info import *
from tests.test_utils import time_function_call

class MarketInfoTester:
    def __init__(self):
        self.client = PerennialSDK()
        self.snapshots = self.get_all_snapshots()
    
    @time_function_call
    def run_all_market_tests(self):
        try:
            success_1 = self.test_price_caller()
            success_2 = self.test_funding_rates()

            if success_1 and success_2:
                logger.info(f'market_info_t/run_all_market_tests() - All tests passed')
                return True
            else:
                logger.error(f'market_info_t/run_all_market_tests() - Tests failed. Please debug')
                return False
        
        except Exception as e:
                logger.error(f'market_info_t/run_all_market_tests() - Error while running market tests. Error: {e}', exc_info=True)
                return None

    @time_function_call
    def test_price_caller(self) -> bool:
        try:
            client = self.client

            prices = []
            total_markets = len(arbitrum_markets)
            successful_calls = 0

            for symbol, contract in arbitrum_markets.items():
                try:
                    snapshot: dict = self.snapshots[symbol]
                    price_dict = client.market_info.fetch_market_price(symbol, snapshot)
                    if price_dict:
                        prices.append(price_dict)
                    else:
                        raise Exception
                except Exception as e:
                    logger.exception(f'test_price_caller - Exception occurred while fetching price for symbol {symbol}. Error: {e}', exc_info=True)
            
            for item in prices:
                if item['pre_update_market_price'] != None and item['latest_market_price'] != None:
                    successful_calls += 1
            
            success_percentage = float(successful_calls) / float(total_markets) * 100
            logger.info(f'test_price_caller - Price call success rate: {success_percentage}%.')

            if success_percentage > 85:
                return True
            else:
                return False
        
        except Exception as e:
                logger.error(f'market_info_t/test_price_caller() - Error while testing price calls. Error: {e}', exc_info=True)
                return None

    @time_function_call
    def test_funding_rates(self) -> bool:
        try:
            client = self.client

            rates = []
            total_markets = len(arbitrum_markets)
            successful_calls = 0

            for symbol, contract in arbitrum_markets.items():
                try:
                    snapshot: dict = self.snapshots[symbol]
                    rate_dict = client.market_info.fetch_market_funding_rate(symbol, snapshot)
                    if rate_dict:
                        rates.append(rate_dict)
                    else:
                        raise Exception
                except Exception as e:
                    logger.exception(f'test_funding_rates - Exception occurred while fetching rates for symbol {symbol}. Error: {e}', exc_info=True)
            
            for item in rates:
                if item['net_rate_long_1hr'] != None and item['net_rate_short_1hr'] != None:
                    successful_calls += 1
            
            success_percentage = float(successful_calls) / float(total_markets) * 100
            logger.info(f'test_funding_rates - Funding rate call success rate: {success_percentage}%.')

            if success_percentage > 85:
                return True
            else:
                return False

        except Exception as e:
            logger.error(f'market_info_t - Failed to fetch funding rates. Error: {e}', exc_info=True)
            return None
    
    @time_function_call
    def get_all_snapshots(self) -> dict:
        try:
            all_markets = []
            snapshot_dict = {}

            for market_name, market_address in arbitrum_markets.items():
                all_markets.append(market_name)

            snapshot_dict = fetch_market_snapshot(all_markets)

            processed_snapshot_dict = {}
            for market_name, item in snapshot_dict.items():
                try:
                    market_snapshots = item['preUpdate']['marketSnapshots']
                    for snapshot in market_snapshots:
                        market_address = snapshot['marketAddress']
                        symbol = get_symbol_for_market_address(market_address)
                        processed_snapshot_dict[symbol] = item

                except KeyError as e:
                    logger.error(f"market_info_t - KeyError encountered while parsing snapshot: {e}", exc_info=True)

            return processed_snapshot_dict

        except Exception as e:
            logger.error(f'market_info_t - Failed to fetch funding rates. Error: {e}', exc_info=True)
            return None


x = MarketInfoTester()
y = x.run_all_market_tests()

            

            