from perennial_sdk.sdk import PerennialSDK
from perennial_sdk.constants import *
from perennial_sdk.utils import *
from perennial_sdk.main.markets.snapshot_and_oracle_info import *
from tests.test_utils import time_function_call


class AccountInfoTester:
    def __init__(self):
        self.client = PerennialSDK()
        self.successes = []
        self.failures = []

    @time_function_call
    def run_all_account_tests(self):
        try:
            test_results = {
                "test_fetch_usdc_balance": self.test_fetch_usdc_balance(),
                "test_fetch_dsu_balance": self.test_fetch_dsu_balance(),
                "test_fetch_open_positions": self.test_fetch_open_positions(),
                "test_get_liquidation_price_for_position": self.test_get_liquidation_price_for_position(),
                "test_calculate_liquidation_price": self.test_calculate_liquidation_price(),
                "test_get_trigger_orders": self.test_get_trigger_orders()
            }

            self.successes = [name for name, passed in test_results.items() if passed]
            self.failures = [name for name, passed in test_results.items() if not passed]

            success_percentage = len(self.successes) / len(test_results) * 100

            logger.info(f'AccountInfoTester/run_all_account_tests - Success rate: {success_percentage}%.')
            if self.failures:
                logger.error(f'AccountInfoTester/run_all_account_tests - Failed tests: {self.failures}')

            return success_percentage == 100

        except Exception as e:
            logger.error(f'AccountInfoTester/run_all_account_tests - Error while running account tests. Error: {e}', exc_info=True)
            return False

    def test_fetch_usdc_balance(self) -> bool:
        try:
            usdc_balance = self.client.account_info.fetch_usdc_balance()
            if usdc_balance is not None and usdc_balance >= 0:
                logger.info(f'test_fetch_usdc_balance - USDC balance fetched successfully: {usdc_balance}')
                return True
            else:
                raise ValueError("USDC balance is invalid or None.")
        except Exception as e:
            logger.error(f'test_fetch_usdc_balance - Error: {e}', exc_info=True)
            return False

    def test_fetch_dsu_balance(self) -> bool:
        try:
            dsu_balance = self.client.account_info.fetch_dsu_balance()
            if dsu_balance is not None and dsu_balance >= 0:
                logger.info(f'test_fetch_dsu_balance - DSU balance fetched successfully: {dsu_balance}')
                return True
            else:
                raise ValueError("DSU balance is invalid or None.")
        except Exception as e:
            logger.error(f'test_fetch_dsu_balance - Error: {e}', exc_info=True)
            return False
    
    def test_get_trigger_orders(self, should_find_orders: bool) -> bool:
        try:
            orders_found: bool = False
            orders = self.client.order_fetcher.fetch_trigger_orders()
            if len(orders) > 0:
                    orders_found = True

            if should_find_orders and orders_found:
                return True
            elif should_find_orders and not orders_found:
                return False
            elif not should_find_orders and orders_found:
                return False
            elif not should_find_orders and not orders_found:
                return True
            
            return None

        except Exception as e:
            logger.error(f'account_info_t.py/test_get_trigger_orders() - Error while placing limit order on market ETH. Error: {e}', exc_info=True)
            return None

    def test_fetch_open_positions(self) -> bool:
        try:
            sample_market = list(arbitrum_markets.keys())[0]
            snapshot = self.client.account_info.market_reader.get_all_snapshots()
            open_positions = self.client.account_info.fetch_open_positions(sample_market, snapshot[sample_market])
            if open_positions is not None:
                logger.info(f'test_fetch_open_positions - Open positions fetched successfully: {open_positions}')
                return True
            else:
                logger.info('test_fetch_open_positions - No open positions found.')
                return True
        except Exception as e:
            logger.error(f'test_fetch_open_positions - Error: {e}', exc_info=True)
            return False

    def test_get_liquidation_price_for_position(self) -> bool:
        try:
            sample_market = list(arbitrum_markets.keys())[0]
            liquidation_price = self.client.account_info.get_liquidation_price_for_position(sample_market)
            if liquidation_price is not None and liquidation_price > 0:
                logger.info(f'test_get_liquidation_price_for_position - Liquidation price fetched successfully: {liquidation_price}')
                return True
            else:
                raise ValueError("Liquidation price is invalid or None.")
        except Exception as e:
            logger.error(f'test_get_liquidation_price_for_position - Error: {e}', exc_info=True)
            return False

    def test_calculate_liquidation_price(self) -> bool:
        try:
            position_details = {
                "side": "LONG",
                "execution_price": 2000.0,
                "post_update_collateral": 1000.0,
                "size_in_asset": 0.5
            }
            maintenance_margin = {"min_maintenance_margin": 0.05}
            liquidation_price = self.client.account_info.calculate_liquidation_price(position_details, maintenance_margin)
            if liquidation_price is not None and liquidation_price > 0:
                logger.info(f'test_calculate_liquidation_price - Liquidation price calculated successfully: {liquidation_price}')
                return True
            else:
                raise ValueError("Calculated liquidation price is invalid or None.")
        except Exception as e:
            logger.error(f'test_calculate_liquidation_price - Error: {e}', exc_info=True)
            return False

x = AccountInfoTester()
y = x.test_get_trigger_orders(True)
print(y)