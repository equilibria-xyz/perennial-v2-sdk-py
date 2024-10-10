from perennial_sdk.config import *
from perennial_sdk.main.orders.order_manager import cancel_list_of_orders


market_address = 'sol' # market address is required by MultiInvoker, but whatever value you use, it will still cancel only by nonce.
nonces = [10745, 10746]  # List of nonces for the orders to be cancelled

# Cancel all orders with the given nonces
tx_hash_cancel_order = cancel_list_of_orders(market_address, nonces)
print(f'Orders cancelled hash: 0x{tx_hash_cancel_order.hex()}')
