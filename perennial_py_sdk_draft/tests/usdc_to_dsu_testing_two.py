from web3 import Web3
from eth_account import Account
from eth_abi import encode
from perennial_sdk.abi.dsu_abi import dsu_abi
from perennial_sdk.abi.multi_invoker_abi import multi_invoker_abi
from perennial_sdk.abi.usdc_abi import usdc_abi
from perennial_sdk.constants.contract_addresses import usdc_address, dsu_address, multi_invoker_address
from perennial_sdk.constants.market_addresses import arbitrum_markets

# Connect to an Ethereum node provider (links/gives access to a node) (e.g., Infura).
infura_url = "https://arbitrum-mainnet.infura.io/v3/d8eaa7b40bbf4359ba4bd8a3659dca93"
web3 = Web3(Web3.HTTPProvider(infura_url))
private_key = "62fd39147037c7f63c836d5d134f46979ece3794e491f14c0f269c1a5ccf3b7c"
account = Account.from_key(private_key)
account_address = account.address
network_id = web3.net.version


usdc_contract = web3.eth.contract(address=usdc_address,abi=usdc_abi)
dsu_contract = web3.eth.contract(address=dsu_address,abi=dsu_abi)
multi_invoker_contract = web3.eth.contract(address=multi_invoker_address,abi=multi_invoker_abi)
link_address = arbitrum_markets['link']

# new position
new_maker = 0  # No new maker position
new_long = 0   # No new long position
new_short = 0  # Closing the short position by setting it to 0
collateral = -99938265  # Claiming the collateral; negative because it's being withdrawn
wrap = True  # Assuming collateral needs to be wrapped
interface_fee1 = (0, '0x0000000000000000000000000000000000000000', False)  # No interface fee
interface_fee2 = (0, '0x0000000000000000000000000000000000000000', False)  # No interface fee

# Define the action
action_one = 1  #UPDATE_POSITION
action_six = 6  #Commit price




"""
args_one = encode(
    ['address', 'uint256', 'uint256', 'uint256', 'int256', 'bool', '(uint256,address,bool)', '(uint256,address,bool)'],
    [
        link_address,  # IMarket market
        0,               # UFixed6 newMaker
        0,               # UFixed6 newLong
        0,               # UFixed6 newShort
        -99938265,       # Fixed6 collateral
        True,            # bool wrap
        (0, '0x0000000000000000000000000000000000000000', False),  # InterfaceFee1
        (0, '0x0000000000000000000000000000000000000000', False)   # InterfaceFee2
    ])

args_six = encode(
    ['address', 'uint256', 'bytes32[]', 'uint256', 'bytes', 'bool'],
    [
        keeperFactory, #address
        value,
        ids, 
        version,
        vaa,
        revertOnFailure])


# Prepare the invocation structure
invocations_one = [(action_one,args_one)]

tx = multi_invoker_contract.functions.invoke(account_address,invocations_one).build_transaction({
    'from': account_address,
    'value': web3.to_wei(0, 'ether'),  # If any ETH needs to be sent, specify it here
    'gas': 5000000,
    'gasPrice': web3.to_wei('1', 'gwei'),
    'nonce': web3.eth.get_transaction_count(account_address),
})

# Sign and send the transaction
signed_tx = web3.eth.account.sign_transaction(tx,private_key)
tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)

print(f"Transaction sent with hash: {tx_hash.hex()}")

# Wait for the transaction receipt
tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
print(f'Transaction receipt: {tx_receipt}')

"""