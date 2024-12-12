from .main import *
from .main.account.account_info import *
from .main.orders.order_manager import TxExecutor
from .main.markets.market_info import MarketInfo
from .main.graph_queries.order_fetcher import OrderFetcher

class PerennialSDK:
    def __init__(self):
        self.market_info = MarketInfo()
        self.account_info = AccountInfo()
        self.tx_executor = TxExecutor()
        self.order_fetcher = OrderFetcher()

