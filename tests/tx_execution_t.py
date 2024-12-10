from perennial_sdk.sdk import PerennialSDK
from perennial_sdk.constants import *
from perennial_sdk.utils import *
from perennial_sdk.main.markets.snapshot_and_oracle_info import *
from tests.test_utils import time_function_call
from hexbytes import HexBytes
from perennial_sdk.utils.global_utils import *

class TxExecutionTester:
    def __init__(self):
        self.client = PerennialSDK()
        self.address = os.getenv('ADDRESS')

    def test_approve_usdc_to_dsu(self) -> bool:
        try:
            initial_approval_amount = USDC_CONTRACT.functions.allowance(
                self.address,
                MULTI_INVOKER_ADDRESS
                ).call() / 1e6
            
            new_approval_amount = initial_approval_amount + 100
            print(new_approval_amount)

            tx_hash = self.client.tx_executor.approve_usdc_to_dsu(new_approval_amount)
            print(tx_hash)
            if not isinstance(tx_hash, str):
                logger.error(f'tx_execution_t.py/test_approve_usdc_to_dsu() - Approval function did not return a transaction hash.')
                return None
            
            post_tx_approval_amount = USDC_CONTRACT.functions.allowance(
                self.address,
                MULTI_INVOKER_ADDRESS
                ).call() / 1e6
            
            if post_tx_approval_amount - initial_approval_amount != 100:
                logger.error(f'tx_execution_t.py/test_approve_usdc_to_dsu() - Approval amount mismatch. pre-tx: {initial_approval_amount}, post-tx: {post_tx_approval_amount}.')
                return False
            elif post_tx_approval_amount - initial_approval_amount == 100:
                return True
        
        except Exception as e:
            logger.error(f'tx_execution_t.py/test_approve_usdc_to_dsu() - Error while testing approval of USDC to the DSU contract. Error: {e}', exc_info=True)
            return None
    
    def test_commit_price_to_multi_invoker(
            self,
            symbol: str
        ) -> bool:
        try:
            tx_hash = self.client.tx_executor.commit_price_to_multi_invoker(symbol)
            if not isinstance(tx_hash, str):
                logger.error(f'tx_execution_t.py/test_commit_price_to_multi_invoker() - MultiInvoker price commit did not return a transaction hash.')
                return None
            else:
                return True
        
        except Exception as e:
            logger.error(f'tx_execution_t.py/test_commit_price_to_multi_invoker() - Error while committing price to MultiInvoker. Error: {e}', exc_info=True)
            return None
        
    def test_deposit_collateral(self) -> bool:
        try:
            tx_hash = self.client.tx_executor.deposit_collateral(
                'eth',
                100
            )

            if not isinstance(tx_hash, str):
                logger.error(f'tx_execution_t.py/test_deposit_collateral() - Failed to deposit collateral.')
                return None
            else:
                return True

        except Exception as e:
            logger.error(f'tx_execution_t.py/test_deposit_collateral() - Error while deposit collateral to ETH market. Error: {e}', exc_info=True)
            return None
    
    def test_withdraw_collateral(self) -> bool:
        try:
            pre_withdrawal_balance = USDC_CONTRACT.functions.balanceOf(
                self.address
                ).call() / 1e6

            tx_hash = self.client.tx_executor.withdraw_collateral(
                'eth'
            )

            time.sleep(2)

            post_withdrawal_balance = USDC_CONTRACT.functions.balanceOf(
                self.address
                ).call() / 1e6

            if not isinstance(tx_hash, str):
                logger.error(f'tx_execution_t.py/test_withdraw_collateral() - Failed to withdraw collateral.')
                return None

            else:
                delta = post_withdrawal_balance - pre_withdrawal_balance
                if delta > 0:
                    logger.info(f'tx_execution_t.py/test_withdraw_collateral() - Collateral withdrawn: {delta} USDC.')
                    return True

        except Exception as e:
            logger.error(f'tx_execution_t.py/test_withdraw_collateral() - Error while withdrawing collateral. Error: {e}', exc_info=True)
            return None
    
    def test_market_order(self) -> bool:
        try:
            price = float(self.client.market_info.fetch_market_price('eth')['latest_market_price'])
            amount_in_asset = price / 100

            symbol = 'eth'
            long_amount = 0
            short_amount = amount_in_asset
            maker_amount = 0
            collateral_amount = 100

            tx_hash = self.client.tx_executor.place_market_order(
                symbol,
                long_amount,
                short_amount,
                maker_amount,
                collateral_amount
            )

            if not isinstance(tx_hash, str):
                logger.error(f'tx_execution_t.py/test_market_order() - Failed to place market order.')
                return None
            else:
                return True

        except Exception as e:
            logger.error(f'tx_execution_t.py/test_market_order() - Error while withdrawing collateral. Error: {e}', exc_info=True)
            return None
    
    def test_close_position(self) -> bool:
        try:
            tx_hash = self.client.tx_executor.close_position_in_market('eth')

            if not isinstance(tx_hash, str):
                logger.error(f'tx_execution_t.py/test_market_order() - Failed to place market order.')
                return None
            else: 
                return True

        except Exception as e:
            logger.error(f'tx_execution_t.py/test_market_order() - Error while withdrawing collateral. Error: {e}', exc_info=True)
            return None


x = TxExecutionTester()
x.test_commit_price_to_multi_invoker('eth')
# x.test_deposit_collateral()
# time.sleep(2)
# y = x.test_close_position()
# y = x.test_withdraw_collateral()
# print(y)

            
