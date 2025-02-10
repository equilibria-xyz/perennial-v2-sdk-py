from perennial_sdk.main.markets.snapshot_and_oracle_info import *
from perennial_sdk.constants import *
from perennial_sdk.utils.pyth_utils import *
from perennial_sdk.config import *
from perennial_sdk.utils import logger
from decimal import Decimal
from hexbytes import HexBytes

class TxExecutor:
    def __init__(self):
        pass
        
    def approve_usdc_to_multi_invoker(self, collateral_amount: float) -> str:
        """
        Approve a specified amount of USDC for the MultiInvoker contract.

        Args:
            collateral_amount (float): The amount of USDC (in decimal format) to approve.

        Returns:
            str: The transaction hash of the approval if successful.

            None: If an error occurs during the approval process.
        """
        try:
            amount_usdc = int(collateral_amount * 10 ** 6)

            approve_tx = USDC_CONTRACT.functions.approve(MULTI_INVOKER_ADDRESS, amount_usdc).build_transaction({
                'from': account_address,
                'nonce': web3.eth.get_transaction_count(account_address),
            })

            signed_approve_tx = web3.eth.account.sign_transaction(approve_tx, private_key)

            estimated_gas = web3.eth.estimate_gas(approve_tx)
            approve_tx["gas"] = estimated_gas

            fee_history = web3.eth.fee_history(1, "latest")
            base_fee_per_gas = fee_history["baseFeePerGas"][-1]
            max_priority_fee_per_gas = web3.eth.max_priority_fee
            max_fee_per_gas = base_fee_per_gas + max_priority_fee_per_gas

            approve_tx["maxFeePerGas"] = max_fee_per_gas
            approve_tx["maxPriorityFeePerGas"] = max_priority_fee_per_gas

            signed_approve_tx_hash = web3.eth.send_raw_transaction(signed_approve_tx.raw_transaction)
            tx_receipt = web3.eth.wait_for_transaction_receipt(signed_approve_tx_hash)

            if tx_receipt['status'] != 1:
                raise Exception
            else:
                logger.info(f'order_manager.py - Approved USDC to DSU contract.')
                return signed_approve_tx_hash.to_0x_hex()
        
        except Exception as e:
            logger.error(f'order_manager.py/approve_usdc_to_dsu() - Error while approving USDC to the DSU contract. Error: {e}', exc_info=True)
            return None

    def commit_price_to_multi_invoker(self, symbol: str) -> str:
        """
        Commit a price to the MultiInvoker contract for a specified market symbol.

        Args:
            symbol (str): The symbol of the market for which the price is being committed.

        Returns:
            str: The transaction hash of the price commit if successful.

            None: If an error occurs during the price commit process.
        """

        try:

            oracle_data = fetch_oracle_info(
                arbitrum_markets[symbol], market_provider_ids[symbol]
            )
            sub_oracle_factory_address = web3.to_checksum_address(oracle_data['sub_oracle_factory_address'])
            min_valid_time = oracle_data['min_valid_time']
            underlying_id = oracle_data['underlying_id']

            vaa_data, publish_time = get_vaa(underlying_id.hex(), min_valid_time)

            price_commit_action = {
                "keeperFactory": oracle_data['factory_address'],
                "version": publish_time-min_valid_time,
                "value": 1,
                "ids": [Web3.to_bytes(hexstr=underlying_id.hex())],
                "updateData":Web3.to_bytes(hexstr='0x'+vaa_data)
            }

            multi_invoker: Contract = web3.eth.contract(address=MULTI_INVOKER_ADDRESS, abi=MULTI_INVOKER_ABI)
            
            action = 6 
            args_encoded = Web3().codec.encode(
                ["address", "uint256", "bytes32[]", "uint256", "bytes", "bool"],
                [
                    sub_oracle_factory_address,
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
                "nonce": web3.eth.get_transaction_count(account_address),
                "value": 1
            })

            signed_tx = web3.eth.account.sign_transaction(transaction, private_key=private_key)

            estimated_gas = web3.eth.estimate_gas(transaction)
            transaction["gas"] = estimated_gas
            base_fee_per_gas = web3.eth.fee_history(1, "latest")["baseFeePerGas"][-1]
            max_priority_fee_per_gas = web3.eth.max_priority_fee
            max_fee_per_gas = base_fee_per_gas + max_priority_fee_per_gas
            transaction["maxFeePerGas"] = max_fee_per_gas

            tx_hash_commit = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
            tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash_commit)

            if tx_receipt['status'] != 1:
                raise Exception
            else:
                logger.info(f'order_manager.py - Price committed to MultiInvoker.')
                return tx_hash_commit.to_0x_hex()
        
        except Exception as e:
            logger.error(f'order_manager.py/commit_price_to_multi_invoker() - Error while commiting price to multi invoker contract. Error: {e}', exc_info=True)
            return None

    def close_position_in_market(self, symbol: str) -> str:
        try:
            update_position_action = [
                arbitrum_markets[symbol],  # IMarket (Market address)
                0,  # newMaker (UFixed6)
                0,  # newLong (UFixed6)
                0,  # newShort (UFixed6)
                0,  # collateral (Fixed6)
                False,  # wrap (bool)
                (0, "0x0000000000000000000000000000000000000000", False),  # interfaceFee1 (amount, receiver, unwrap)
                (0, "0x0000000000000000000000000000000000000000", False)  # interfaceFee2 (amount, receiver, unwrap)
            ]

            fee_history = web3.eth.fee_history(1, "latest")
            base_fee_per_gas = fee_history["baseFeePerGas"][-1]
            max_priority_fee_per_gas = web3.eth.max_priority_fee
            max_fee_per_gas = base_fee_per_gas + max_priority_fee_per_gas

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

            invocation_tuple = (1, encoded_args)  # 1 is for UPDATE_POSITION
            invocations = [invocation_tuple]

            update_tx = MULTI_INVOKER_CONTRACT.functions.invoke(invocations).build_transaction({
                'from': account_address,
                'nonce': web3.eth.get_transaction_count(account_address),
                "maxFeePerGas": max_fee_per_gas
            })

            estimated_gas = web3.eth.estimate_gas(update_tx)
            update_tx['gas'] = estimated_gas

            signed_update_tx = web3.eth.account.sign_transaction(update_tx, private_key=private_key)
            tx_hash_update = web3.eth.send_raw_transaction(signed_update_tx.raw_transaction)
            tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash_update)

            if tx_receipt['status'] != 1:
                raise Exception
            else:
                logger.info(f'order_manager.py - Position successfully closed in market {symbol}.')
                return tx_hash_update.to_0x_hex()

        except Exception as e:
            logger.error(f'order_manager.py/close_position_in_market() - Error while closing position in market {symbol}. Error: {e}', exc_info=True)
            return None

    def withdraw_collateral(self, symbol: str, snapshot: dict = None) -> str:
        """
        Withdraw collateral from a specified market.

        Args:
            symbol (str): The symbol of the market to withdraw collateral from.
            snapshot (dict, optional): A market snapshot. If not provided, a fresh snapshot will be fetched.

        Returns:
            str: The transaction hash of the withdrawal if successful.

            None: If an error occurs during the withdrawal process.
        """

        try:
            if not snapshot:
                snapshot = fetch_market_snapshot([symbol])
                post_update_collateral = snapshot["result"]["postUpdate"]["marketAccountSnapshots"][0]["local"]["collateral"]
            else:
                post_update_collateral = snapshot["postUpdate"]["marketAccountSnapshots"][0]["local"]["collateral"]

            update_position_action = [
                arbitrum_markets[symbol],  # IMarket (Market address)
                0,  # newMaker (UFixed6)
                0,  # newLong (UFixed6)
                0,  # newShort (UFixed6)
                -post_update_collateral,  # collateral (Fixed6)
                True,  # wrap (bool)
                (0, "0x0000000000000000000000000000000000000000", False),  # interfaceFee1 (amount, receiver, unwrap)
                (0, "0x0000000000000000000000000000000000000000", False)  # interfaceFee2 (amount, receiver, unwrap)
            ]

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

            invocation_tuple = (1, encoded_args)  # 1 is for UPDATE_POSITION
            invocations = [invocation_tuple]

            withdraw_tx = MULTI_INVOKER_CONTRACT.functions.invoke(invocations).build_transaction({
                'from': account_address,
                'nonce': web3.eth.get_transaction_count(account_address)
            })

            estimated_gas = web3.eth.estimate_gas(withdraw_tx)
            withdraw_tx['gas'] = estimated_gas

            fee_history = web3.eth.fee_history(1, "latest")
            base_fee_per_gas = fee_history["baseFeePerGas"][-1]
            max_priority_fee_per_gas = web3.eth.max_priority_fee
            max_fee_per_gas = base_fee_per_gas + max_priority_fee_per_gas
            withdraw_tx["maxFeePerGas"] = max_fee_per_gas

            signed_withdraw_tx = web3.eth.account.sign_transaction(withdraw_tx, private_key=private_key)
            tx_hash_withdraw = web3.eth.send_raw_transaction(signed_withdraw_tx.raw_transaction)
            tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash_withdraw)

            if tx_receipt['status'] != 1:
                raise Exception
            else:
                logger.info(f'order_manager.py - Collateral withdrawn successfully from market: {symbol}.')
                return tx_hash_withdraw.to_0x_hex()
        
        except Exception as e:
            logger.error(f'order_manager.py/withdraw_collateral() - Error while withdrawing collateral. Error: {e}', exc_info=True)
            return None

    def deposit_collateral(self, symbol: str, collateral_amount: float) -> str:
        """
        Deposit collateral into a specified market.

        Args:
            symbol (str): The symbol of the market to deposit collateral into.
            collateral_amount (float): The amount of collateral to deposit in USD.

        Returns:
            str: The transaction hash of the deposit if successful.

            None: If an error occurs during the deposit process.
        """
        try:
            self.approve_usdc_to_multi_invoker(collateral_amount)
            amount_usdc = int(collateral_amount * 1000000)

            deposit_collateral_action = [
                arbitrum_markets[symbol],  # IMarket (Market address)
                0,  # newMaker (UFixed6)
                0,  # newLong (UFixed6)
                0,  # newShort (UFixed6)
                amount_usdc,  # collateral (Fixed6)
                True,  # wrap (bool)
                (0, "0x0000000000000000000000000000000000000000", False),  # interfaceFee1 (amount, receiver, unwrap)
                (0, "0x0000000000000000000000000000000000000000", False)  # interfaceFee2 (amount, receiver, unwrap)
            ]

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

            invocation_tuple = (1, encoded_args)  # 1 is for UPDATE_POSITION
            invocations = [invocation_tuple]

            current_nonce = web3.eth.get_transaction_count(account_address)
            fee_history = web3.eth.fee_history(1, "latest")
            base_fee_per_gas = fee_history["baseFeePerGas"][-1]
            max_priority_fee_per_gas = web3.eth.max_priority_fee
            max_fee_per_gas = base_fee_per_gas + max_priority_fee_per_gas

            deposit_tx = MULTI_INVOKER_CONTRACT.functions.invoke(invocations).build_transaction({
                'from': account_address,
                'nonce': current_nonce,
                "maxFeePerGas": max_fee_per_gas
            })

            estimated_gas = web3.eth.estimate_gas(deposit_tx)
            deposit_tx['gas'] = estimated_gas

            signed_withdraw_tx = web3.eth.account.sign_transaction(deposit_tx, private_key=private_key)
            tx_hash_deposit= web3.eth.send_raw_transaction(signed_withdraw_tx.raw_transaction)
            tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash_deposit)

            if tx_receipt['status'] != 1:
                raise Exception
            else:
                logger.info(f'order_manager.py - Deposited collateral: {collateral_amount} USD.')
                return tx_hash_deposit.to_0x_hex()

        except Exception as e:
            logger.error(f'order_manager.py/deposit_collateral() - Error while depositing collateral. Error: {e}', exc_info=True)
            return None

    def place_market_order(
        self,
        symbol: str, 
        long_amount: float, 
        short_amount: float, 
        maker_amount: float, 
        collateral_amount: float
        ) -> str:

        """
        Place a market order in a specified market.

        Args:
            symbol (str): The symbol of the market to place the order in.
            long_amount (float): The amount to long, in units of the asset (e.g. 1 ETH would be 1, half an eth = 0.5, etc).
            short_amount (float): The amount to short, in units of the asset.
            maker_amount (float): The amount for the maker side of the market. Typically left as 0.
            collateral_amount (float): The collateral amount to back the position in USD.

        Returns:
            str: The transaction hash of the market order if successful.

            None: If an error occurs during the order placement process.
        """

        try:
            self.approve_usdc_to_multi_invoker(collateral_amount)

            place_market_order_action = [
                arbitrum_markets[symbol],  # IMarket (Market address)
                int(maker_amount*1e6),  # newMaker (UFixed6)
                int(long_amount*1e6),  # newLong (UFixed6)
                int(short_amount*1e6),  # newShort (UFixed6)
                int(collateral_amount*1e6),  # collateral (Fixed6)
                True,  # wrap (bool)
                (0, "0x0000000000000000000000000000000000000000", False),  # interfaceFee1 (amount, receiver, unwrap)
                (0, "0x0000000000000000000000000000000000000000", False)  # interfaceFee2 (amount, receiver, unwrap)
            ]

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

            invocation_tuple = (1, encoded_args)  # 1 is for UPDATE_POSITION
            invocations = [invocation_tuple]

            market_order_tx = MULTI_INVOKER_CONTRACT.functions.invoke(invocations).build_transaction({
                'from': account_address,
                'nonce': web3.eth.get_transaction_count(account_address)
            })

            estimated_gas = web3.eth.estimate_gas(market_order_tx)
            market_order_tx['gas'] = estimated_gas

            fee_history = web3.eth.fee_history(1, "latest")
            base_fee_per_gas = fee_history["baseFeePerGas"][-1]
            max_priority_fee_per_gas = web3.eth.max_priority_fee
            max_fee_per_gas = base_fee_per_gas + max_priority_fee_per_gas
            market_order_tx["maxFeePerGas"] = max_fee_per_gas

            signed_place_market_order_tx = web3.eth.account.sign_transaction(market_order_tx, private_key=private_key)
            tx_hash_place_market_order = web3.eth.send_raw_transaction(signed_place_market_order_tx.raw_transaction)
            tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash_place_market_order)

            if tx_receipt['status'] != 1:
                raise Exception
            else:
                logger.info(f'order_manager.py - Market order executed on market: {symbol}.')
                return tx_hash_place_market_order.to_0x_hex()
        
        except Exception as e:
            logger.error(f'order_manager.py/place_market_order() - Error while placing market order for market: {symbol}. Error: {e}', exc_info=True)
            return None

    def place_limit_order(self, symbol: str, side: int, price: float, delta: float) -> str:
        """
        Place a limit order in a specified market.

        Args:
            symbol (str): The symbol of the market to place the limit order in.
            side (int): The side of the order (1 for long, 2 for short).
            price (float): The limit price for the order.
            delta (float): The delta amount for the order (measured in whole units of the asset).

        Returns:
            str: The transaction hash of the limit order if successful.

            None: If an error occurs during the order placement process.
        """
        try:
            global comparison
            if side==1: comparison=-1
            elif side == 2: comparison=1

            place_limit_order_action = [
                arbitrum_markets[symbol],  # IMarket (Market address)
                side,  # Side = 1 to Buy; 2 to Short
                comparison,  # Comparison -1 if long; 1 if short.
                20 * 1000000,  # Max fee (multiply by 1e6)
                int(price * 1000000),  # Price (convert to int)
                int(delta * 1000000),  # Delta (convert to int)
                (0, "0x8cda59615c993f925915d3eb4394badb3feef413", False),  # interfaceFee1 (amount, receiver, unwrap)
                (0, "0x0000000000000000000000000000000000000000", False)  # interfaceFee2 (amount, receiver, unwrap)
            ]

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


            invocation_tuple = (3, encoded_args) 
            invocations = [invocation_tuple]

            

            limit_order_tx = MULTI_INVOKER_CONTRACT.functions.invoke(invocations).build_transaction({
                'from': account_address,
                'nonce': web3.eth.get_transaction_count(account_address)
            })

            signed_place_limit_order_tx = web3.eth.account.sign_transaction(limit_order_tx, private_key=private_key)

            estimated_gas = web3.eth.estimate_gas(limit_order_tx)
            limit_order_tx['gas'] = estimated_gas
            fee_history = web3.eth.fee_history(1, "latest")
            base_fee_per_gas = fee_history["baseFeePerGas"][-1]
            max_priority_fee_per_gas = web3.eth.max_priority_fee
            max_fee_per_gas = base_fee_per_gas + max_priority_fee_per_gas
            limit_order_tx['maxFeePerGas'] = max_fee_per_gas

            tx_hash_place_limit_order = web3.eth.send_raw_transaction(signed_place_limit_order_tx.raw_transaction)
            tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash_place_limit_order)

            if tx_receipt['status'] != 1:
                raise Exception
            else:
                logger.info(f'order_manager.py - Placed limit order on market address {symbol}.')
                return tx_hash_place_limit_order.to_0x_hex()
        
        except Exception as e:
            logger.error(f'order_manager.py/place_limit_order() - Error while placing limit order for market {symbol}. Error: {e}', exc_info=True)
            return None

    def cancel_order(self, symbol: str, nonce: int) -> str:
        """
        Cancel a limit order in a specified market.

        Args:
            symbol (str): The symbol of the market where the order is placed.
            nonce (int): The nonce of the order to be canceled.

        Returns:
            str: The transaction hash of the cancel order if successful.

            None: If an error occurs during the cancellation process.
        """
        try:
            cancel_order_action = [arbitrum_markets[symbol], nonce]
            cancel_args = web3.codec.encode([
                "address",
                "uint256"
            ],
            cancel_order_action)

            cancel_invocation_tuple = (4, cancel_args)

            cancel_invocations = [cancel_invocation_tuple]

            cancel_order_tx = MULTI_INVOKER_CONTRACT.functions.invoke(cancel_invocations).build_transaction({
                'from': account_address,
                'nonce': web3.eth.get_transaction_count(account_address)
            })

            
            estimated_gas = web3.eth.estimate_gas(cancel_order_tx)
            cancel_order_tx['gas'] = estimated_gas

            fee_history = web3.eth.fee_history(1, "latest")
            base_fee_per_gas = fee_history["baseFeePerGas"][-1]
            max_priority_fee_per_gas = web3.eth.max_priority_fee
            max_fee_per_gas = base_fee_per_gas + max_priority_fee_per_gas
            cancel_order_tx["maxFeePerGas"] = max_fee_per_gas

            signed_cancel_order_tx = web3.eth.account.sign_transaction(cancel_order_tx, private_key=private_key)
            tx_hash_cancel_order = web3.eth.send_raw_transaction(signed_cancel_order_tx.raw_transaction)
            tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash_cancel_order)

            if tx_receipt['status'] != 1:
                raise Exception
            else:
                logger.info(f'order_manager.py - Canceled limit order on market address {symbol}.')
                return tx_hash_cancel_order.to_0x_hex()
        
        except Exception as e:
            logger.error(f'order_manager.py/cancel_order() - Error while cancelling order for market {symbol}. Error: {e}', exc_info=True)
            return None

    def cancel_list_of_orders(self, symbol: str, nonces: list) -> str:
        """
        Cancel a list of limit orders in a specified market.

        Args:
            symbol (str): The symbol of the market where the orders are placed.
            nonces (list): A list of nonces corresponding to the orders to be canceled.

        Returns:
            str: The transaction hash of the cancel operation if successful.

            None: If an error occurs during the cancellation process.
        """

        try:
            cancel_invocations = []

            for nonce in nonces:
                cancel_order_action = [arbitrum_markets[symbol], nonce]
                cancel_args = web3.codec.encode([
                    "address",
                    "uint256"
                ], cancel_order_action)

                cancel_invocation_tuple = (4, cancel_args)
                cancel_invocations.append(cancel_invocation_tuple)

            cancel_order_tx = MULTI_INVOKER_CONTRACT.functions.invoke(cancel_invocations).build_transaction({
                'from': account_address,
                'nonce': web3.eth.get_transaction_count(account_address),

            })

            fee_history = web3.eth.fee_history(1, "latest")
            base_fee_per_gas = fee_history["baseFeePerGas"][-1]
            max_priority_fee_per_gas = web3.eth.max_priority_fee
            max_fee_per_gas = base_fee_per_gas + max_priority_fee_per_gas
            cancel_order_tx["maxFeePerGas"] = max_fee_per_gas

            estimated_gas = web3.eth.estimate_gas(cancel_order_tx)
            cancel_order_tx['gas'] = estimated_gas

            signed_cancel_order_tx = web3.eth.account.sign_transaction(cancel_order_tx, private_key=private_key)
            tx_hash_cancel_all_orders = web3.eth.send_raw_transaction(signed_cancel_order_tx.raw_transaction)
            tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash_cancel_all_orders)

            if tx_receipt['status'] != 1:
                raise Exception
            else:
                logger.info(f'order_manager.py - Canceled a list of orders on market address {symbol}.')
                return tx_hash_cancel_all_orders.to_0x_hex()
        
        except Exception as e:
            logger.error(f'order_manager.py/cancel_list_of_orders() - Error while cancelling order for market {symbol}. Error: {e}', exc_info=True)
            return None


    def place_stop_loss_order(self, symbol: str, side: int, price: float, delta: float) -> str:
        """
        Place a stop-loss order in a specified market.

        Args:
            symbol (str): The symbol of the market where the stop-loss order is to be placed.
            side (int): The order side; 1 for Long (Buy), 2 for Short (Sell).
            price (float): The stop-loss trigger price.
            delta (float): The delta value for the stop-loss order.

        Returns:
            str: The transaction hash of the stop-loss order if successfully placed.

            None: If an error occurs during the stop-loss order placement.
        """
        try:

            global comparison
            if side == 1:
                comparison = -1
            elif side == 2:
                comparison = 1

            place_stop_loss_action = [
                arbitrum_markets[symbol],  # IMarket (Market address)
                side,  # Side - 1 to Buy; 2 to Short
                comparison,  # Comparison -1 if long; 1 if short.
                20 * 1000000,  # Max fee (multiply by 1e6)
                int(price * 1000000),  # Price (convert to int)
                int(delta * 1000000),  # Delta (convert to int)
                (0, "0x8cda59615c993f925915d3eb4394badb3feef413", False),  # interfaceFee1 (amount, receiver, unwrap)
                (0, "0x0000000000000000000000000000000000000000", False)  # interfaceFee2 (amount, receiver, unwrap)
            ]

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

            invocation_tuple = (3, encoded_args)  # 3 is for PLACE_ORDER
            invocations = [invocation_tuple]

            stop_loss_order_tx = MULTI_INVOKER_CONTRACT.functions.invoke(invocations).build_transaction({
                'from': account_address,
                'nonce': web3.eth.get_transaction_count(account_address),
            })

            estimated_gas = web3.eth.estimate_gas(stop_loss_order_tx)
            stop_loss_order_tx['gas'] = estimated_gas

            fee_history = web3.eth.fee_history(1, "latest")
            base_fee_per_gas = fee_history["baseFeePerGas"][-1]
            max_priority_fee_per_gas = web3.eth.max_priority_fee
            max_fee_per_gas = base_fee_per_gas + max_priority_fee_per_gas
            stop_loss_order_tx["maxFeePerGas"] = max_fee_per_gas

            signed_stop_loss_order_tx = web3.eth.account.sign_transaction(stop_loss_order_tx, private_key=private_key)
            tx_hash_stop_loss_order = web3.eth.send_raw_transaction(signed_stop_loss_order_tx.raw_transaction)
            tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash_stop_loss_order)

            if tx_receipt['status'] != 1:
                raise Exception
            else:
                logger.info(f'order_manager.py - Placed stop-loss order on market address {symbol}.')
                return tx_hash_stop_loss_order.to_0x_hex()
        
        except Exception as e:
            logger.error(f'order_manager.py/place_stop_loss_order() - Error while placing stop-loss order for market {symbol}. Error: {e}', exc_info=True)
            return None

    def place_take_profit_order(self, symbol: str, side: int, price: float, delta:float) -> str:
        """
        Place a take-profit order in a specified market.

        Args:
            symbol (str): The symbol of the market where the take-profit order is to be placed.
            side (int): The order side; 1 for Long (Buy), 2 for Short (Sell).
            price (float): The take-profit trigger price.
            delta (float): The delta value for the take-profit order.

        Returns:
            str: The transaction hash of the take-profit order if successfully placed.

            None: If an error occurs during the take-profit order placement.
        """
        try:
            global comparison
            if side==1: comparison=1
            elif side == 2: comparison=-1

            place_take_profit_action = [
                arbitrum_markets[symbol],  # IMarket (Market address)
                side,  # Side - 1 to Buy; 2 to Short
                comparison,  # Comparison -1 if long; 1 if short.
                20 * 1000000,  # Max fee (multiply by 1e6)
                int(price * 1000000),  # Price (convert to int)
                int(delta * 1000000),  # Delta (convert to int)
                (0, "0x8cda59615c993f925915d3eb4394badb3feef413", False),  # interfaceFee1 (amount, receiver, unwrap)
                (0, "0x0000000000000000000000000000000000000000", False)  # interfaceFee2 (amount, receiver, unwrap)
            ]

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

            invocation_tuple = (3, encoded_args)  # 3 is for PLACE_ORDER
            invocations = [invocation_tuple]

            take_profit_order_tx = MULTI_INVOKER_CONTRACT.functions.invoke(invocations).build_transaction({
                'from': account_address,
                'nonce': web3.eth.get_transaction_count(account_address),
            })

            estimated_gas = web3.eth.estimate_gas(take_profit_order_tx)
            take_profit_order_tx['gas'] = estimated_gas

            fee_history = web3.eth.fee_history(1, "latest")
            base_fee_per_gas = fee_history["baseFeePerGas"][-1]
            max_priority_fee_per_gas = web3.eth.max_priority_fee
            max_fee_per_gas = base_fee_per_gas + max_priority_fee_per_gas
            take_profit_order_tx["maxFeePerGas"] = max_fee_per_gas

            take_profit_order_tx = web3.eth.account.sign_transaction(take_profit_order_tx, private_key=private_key)
            tx_hash_stop_loss_order = web3.eth.send_raw_transaction(take_profit_order_tx.raw_transaction)
            tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash_stop_loss_order)

            if tx_receipt['status'] != 1:
                raise Exception
            else:
                logger.info(f'order_manager.py - Placed take profit order on market {symbol}.')
                return tx_hash_stop_loss_order.to_0x_hex()
        
        except Exception as e:
            logger.error(f'order_manager.py/place_take_profit_order() - Error while placing take profit order for market {symbol}. Error: {e}', exc_info=True)
            return None
