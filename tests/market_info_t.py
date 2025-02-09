from perennial_sdk.sdk import PerennialSDK
from perennial_sdk.constants import *
from perennial_sdk.utils import *
from perennial_sdk.main.markets.snapshot_and_oracle_info import *
from perennial_sdk.utils.test_utils import time_function_call

class MarketInfoTester:
    def __init__(self):
        self.client = PerennialSDK()
        self.snapshots = self.client.market_info.get_all_snapshots()
    
    @time_function_call
    def run_all_market_tests(self):
        try:
            test_results = {
                "test_price_caller": self.test_price_caller(),
                "test_funding_rates": self.test_funding_rates(),
                "get_all_snapshots": self.test_get_all_snapshots()
            }

            total_tests = len(test_results)
            passed_tests = [name for name, result in test_results.items() if result]
            failed_tests = [name for name, result in test_results.items() if not result]
            pass_percentage = (len(passed_tests) / total_tests) * 100

            if len(failed_tests) == 0:
                logger.info(f"market_info_t/run_all_market_tests() - All tests passed. Pass percentage: {pass_percentage:.2f}%")
                return True
            else:
                logger.error(
                    f"market_info_t/run_all_market_tests() - {len(failed_tests)} tests failed. "
                    f"Failed tests: {', '.join(failed_tests)}. Pass percentage: {pass_percentage:.2f}%"
                )
                return False

        except Exception as e:
            logger.error(f"market_info_t/run_all_market_tests() - Error while running market tests. Error: {e}", exc_info=True)
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
    def test_get_all_snapshots(self) -> bool:
        try:
            snapshot_dict = self.snapshots

            if not snapshot_dict:
                logger.error("test_get_all_snapshots - Snapshot dictionary is empty.")
                return False

            processed_snapshot_dict = {}
            for market_name, item in snapshot_dict.items():
                try:
                    market_snapshots = item.get('preUpdate', {}).get('marketSnapshots', [])
                    if not market_snapshots:
                        logger.error(f"test_get_all_snapshots - No market snapshots for market: {market_name}")
                        return False

                    for snapshot in market_snapshots:
                        market_address = snapshot.get('marketAddress')
                        symbol = get_symbol_for_market_address(market_address)
                        processed_snapshot_dict[symbol] = item

                except KeyError as e:
                    logger.error(f"test_get_all_snapshots - KeyError encountered while parsing snapshot for market: {market_name}. Error: {e}", exc_info=True)
                    return False

            if processed_snapshot_dict:
                logger.info("test_get_all_snapshots - All snapshots processed successfully.")
                return True
            else:
                logger.error("test_get_all_snapshots - Processed snapshot dictionary is empty.")
                return False

        except Exception as e:
            logger.error(f"test_get_all_snapshots - Failed to fetch or process snapshots. Error: {e}", exc_info=True)
            return False
    


x = MarketInfoTester()
y = x.run_all_market_tests()

            

            