from perennial_sdk.main.markets.snapshot_and_oracle_info import *
from perennial_sdk.constants import *
from perennial_sdk.utils.pyth_utils import *
from perennial_sdk.config import *
from decimal import Decimal


def approve_usdc_to_dsu(collateral_amount: float):

    # Ensure the collateral_amount has 2 decimal places
    collateral_amount = round(Decimal(collateral_amount), 2)
    # Convert to smallest unit (6 decimals for USDC)
    amount_usdc = int(collateral_amount * 10 ** 6)

    approve_tx = usdc_contract.functions.approve(multi_invoker_address, amount_usdc).build_transaction({
        'from': account_address,
        'nonce': web3.eth.get_transaction_count(account_address),
        'gas': 2000000,
        'gasPrice': web3.to_wei('2', 'gwei')
    })
    signed_approve_tx = web3.eth.account.sign_transaction(approve_tx, private_key)
    signed_approve_tx_hash = web3.eth.send_raw_transaction(signed_approve_tx.raw_transaction)
    web3.eth.wait_for_transaction_receipt(signed_approve_tx_hash)

    print(f'Approved USDC to be used as collateral: {collateral_amount} USD.')

    return signed_approve_tx_hash

def commit_price_to_multi_invoker(market_address: str):

    # Step 1: Fetch Oracle Information
    latest_oracle, current_oracle, current_oracle_timestamp, factory_address, min_valid_time, underlying_id = fetch_oracle_info(
        arbitrum_markets[market_address], market_provider_ids[market_address]
    )

    # Step 2: Get VAA (Value Associated Agreement) and Publish Time
    vaa_data, publish_time = get_vaa(underlying_id.hex(), min_valid_time)

    # Step 3: Prepare the Commit Price Action
    price_commit_action = {
        "keeperFactory": factory_address,
        "version": publish_time-min_valid_time,
        "value": 1,
        "ids": [Web3.to_bytes(hexstr=underlying_id.hex())],
        "updateData":Web3.to_bytes(hexstr='0x'+vaa_data) # Decode the VAA to bytes
    }

    # Step 4: Create the contract instance for MultiInvoker
    multi_invoker = web3.eth.contract(address=multi_invoker_address, abi=multi_invoker_abi)

    base_fee_per_gas = web3.eth.fee_history(1, "latest")["baseFeePerGas"][-1]
    max_fee_per_gas = base_fee_per_gas + Web3.to_wei(2, 'gwei')

    # Prepare the call data using the ABI encoded args
    action = 6  # Assuming action 6 corresponds to COMMIT_PRICE
    args_encoded = Web3().codec.encode(
        ["address", "uint256", "bytes32[]", "uint256", "bytes", "bool"],
        [
            factory_address,
            price_commit_action["value"],
            price_commit_action["ids"],
            price_commit_action["version"],
            price_commit_action["updateData"],  # Already in bytes format
            True  # revertOnFailure
        ],
    )
    transaction = multi_invoker.functions.invoke(
        account_address,
        [
            {
                "action": action,  # PerennialAction.COMMIT_PRICE
                "args": args_encoded  # Encoded arguments for the action
            }
        ]
    ).build_transaction({
        "from": account_address,
        "nonce": web3.eth.get_transaction_count(account_address),  # Get the transaction nonce
        "value": 1,
        "gas": 4000000,  # Adjust the gas limit as needed
        "maxFeePerGas": max_fee_per_gas
    })

    # Step 6: Sign the transaction
    signed_txn = web3.eth.account.sign_transaction(transaction, private_key=private_key)

    # Step 7: Send the raw transaction
    tx_hash_commit = web3.eth.send_raw_transaction(signed_txn.raw_transaction)
    web3.eth.wait_for_transaction_receipt(tx_hash_commit)

    print(f'Price committed.')

    return tx_hash_commit

def close_position_in_market(market_address: str):

    # Step 1: Prepare the Update Position Action (action = 1)
    update_position_action = [
        arbitrum_markets[market_address],  # IMarket (Market address)
        0,  # newMaker (UFixed6)
        0,  # newLong (UFixed6)
        0,  # newShort (UFixed6)
        0,  # collateral (Fixed6)
        False,  # wrap (bool)
        (0, "0x0000000000000000000000000000000000000000", False),  # interfaceFee1 (amount, receiver, unwrap)
        (0, "0x0000000000000000000000000000000000000000", False)  # interfaceFee2 (amount, receiver, unwrap)
    ]

    # Step 2: Create the contract instance for MultiInvoker
    multi_invoker = web3.eth.contract(address=multi_invoker_address, abi=multi_invoker_abi)

    base_fee_per_gas = web3.eth.fee_history(1, "latest")["baseFeePerGas"][-1]
    max_fee_per_gas = base_fee_per_gas + Web3.to_wei(2, 'gwei')

    # Step 3: ABI-encode the arguments for UPDATE_POSITION
    encoded_args = web3.codec.encode(
        [
            "address",  # IMarket (address)
            "uint256",  # UFixed6 newMaker
            "uint256",  # UFixed6 newLong
            "uint256",  # UFixed6 newShort
            "int256",  # Fixed6 collateral
            "bool",  # wrap
            "(uint256,address,bool)",  # InterfaceFee1
            "(uint256,address,bool)"  # InterfaceFee2
        ],
        update_position_action
    )

    # Step 4: Create the invocation tuple with action type 1 (UPDATE_POSITION)
    invocation_tuple = (1, encoded_args)  # 1 is for UPDATE_POSITION

    # Step 5: Build the invocation array
    invocations = [invocation_tuple]

    # Step 6: Build the transaction to call the invoke function
    update_tx = multi_invoker.functions.invoke(invocations).build_transaction({
        'from': account_address,
        'nonce': web3.eth.get_transaction_count(account_address),
        'gas': 2000000,
        "maxFeePerGas": max_fee_per_gas
    })

    # Step 6: Sign the transaction
    signed_update_tx = web3.eth.account.sign_transaction(update_tx, private_key=private_key)

    # Step 7: Send the raw transaction
    tx_hash_update = web3.eth.send_raw_transaction(signed_update_tx.raw_transaction)

    return tx_hash_update

def withdraw_collateral(market_address: str):

    snapshot = fetch_market_snapshot([market_address])
    post_update_collateral = snapshot["result"]["postUpdate"]["marketAccountSnapshots"][0]["local"]["collateral"]

    # Step 1: Prepare the Update Position Action (action = 1)
    update_position_action = [
        arbitrum_markets[market_address],  # IMarket (Market address)
        0,  # newMaker (UFixed6)
        0,  # newLong (UFixed6)
        0,  # newShort (UFixed6)
        -post_update_collateral,  # collateral (Fixed6)
        True,  # wrap (bool)
        (0, "0x0000000000000000000000000000000000000000", False),  # interfaceFee1 (amount, receiver, unwrap)
        (0, "0x0000000000000000000000000000000000000000", False)  # interfaceFee2 (amount, receiver, unwrap)
    ]
    # Step 2: Create the contract instance for MultiInvoker
    multi_invoker = web3.eth.contract(address=multi_invoker_address, abi=multi_invoker_abi)

    base_fee_per_gas = web3.eth.fee_history(1, "latest")["baseFeePerGas"][-1]
    max_fee_per_gas = base_fee_per_gas + Web3.to_wei(2, 'gwei')

    # Step 3: ABI-encode the arguments for UPDATE_POSITION
    encoded_args = web3.codec.encode(
        [
            "address",  # IMarket (address)
            "uint256",  # UFixed6 newMaker
            "uint256",  # UFixed6 newLong
            "uint256",  # UFixed6 newShort
            "int256",  # Fixed6 collateral
            "bool",  # wrap
            "(uint256,address,bool)",  # InterfaceFee1
            "(uint256,address,bool)"  # InterfaceFee2
        ],
        update_position_action
    )

    # Step 4: Create the invocation tuple with action type 1 (UPDATE_POSITION)
    invocation_tuple = (1, encoded_args)  # 1 is for UPDATE_POSITION

    # Step 5: Build the invocation array
    invocations = [invocation_tuple]

    # Step 6: Build the transaction to call the invoke function
    withdraw_tx = multi_invoker.functions.invoke(invocations).build_transaction({
        'from': account_address,
        'nonce': web3.eth.get_transaction_count(account_address),
        'gas': 2000000,
        "maxFeePerGas": max_fee_per_gas
    })

    # Step 6: Sign the transaction
    signed_withdraw_tx = web3.eth.account.sign_transaction(withdraw_tx, private_key=private_key)

    # Step 7: Send the raw transaction
    tx_hash_withdraw = web3.eth.send_raw_transaction(signed_withdraw_tx.raw_transaction)
    return tx_hash_withdraw

def deposit_collateral(market_address: str, collateral_amount: float):

    amount_usdc = int(collateral_amount * 10 ** 6)
    # Step 1: Prepare the Update Position Action (action = 1)
    deposit_collateral_action = [
        arbitrum_markets[market_address],  # IMarket (Market address)
        0,  # newMaker (UFixed6)
        0,  # newLong (UFixed6)
        0,  # newShort (UFixed6)
        amount_usdc,  # collateral (Fixed6)
        True,  # wrap (bool)
        (0, "0x0000000000000000000000000000000000000000", False),  # interfaceFee1 (amount, receiver, unwrap)
        (0, "0x0000000000000000000000000000000000000000", False)  # interfaceFee2 (amount, receiver, unwrap)
    ]

    # Step 3: ABI-encode the arguments for UPDATE_POSITION
    encoded_args = web3.codec.encode(
        [
            "address",  # IMarket (address)
            "uint256",  # UFixed6 newMaker
            "uint256",  # UFixed6 newLong
            "uint256",  # UFixed6 newShort
            "int256",  # Fixed6 collateral
            "bool",  # wrap
            "(uint256,address,bool)",  # InterfaceFee1
            "(uint256,address,bool)"  # InterfaceFee2
        ],
        deposit_collateral_action
    )

    # Step 4: Create the invocation tuple with action type 1 (UPDATE_POSITION)
    invocation_tuple = (1, encoded_args)  # 1 is for UPDATE_POSITION

    # Step 5: Build the invocation array
    invocations = [invocation_tuple]

    current_nonce = web3.eth.get_transaction_count(account_address)
    base_fee_per_gas = web3.eth.fee_history(1, "latest")["baseFeePerGas"][-1]
    max_fee_per_gas = base_fee_per_gas + Web3.to_wei(2, 'gwei')

    # Step 6: Build the transaction to call the invoke function
    deposit_tx = multi_invoker_contract.functions.invoke(invocations).build_transaction({
        'from': account_address,
        'nonce': current_nonce,
        'gas': 2000000,
        "maxFeePerGas": max_fee_per_gas
    })

    # Step 6: Sign the transaction
    signed_withdraw_tx = web3.eth.account.sign_transaction(deposit_tx, private_key=private_key)

    # Step 7: Send the raw transaction adn wait for receipt.
    tx_hash_deposit= web3.eth.send_raw_transaction(signed_withdraw_tx.raw_transaction)
    web3.eth.wait_for_transaction_receipt(tx_hash_deposit)

    print(f'Deposited collateral: {collateral_amount} USD.')

    return tx_hash_deposit

def place_market_order(market_address: str, long_amount: float, short_amount: float, maker_amount: float, collateral_amount: float):

    place_market_order_action = [
        arbitrum_markets[market_address],  # IMarket (Market address)
        maker_amount * 1000000,  # newMaker (UFixed6)
        long_amount * 1000000,  # newLong (UFixed6)
        short_amount * 1000000,  # newShort (UFixed6)
        collateral_amount * 1000000,  # collateral (Fixed6)
        True,  # wrap (bool)
        (0, "0x0000000000000000000000000000000000000000", False),  # interfaceFee1 (amount, receiver, unwrap)
        (0, "0x0000000000000000000000000000000000000000", False)  # interfaceFee2 (amount, receiver, unwrap)
    ]

    # Step 2: Create the contract instance for MultiInvoker
    multi_invoker = web3.eth.contract(address=multi_invoker_address, abi=multi_invoker_abi)

    base_fee_per_gas = web3.eth.fee_history(1, "latest")["baseFeePerGas"][-1]
    max_fee_per_gas = base_fee_per_gas + Web3.to_wei(2.2, 'gwei')

    # Step 3: ABI-encode the arguments for UPDATE_POSITION
    encoded_args = web3.codec.encode(
        [
            "address",  # IMarket (address)
            "uint256",  # UFixed6 newMaker
            "uint256",  # UFixed6 newLong
            "uint256",  # UFixed6 newShort
            "int256",  # Fixed6 collateral
            "bool",  # wrap
            "(uint256,address,bool)",  # InterfaceFee1
            "(uint256,address,bool)"  # InterfaceFee2
        ],
        place_market_order_action
    )

    # Step 4: Create the invocation tuple with action type 1 (UPDATE_POSITION)
    invocation_tuple = (1, encoded_args)  # 1 is for UPDATE_POSITION

    # Step 5: Build the invocation array
    invocations = [invocation_tuple]

    # Step 6: Build the transaction to call the invoke function
    update_tx = multi_invoker.functions.invoke(invocations).build_transaction({
        'from': account_address,
        'nonce': web3.eth.get_transaction_count(account_address),
        'gas': 2200000,
        "maxFeePerGas": max_fee_per_gas
    })

    # Step 6: Sign the transaction
    signed_place_market_order_tx = web3.eth.account.sign_transaction(update_tx, private_key=private_key)

    # Step 7: Send the raw transaction
    tx_hash_place_market_order = web3.eth.send_raw_transaction(signed_place_market_order_tx.raw_transaction)
    web3.eth.wait_for_transaction_receipt(tx_hash_place_market_order)

    return tx_hash_place_market_order

def place_limit_order(market_address: str, side: int, price: float, delta: float):

    global comparison
    if side==1: comparison=-1
    elif side == 2: comparison=1

    # Multiply price and delta by 1e6 to avoid float issues
    place_limit_order_action = [
        arbitrum_markets[market_address],  # IMarket (Market address)
        side,  # Side = 1 to Buy; 2 to Short
        comparison,  # Comparison -1 if long; 1 if short.
        20 * 1000000,  # Max fee (multiply by 1e6)
        int(price * 1000000),  # Price (convert to int)
        int(delta * 1000000),  # Delta (convert to int)
        (0, "0x8cda59615c993f925915d3eb4394badb3feef413", False),  # interfaceFee1 (amount, receiver, unwrap)
        (0, "0x0000000000000000000000000000000000000000", False)  # interfaceFee2 (amount, receiver, unwrap)
    ]

    # Step 3: ABI-encode the arguments for PLACE_ORDER
    encoded_args = web3.codec.encode(
        [
            "address",     # IMarket (address)
            "int8",        # Side
            "int8",        # Comparison
            "uint256",     # Fee
            "uint256",     # Price (now an integer)
            "int256",      # Delta (now an integer)
            "(uint256,address,bool)",  # InterfaceFee1
            "(uint256,address,bool)"   # InterfaceFee2
        ],
        place_limit_order_action
    )

    # Step 4: Create the invocation tuple with action type 3 (PLACE_ORDER)
    invocation_tuple = (3, encoded_args)  # 3 is for PLACE_ORDER

    # Step 5: Build the invocation array
    invocations = [invocation_tuple]

    base_fee_per_gas = web3.eth.fee_history(1, "latest")["baseFeePerGas"][-1]
    max_fee_per_gas = base_fee_per_gas + Web3.to_wei(2.2, 'gwei')

    limit_order_tx = multi_invoker_contract.functions.invoke(invocations).build_transaction({
        'from': account_address,
        'nonce': web3.eth.get_transaction_count(account_address),
        'gas': 2200000,
        "maxFeePerGas": max_fee_per_gas
    })

    # Step 6: Sign the transaction
    signed_place_limit_order_tx = web3.eth.account.sign_transaction(limit_order_tx, private_key=private_key)

    # Step 7: Send the raw transaction
    tx_hash_place_limit_order = web3.eth.send_raw_transaction(signed_place_limit_order_tx.raw_transaction)

    # Step 8: Wait for receipt
    web3.eth.wait_for_transaction_receipt(tx_hash_place_limit_order)

    return tx_hash_place_limit_order

def cancel_order(market_address: str, nonce: int):

    cancel_order_action = [arbitrum_markets[market_address], nonce]
    cancel_args = web3.codec.encode([
        "address",
        "uint256"
    ],
    cancel_order_action)

    cancel_invocation_tuple = (4, cancel_args)

    cancel_invocations = [cancel_invocation_tuple]

    base_fee_per_gas = web3.eth.fee_history(1, "latest")["baseFeePerGas"][-1]
    max_fee_per_gas = base_fee_per_gas + Web3.to_wei(2.2, 'gwei')

    cancel_order_tx = multi_invoker_contract.functions.invoke(cancel_invocations).build_transaction({
        'from': account_address,
        'nonce': web3.eth.get_transaction_count(account_address),
        'gas': 2200000,
        "maxFeePerGas": max_fee_per_gas
    })

    # Step 6: Sign the transaction
    signed_cancel_order_tx = web3.eth.account.sign_transaction(cancel_order_tx, private_key=private_key)

    # Step 7: Send the raw transaction
    tx_hash_cancel_order = web3.eth.send_raw_transaction(signed_cancel_order_tx.raw_transaction)

    # Step 8: Wait for receipt
    web3.eth.wait_for_transaction_receipt(tx_hash_cancel_order)

    return tx_hash_cancel_order

def cancel_list_of_orders(market_address:str,nonces: list):

    cancel_invocations = []

    # Loop through each nonce and prepare the cancellation action
    for nonce in nonces:
        cancel_order_action = [arbitrum_markets[market_address], nonce]
        cancel_args = web3.codec.encode([
            "address",
            "uint256"
        ], cancel_order_action)

        # Prepare the invocation tuple
        cancel_invocation_tuple = (4, cancel_args)
        cancel_invocations.append(cancel_invocation_tuple)

    # Gas fee calculation
    base_fee_per_gas = web3.eth.fee_history(1, "latest")["baseFeePerGas"][-1]
    max_fee_per_gas = base_fee_per_gas + Web3.to_wei(2.2, 'gwei')

    # Build the transaction
    cancel_order_tx = multi_invoker_contract.functions.invoke(cancel_invocations).build_transaction({
        'from': account_address,
        'nonce': web3.eth.get_transaction_count(account_address),
        'gas': 2200000,
        "maxFeePerGas": max_fee_per_gas
    })

    # Sign the transaction
    signed_cancel_order_tx = web3.eth.account.sign_transaction(cancel_order_tx, private_key=private_key)

    # Send the raw transaction
    tx_hash_cancel_all_orders = web3.eth.send_raw_transaction(signed_cancel_order_tx.raw_transaction)

    # Wait for receipt
    web3.eth.wait_for_transaction_receipt(tx_hash_cancel_all_orders)

    return tx_hash_cancel_all_orders

def place_stop_loss_order(market_address: str, side: int, price: float, delta: float):

    global comparison
    if side == 1:
        comparison = -1
    elif side == 2:
        comparison = 1

    # Multiply price and delta by 1e6 to avoid float issues
    place_stop_loss_action = [
        arbitrum_markets[market_address],  # IMarket (Market address)
        side,  # Side - 1 to Buy; 2 to Short
        comparison,  # Comparison -1 if long; 1 if short.
        20 * 1000000,  # Max fee (multiply by 1e6)
        int(price * 1000000),  # Price (convert to int)
        int(delta * 1000000),  # Delta (convert to int)
        (0, "0x8cda59615c993f925915d3eb4394badb3feef413", False),  # interfaceFee1 (amount, receiver, unwrap)
        (0, "0x0000000000000000000000000000000000000000", False)  # interfaceFee2 (amount, receiver, unwrap)
    ]

    # Step 3: ABI-encode the arguments for PLACE_ORDER
    encoded_args = web3.codec.encode(
        [
            "address",  # IMarket (address)
            "int8",  # Side
            "int8",  # Comparison
            "uint256",  # Fee
            "uint256",  # Price (now an integer)
            "int256",  # Delta (now an integer)
            "(uint256,address,bool)",  # InterfaceFee1
            "(uint256,address,bool)"  # InterfaceFee2
        ],
        place_stop_loss_action
    )

    # Step 4: Create the invocation tuple with action type 3 (PLACE_ORDER)
    invocation_tuple = (3, encoded_args)  # 3 is for PLACE_ORDER

    # Step 5: Build the invocation array
    invocations = [invocation_tuple]

    base_fee_per_gas = web3.eth.fee_history(1, "latest")["baseFeePerGas"][-1]
    max_fee_per_gas = base_fee_per_gas + Web3.to_wei(2.2, 'gwei')

    stop_loss_order_tx = multi_invoker_contract.functions.invoke(invocations).build_transaction({
        'from': account_address,
        'nonce': web3.eth.get_transaction_count(account_address),
        'gas': 2200000,
        "maxFeePerGas": max_fee_per_gas
    })

    # Step 6: Sign the transaction
    signed_stop_loss_order_tx = web3.eth.account.sign_transaction(stop_loss_order_tx, private_key=private_key)

    # Step 7: Send the raw transaction
    tx_hash_stop_loss_order = web3.eth.send_raw_transaction(signed_stop_loss_order_tx.raw_transaction)

    # Step 8: Wait for receipt
    web3.eth.wait_for_transaction_receipt(tx_hash_stop_loss_order)

    return tx_hash_stop_loss_order

def place_take_profit_order(market_address: str, side: int, price: float, delta:float):

    global comparison
    if side==1: comparison=1
    elif side == 2: comparison=-1

    # Multiply price and delta by 1e6 to avoid float issues
    place_take_profit_action = [
        arbitrum_markets[market_address],  # IMarket (Market address)
        side,  # Side - 1 to Buy; 2 to Short
        comparison,  # Comparison -1 if long; 1 if short.
        20 * 1000000,  # Max fee (multiply by 1e6)
        int(price * 1000000),  # Price (convert to int)
        int(delta * 1000000),  # Delta (convert to int)
        (0, "0x8cda59615c993f925915d3eb4394badb3feef413", False),  # interfaceFee1 (amount, receiver, unwrap)
        (0, "0x0000000000000000000000000000000000000000", False)  # interfaceFee2 (amount, receiver, unwrap)
    ]

    # Step 3: ABI-encode the arguments for PLACE_ORDER
    encoded_args = web3.codec.encode(
        [
            "address",     # IMarket (address)
            "int8",        # Side
            "int8",        # Comparison
            "uint256",     # Fee
            "uint256",     # Price (now an integer)
            "int256",      # Delta (now an integer)
            "(uint256,address,bool)",  # InterfaceFee1
            "(uint256,address,bool)"   # InterfaceFee2
        ],
        place_take_profit_action
    )

    # Step 4: Create the invocation tuple with action type 3 (PLACE_ORDER)
    invocation_tuple = (3, encoded_args)  # 3 is for PLACE_ORDER

    # Step 5: Build the invocation array
    invocations = [invocation_tuple]

    base_fee_per_gas = web3.eth.fee_history(1, "latest")["baseFeePerGas"][-1]
    max_fee_per_gas = base_fee_per_gas + Web3.to_wei(2.2, 'gwei')

    take_profit_order_tx = multi_invoker_contract.functions.invoke(invocations).build_transaction({
        'from': account_address,
        'nonce': web3.eth.get_transaction_count(account_address),
        'gas': 2200000,
        "maxFeePerGas": max_fee_per_gas
    })

    # Step 6: Sign the transaction
    signed_take_profit_order_tx = web3.eth.account.sign_transaction(take_profit_order_tx, private_key=private_key)

    # Step 7: Send the raw transaction
    tx_hash_take_profit_order = web3.eth.send_raw_transaction(signed_take_profit_order_tx.raw_transaction)

    # Step 8: Wait for receipt
    web3.eth.wait_for_transaction_receipt(tx_hash_take_profit_order)

    return tx_hash_take_profit_order
