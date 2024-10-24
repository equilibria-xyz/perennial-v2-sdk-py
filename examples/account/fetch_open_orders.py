from perennial_sdk.main.graph_queries.order_fetcher import fetch_trigger_orders
from perennial_sdk.config import *


def fetch_open_orders() -> None:
    # Call the function and fetch trigger orders
    orders = fetch_trigger_orders()

    # Check if any orders were returned
    if orders:
        for order in orders:
            print("Order Details:")
            # Access the attributes of the Order object directly
            print(f"Order ID: {order.order_id}")
            print(f"Account: {order.account}")
            print(f"Market: {order.market}")
            print(f"Side: {order.side}")
            print(f"Trigger Price: {order.trigger_price}")
            print(f"Trigger Delta: {order.trigger_delta}")
            print(f"Comparison: {order.comparison}")
            print(f"Cancelled: {order.cancelled}")
            print(f"Executed: {order.executed}")
            print(f"Collaterals: {order.collaterals}")
            print(f"Nonce: {order.nonce}")
            print("-" * 40)  # Separator for readability
    else:
        print("-" * 40)
        print("No open orders found.")


if __name__ == "__main__":
    fetch_open_orders()