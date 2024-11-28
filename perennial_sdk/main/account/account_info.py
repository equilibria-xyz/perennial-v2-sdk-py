from datetime import datetime, timezone
from utils import logger
from perennial_sdk.main.markets import *
from perennial_sdk.main.markets.market_info import MarginMaintenanceInfo
from perennial_sdk.constants import *
from perennial_sdk.constants.market_contracts import *
from web3.contract import Contract

class AccountInfo:

    def __init__(self, account):
        self.account = account

    @staticmethod
    def fetch_balance(contract: Contract, account_address: str) -> int:
        try:
            return int(contract.functions.balanceOf(account_address).call() / BIG_6_DIVISOR)
        
        except Exception as e:
            logger.error(f'account_info.py/fetch_balance(); Failed to fetch balance for account address {account_address}. Error: {e}', exc_info=True)
            return None

    @staticmethod
    def fetch_usdc_balance(account_address: str) -> float:
        try:
            return float(AccountInfo.fetch_balance(USDC_CONTRACT, account_address))
        
        except Exception as e:
            logger.error(f'account_info.py/fetch_usdc_balance(); Failed to fetch USDC balance for account address {account_address}. Error: {e}', exc_info=True)
            return None

    @staticmethod
    def fetch_dsu_balance(account_address: str) -> float:
        try:
            return float(AccountInfo.fetch_balance(DSU_CONTRACT, account_address))
        
        except Exception as e:
            logger.error(f'account_info.py/fetch_dsu_balance(); Failed to fetch DSU balance for account address {account_address}. Error: {e}', exc_info=True)
            return None

    @staticmethod
    def fetch_open_positions(symbol: str, snapshot: dict = None):
        try:
            if not snapshot:
                snapshot = fetch_market_snapshot([symbol])

            pre_update_snap = snapshot["result"]["preUpdate"]["marketAccountSnapshots"][0]
            post_update_snap = snapshot["result"]["postUpdate"]["marketAccountSnapshots"][0]
            position_info = post_update_snap["position"]

            if position_info["maker"] == 0 and position_info["long"] == 0 and position_info["short"] == 0:
                logger.info(f'account_info.py/fetch_open_positions() - No open positions found for market {symbol}, returning None')
                return None 

            exec_price = float(pre_update_snap["prices"][0]) / BIG_6_DIVISOR
            latest_price = float(post_update_snap["prices"][0]) / BIG_6_DIVISOR
            trade_opened_utc = datetime.fromtimestamp(position_info["timestamp"], timezone.utc).strftime(
                '%d-%m-%y %H:%M:%S')
            side = 'MAKER' if position_info["maker"] != 0 else 'LONG' if position_info["long"] != 0 else 'SHORT'
            amount = float(max(position_info["maker"], position_info["long"], position_info["short"])) / BIG_6_DIVISOR
            pre_update_collateral = float(pre_update_snap["local"]["collateral"]) / BIG_6_DIVISOR
            post_update_collateral = float(post_update_snap["local"]["collateral"]) / BIG_6_DIVISOR

            return {
                'market': symbol.upper(),
                'side': side,
                'amount': amount,
                'exec_price': exec_price,
                'latest_price': latest_price,
                'timestamp': trade_opened_utc,
                'pre_update_collateral': pre_update_collateral,
                'post_update_collateral': post_update_collateral
            }
        
        except Exception as e:
            logger.error(f'account_info.py/fetch_open_positions() - Failed to fetch open positions for market {symbol}. Error: {e}', exc_info=True)
            return None

    @staticmethod
    def get_liquidation_price_for_position(symbol: str) -> float:
        try:
            position_details = AccountInfo.fetch_open_positions(symbol)
            maintenance_margin = MarginMaintenanceInfo.get_maintenence_margin()
            liquidation_price = AccountInfo.calculate_liquidation_price(
                position_details,
                maintenance_margin
            )

            return liquidation_price
        
        except Exception as e:
            logger.error(f'account_info.py/get_liquidation_price_for_position() - Error while calculating liquidation price for position. Error: {e}', exc_info=True)
            return None
    
    @staticmethod
    def calculate_liquidation_price(position_details: dict, maintenance_margin: dict) -> float:
        try:
            is_long = False
            if position_details['side'] == 'LONG':
                is_long = True

            execution_price = position_details["execution_price"]
            collateral = position_details["post_update_collateral"]
            amount = position_details["size_in_asset"]
            min_maintenance_margin = maintenance_margin["min_maintenance_margin"]

            position_size = amount * execution_price

            if is_long:
                liquidation_price = execution_price - ((collateral - (position_size * min_maintenance_margin)) / amount)
            else:
                liquidation_price = execution_price + ((collateral - (position_size * min_maintenance_margin)) / amount)

            return liquidation_price
        
        except Exception as e:
            logger.error(f'account_info.py/calculate_liquidation_price() - Error while calculating liquidation price for position. Error: {e}', exc_info=True)
            return None

