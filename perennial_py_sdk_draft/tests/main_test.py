from eth_account import Account
from constants.all_constants import *
from web3 import Web3

infura_url = "https://arbitrum-mainnet.infura.io/v3/d8eaa7b40bbf4359ba4bd8a3659dca93"
web3 = Web3(Web3.HTTPProvider(infura_url))
private_key = ""
account = Account.from_key(private_key)
account_address = account.address
network_id = web3.net.version

print(f"           Connected to network with ID: {network_id}")
print(f'Loaded account: {account.address}')

multi_invoker_contract = web3.eth.contract(address=multi_invoker_address,abi=multi_invoker_abi)

#
def invoke_update_market_position(account, market, new_maker, new_long, new_short, collateral, wrap, interface_fee1,
                                  interface_fee2):
    # Prepare invocation data directly using contract's encodeABI method
    args_encoded = multi_invoker_contract.encodeABI(
        fn_name='invoke',
        args=[account,[
            market,
            new_maker,
            new_long,
            new_short,
            collateral,
            wrap,
            (interface_fee1['amount'], interface_fee1['receiver'], interface_fee1['unwrap']),
            (interface_fee2['amount'], interface_fee2['receiver'], interface_fee2['unwrap']),
            ]])

    # Build the transaction to invoke the actions
    tx = {
        'from': account_address,
        'to': multi_invoker_address,
        'data': args_encoded,
        'nonce': web3.eth.get_transaction_count(account_address),
        'gas': 500000,  # Estimate appropriate gas limit
        'gasPrice': web3.to_wei('50', 'gwei')
    }

    # Sign the transaction with the private key
    signed_tx = web3.eth.account.sign_transaction(tx, private_key=private_key)

    # Send the transaction
    tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)

    # Wait for the transaction to be mined
    tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

    # Return the transaction receipt
    return tx_receipt


# Example usage
market_address = '0xD9c296A7Bee1c201B9f3531c7AC9c9310ef3b738'  # Example market address
new_maker = 0  # No change to maker position
new_long = 0  # No change to long position
new_short = 0  # Closing short position
collateral = -99000000  # Withdraw this amount of DSU
wrap = True  # Convert DSU to USDC
interface_fee1 = {
    'amount': 0,
    'receiver': '0x0000000000000000000000000000000000000000',
    'unwrap': False
}
interface_fee2 = {
    'amount': 0,
    'receiver': '0x0000000000000000000000000000000000000000',
    'unwrap': False
}

receipt = invoke_update_market_position(
    account=account_address,
    market=market_address,
    new_maker=new_maker,
    new_long=new_long,
    new_short=new_short,
    collateral=collateral,
    wrap=wrap,
    interface_fee1=interface_fee1,
    interface_fee2=interface_fee2
)

print(f'Invoke update market position transaction receipt: {receipt}')