import requests
from perennial_sdk.constants import *
from perennial_sdk.config import *
from utils import logger


# Define the Order class to represent trigger orders
class Order:
    def __init__(self, order_id, account, market, side, trigger_price, trigger_delta, comparison, cancelled, executed, collaterals, nonce):
        self.order_id = order_id
        self.account = account
        self.market = market
        self.side = side
        self.trigger_price = trigger_price
        self.trigger_delta = trigger_delta
        self.comparison = comparison
        self.cancelled = cancelled
        self.executed = executed
        self.collaterals = collaterals
        self.nonce = nonce

    def __str__(self):
        """String representation of the order for easy printing."""
        return (f"Order ID: {self.order_id}\n"
                f"Account: {self.account}\n"
                f"Market: {self.market}\n"
                f"Side: {self.side}\n"
                f"Trigger Price: {self.trigger_price}\n"
                f"Trigger Delta: {self.trigger_delta}\n"
                f"Comparison: {self.comparison}\n"
                f"Cancelled: {self.cancelled}\n"
                f"Executed: {self.executed}\n"
                f"Collaterals: {self.collaterals}\n"
                f"Nonce: {self.nonce}\n")

    def is_active(self):
        """Check if the order is active (not cancelled or executed)."""
        return not self.cancelled and not self.executed


def fetch_trigger_orders():
    """Fetch and return a list of Order objects for the given account."""

    try:
        headers = {
            'Content-Type': 'application/json'
        }

        # Define the GraphQL query
        query = f"""
        {{
        multiInvokerTriggerOrders(
            first: 100, 
            where: {{ 
                    account: "{account_address}",
                    cancelled: false
                }}
        ) {{
            id
            account
            market
            triggerOrderSide
            triggerOrderDelta
            triggerOrderPrice
            triggerOrderComparison
            cancelled
            executed
            associatedOrder {{
                    startCollateral
                    endCollateral
                }}
            nonce
        }}
        }}
        """

        address_to_market_name = {v.lower(): k.upper() for k, v in arbitrum_markets.items()}
        response = requests.post(arbitrum_graph_url, json={'query': query}, headers=headers)

        if response.status_code == 200:
            try:

                data = response.json()
                orders = data['data']['multiInvokerTriggerOrders']

                order_objects = []
                for order in orders:
                    order_id = str(order['id'])
                    account = str(order['account'])
                    market = f"{market_name} ({order['market']})"
                    market_address = str(order['market']).lower()
                    market_name = address_to_market_name.get(market_address, "Unknown Market")
                    side = "Long" if order['triggerOrderSide'] == 1 else "Short"
                    trigger_price = f"{int(order['triggerOrderPrice']) / BIG_6_DIVISOR:.2f}"
                    trigger_delta = f"{int(order['triggerOrderDelta']) / 1e6:.4f}"
                    comparison = "<=" if order['triggerOrderComparison'] == -1 else ">="
                    cancelled = order['cancelled']
                    executed = order['executed']
                    collaterals = order['associatedOrder']
                    nonce = int(order['nonce'])

                    order = {
                        'order_id': order_id,
                        'account': account,
                        'market': market,
                        'side': side,
                        'trigger_price': trigger_price,
                        'trigger_delta': trigger_delta,
                        'comparison': comparison,
                        'cancelled': cancelled,
                        'executed': executed,
                        'collaterals': collaterals,
                        'nonce': nonce
                    }
                    order_objects.append(order)

                return order_objects

            except requests.exceptions.JSONDecodeError as e:
                logger.error(f"account_info.py/fetch_trigger_orders() - JSONDecode error while attempting to parse response as JSON. Raw response: {response.text}")
                return None
        else:
            logger.error(f"account_info.py/fetch_trigger_orders() - Failed to fetch data, response code: {response.status_code}, Response text: {response.text}")
            return None
    
    except Exception as e:
        logger.error(f'account_info.py/fetch_trigger_orders() - Error while fetching trigger orders. Error: {e}', exc_info=True)
        return None

def fetch_latest_order_nonce():
    """Fetch the nonce of the most recent order for the given account."""
    try:
        headers = {
            'Content-Type': 'application/json'
        }

        # Define the GraphQL query
        query = f"""
        {{
        multiInvokerTriggerOrders(
            first: 1, 
            where: {{ 
                    account: "{account_address}",
                    cancelled: false
                }},
            orderBy: nonce,
            orderDirection: desc
        ) {{
            id
            account
            market
            triggerOrderSide
            triggerOrderDelta
            triggerOrderPrice
            triggerOrderComparison
            cancelled
            executed
            associatedOrder {{
                    startCollateral
                    endCollateral
                }}
            nonce
        }}
        }}
        """

        # Map market addresses to market names
        address_to_market_name = {v.lower(): k.upper() for k, v in arbitrum_markets.items()}

        # Send the POST request with the query
        response = requests.post(arbitrum_graph_url, json={'query': query}, headers=headers)

        # Check if the request was successful
        if response.status_code == 200:
            try:
                # Try to parse the response JSON
                data = response.json()
                orders = data['data']['multiInvokerTriggerOrders']

                # Return the orders as a list of Order objects
                order_objects = []
                for order in orders:
                    market_address = order['market'].lower()  # Convert to lowercase for lookup
                    market_name = address_to_market_name.get(market_address, "Unknown Market")

                    # Create an Order object
                    order_obj = Order(
                        order_id=order['id'],
                        account=order['account'],
                        market=f"{market_name} ({order['market']})",
                        side="Long" if order['triggerOrderSide'] == 1 else "Short",
                        trigger_price=f"{int(order['triggerOrderPrice']) / 1e6:.2f}",  # Price in micro units
                        trigger_delta=f"{int(order['triggerOrderDelta']) / 1e6:.4f}",  # Delta in micro units
                        comparison="<=" if order['triggerOrderComparison'] == -1 else ">=",
                        cancelled=order['cancelled'],
                        executed=order['executed'],
                        collaterals=order['associatedOrder'],
                        nonce=order['nonce']
                    )
                    order_objects.append(order_obj)

                return order_objects

            except requests.exceptions.JSONDecodeError as e:
                logger.error(f"account_info.py/fetch_latest_order_nonce() - Failed to parse response as JSON. Raw response: {response.text}")
                return None
        else:
            logger.error(f"account_info.py/fetch_latest_order_nonce() - Failed to fetch data: {response.status_code}. Response text: {response.text}")
            return None

    except Exception as e:
        logger.error(f'account_info.py/fetch_latest_order_nonce() - Error while fetching latest order nonce. Error: {e}', exc_info=True)
        return None