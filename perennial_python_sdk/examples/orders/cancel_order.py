from perennial_sdk.config import *
from perennial_sdk.main.orders.order_manager import cancel_order


market_address = 'sol' # market address is required by MultiInvoker, but whatever value you use, it will still cancel only by nonce.
nonce = 10744

tx_hash_cancel_order = cancel_order(market_address,nonce)
print(f'Order cancelled hash: 0x{tx_hash_cancel_order.hex()}')
