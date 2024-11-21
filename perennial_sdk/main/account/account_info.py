from datetime import datetime, timezone
from perennial_sdk.main.markets import *
from perennial_sdk.main.markets.market_info import MarginMaintenanceInfo


class PositionDetails:
    def __init__(self, market, side, amount, exec_price, latest_price, timestamp, pre_update_collateral,
                 post_update_collateral):
        self.market = market
        self.side = side
        self.amount = amount
        self.exec_price = exec_price
        self.latest_price = latest_price
        self.timestamp = timestamp
        self.pre_update_collateral = pre_update_collateral
        self.post_update_collateral = post_update_collateral

    def get_position_object(self):
            return {
                    "market": self.market,
                    "side": self.side,
                    "size_in_asset": self.amount,
                    "execution_price": self.exec_price,
                    "latest_price": self.latest_price,
                    "opened_at": self.timestamp,
                    "pre_update_collateral": self.pre_update_collateral,
                    "post_update_collateral": self.post_update_collateral
            }


class AccountInfo:

    def __init__(self, account):
        self.account = account

    @staticmethod
    def fetch_balance(contract, account_address: str, divisor=1e6):
        return contract.functions.balanceOf(account_address).call() / divisor

    @staticmethod
    def fetch_usdc_balance(account_address: str) -> float:
        return AccountInfo.fetch_balance(usdc_contract, account_address)

    @staticmethod
    def fetch_dsu_balance(account_address: str) -> float:
        return AccountInfo.fetch_balance(dsu_contract, account_address)

    @staticmethod
    def fetch_open_positions(market_address: str):
        snapshot = fetch_market_snapshot([market_address])
        pre_update_snap = snapshot["result"]["preUpdate"]["marketAccountSnapshots"][0]
        post_update_snap = snapshot["result"]["postUpdate"]["marketAccountSnapshots"][0]
        position_info = post_update_snap["position"]

        if position_info["maker"] == 0 and position_info["long"] == 0 and position_info["short"] == 0:
            return None  # No open position

        exec_price = pre_update_snap["prices"][0] / 1e6
        latest_price = post_update_snap["prices"][0] / 1e6
        trade_opened_utc = datetime.fromtimestamp(position_info["timestamp"], timezone.utc).strftime(
            '%d-%m-%y %H:%M:%S')
        side = 'MAKER' if position_info["maker"] != 0 else 'LONG' if position_info["long"] != 0 else 'SHORT'
        amount = max(position_info["maker"], position_info["long"], position_info["short"]) / 1e6
        pre_update_collateral = pre_update_snap["local"]["collateral"] / 1e6
        post_update_collateral = post_update_snap["local"]["collateral"] / 1e6

        return PositionDetails(
            market=market_address.upper(),
            side=side,
            amount=amount,
            exec_price=exec_price,
            latest_price=latest_price,
            timestamp=trade_opened_utc,
            pre_update_collateral=pre_update_collateral,
            post_update_collateral=post_update_collateral
        ).get_position_object()

    @staticmethod
    def get_liquidation_price_for_position(market_address: str) -> float:
        try:
            position_details = AccountInfo.fetch_open_positions(market_address)
            maintenance_margin = MarginMaintenanceInfo.get_maintenence_margin()
            liquidation_price = AccountInfo.calculate_liquidation_price(
                position_details,
                maintenance_margin
            )

            return liquidation_price
        
        except Exception as e:
            print(f'Account_info.py - Error while calculating liquidation price for position. Error: {e}')
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
            print(f'Account_info.py - Error while calculating liquidation price for position. Error: {e}')
            return None

