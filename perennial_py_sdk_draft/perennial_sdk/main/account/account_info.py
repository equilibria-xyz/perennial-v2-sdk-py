from datetime import datetime, timezone
from perennial_sdk.main.markets import *


class AccountInfo:

    def __init__(self,account):
        self.account = account

    def fetch_usdc_balance(self, account_address):
        usdc_balance = usdc_contract.functions.balanceOf(account_address).call()
        return usdc_balance/1000000

    def fetch_dsu_balance(self, account_address):
        dsu_balance = dsu_contract.functions.balanceOf(account_address).call()
        return dsu_balance/1000000

    def fetch_open_positions(self, account_address, market_address):

        snapshot = fetch_market_snapshot([market_address], account_address)

        position_info = snapshot["result"]["postUpdate"]["marketAccountSnapshots"][0]["position"]
        trade_opened_ufix = snapshot["result"]["postUpdate"]["marketAccountSnapshots"][0]["position"]["timestamp"]
        trade_opened_utc = datetime.fromtimestamp(trade_opened_ufix, timezone.utc).strftime('%d-%m-%y %H:%M:%S')

        open_position = False

        if position_info["maker"] != 0 or position_info["long"] != 0 or position_info["short"] != 0:
            open_position = True

            position_details = {
                'market': market_address.upper(),
                'side': 'MAKER' if position_info["maker"] != 0 else 'LONG' if position_info["long"] != 0 else 'SHORT',
                'amount': max(position_info["maker"], position_info["long"], position_info["short"]) / 1e6,
                'timestamp': trade_opened_utc,
                'pre_update_collateral': snapshot["result"]["preUpdate"]["marketAccountSnapshots"][0]["local"][
                                             "collateral"] / 1e6,
                'post_update_collateral': snapshot["result"]["postUpdate"]["marketAccountSnapshots"][0]["local"][
                                              "collateral"] / 1e6,
            }
            return position_details
        else:
            return None
