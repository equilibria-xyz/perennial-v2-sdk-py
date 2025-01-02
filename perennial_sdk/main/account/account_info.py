from datetime import datetime, timezone
from perennial_sdk.utils import logger
from perennial_sdk.main.markets import *
from perennial_sdk.main.markets.market_info import MarketInfo
from perennial_sdk.constants import *
from perennial_sdk.constants.market_contracts import *
from web3.contract import Contract

class AccountInfo:
    def __init__(self):
        self.local_account = os.getenv('ADDRESS')
        self.market_reader = MarketInfo()

    def fetch_balance(self, contract: Contract, account_address: str = None) -> int:
        """
            Fetch the token balance of an account from a specified contract.

            Args:
                contract (Contract): The web3 contract object representing the token.
                account_address (str, optional): The address of the account to fetch the balance for. Defaults to the local account.

            Returns:
                int: The token balance of the account, scaled down by the divisor.

                None: If an error occurs or the balance cannot be fetched.
        """
        try:
            if not account_address:
                account_address = self.local_account

            return int(contract.functions.balanceOf(account_address).call() / BIG_6_DIVISOR)
        
        except Exception as e:
            logger.error(f'account_info.py/fetch_balance(); Failed to fetch balance for account address {account_address}. Error: {e}', exc_info=True)
            return None

    def fetch_usdc_balance(self, account_address: str = None) -> float:
        """
            Fetch the USDC balance of an account.

            Args:
                account_address (str, optional): The address of the account to fetch the balance for. Defaults to the local account.

            Returns:
                float: The USDC balance of the account.

                None: If an error occurs or the balance cannot be fetched.
        """
        try:
            if not account_address:
                account_address = self.local_account

            return float(AccountInfo.fetch_balance(USDC_CONTRACT, account_address))
        
        except Exception as e:
            logger.error(f'account_info.py/fetch_usdc_balance(); Failed to fetch USDC balance for account address {account_address}. Error: {e}', exc_info=True)
            return None

    def fetch_dsu_balance(self, account_address: str = None) -> float:
        """
        Fetch the DSU balance of an account.

        Args:
            account_address (str, optional): The address of the account to fetch the balance for. Defaults to the local account.

        Returns:
            float: The DSU balance of the account.

            None: If an error occurs or the balance cannot be fetched.
        """
        try:
            if not account_address:
                account_address = self.local_account

            return float(AccountInfo.fetch_balance(DSU_CONTRACT, account_address))
        
        except Exception as e:
            logger.error(f'account_info.py/fetch_dsu_balance(); Failed to fetch DSU balance for account address {account_address}. Error: {e}', exc_info=True)
            return None

    def fetch_open_positions(self, symbol: str, snapshot: dict = None):
        """
        Fetch open positions for a given market symbol.

        Retrieves details about open positions for a specific market.

        Args:
            symbol (str): The symbol of the market (in lowercase) to fetch positions for (e.g., "eth").
            snapshot (dict, optional): A pre-fetched market snapshot. If not provided,
                                    a new snapshot is fetched for the specified symbol.

        Returns:
            dict: A dictionary containing the following position details:
                - market (str): The symbol of the market (uppercase).
                - side (str): The type of position ("LONG", "SHORT", or "MAKER").
                - amount (float): The size of the position in asset units.
                - exec_price (float): The execution price of the position.
                - latest_price (float): The most recent price of the market.
                - timestamp (str): The timestamp of the trade opening in UTC.
                - pre_update_collateral (float): The collateral amount before the latest market update.
                - post_update_collateral (float): The collateral amount after the latest market update.
            
            None: If no open positions are found for the given market symbol.

        Logs:
            - Logs a message if no open positions are found.
            - Logs errors if fetching open positions fails.

        Raises:
            Exception: If there is an error processing the snapshot or fetching position details.
        """
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

    def get_liquidation_price_for_position(self, symbol: str) -> float:
        """
        Calculate the liquidation price for an open position in a specific market.

        Args:
            symbol (str): The lowercase symbol of the market to calculate the liquidation price for (e.g., "ETH").

        Returns:
            float: The calculated liquidation price for the position.

            None: If an error occurs or the calculation cannot be completed.
        """
        try:
            position_details = self.fetch_open_positions(symbol)
            maintenance_margin = self.market_reader.fetch_margin_maintenance_info()
            liquidation_price = self.calculate_liquidation_price(
                position_details,
                maintenance_margin
            )

            return liquidation_price
        
        except Exception as e:
            logger.error(f'account_info.py/get_liquidation_price_for_position() - Error while calling liquidation price for position. Error: {e}', exc_info=True)
            return None
    
    def calculate_liquidation_price(self, position_details: dict, maintenance_margin: dict) -> float:
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

