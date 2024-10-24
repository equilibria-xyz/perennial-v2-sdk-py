from eth_abi import decode
from web3 import Web3


def get_type(lst, t):
    """
    Process a list of ABI items and generate a string or list representation of their types.

    Handles simple types, tuples, and arrays of tuples recursively. Useful for creating
    type strings for Ethereum ABI encoding/decoding operations.

    Args:
        lst (list): A list of ABI items, each a dict containing at least a 'type' key.
        t (bool): If True, return a comma-separated string of types; if False, return a list.

    Returns:
        str or list: A comma-separated string of types if t is True, otherwise a list of types.
    """
    result = []  # Initialize an empty list to store the processed types
    for item in lst:
        item_type = item["type"]  # Extract the 'type' from the current item
        if item_type == "tuple":
            # If it's a tuple, recursively process its components
            component_type = f"({get_type(item['components'], True)})"
        elif item_type == "tuple[]":
            # If it's an array of tuples, recursively process the tuple components
            # and append '[]' to indicate it's an array
            component_type = f"({get_type(item['components'], True)})[]"
        else:
            # For all other types (int, uint, address, etc.), use the type as is
            component_type = item_type

        result.append(component_type)  # Add the processed type to the result list

    if t:
        # If t is True, join the types with commas and return as a string
        return ",".join(result)
    # If t is False, return the list of types
    return result

def label_data_with_abi(data, abi):
    """
    Label a data structure according to the provided ABI (Application Binary Interface).

    Recursively processes the data, handling tuples, arrays of tuples, and other array types.

    Args:
        data (list): The data structure to be labeled.
        abi (list): The ABI structure describing the data format.

    Returns:
        dict: A dictionary where keys are field names from the ABI and values are the labeled data.

    Note:
        This function uses recursive helper functions to handle nested structures.
    """

    # Helper function to label individual items in the data structure
    def label_item(item, abi_type):
        if abi_type["type"] == "tuple":
            # If the item is a tuple, recursively label its components
            return label_tuple(item, abi_type["components"])
        elif abi_type["type"] == "tuple[]":
            # If the item is an array of tuples, label each tuple in the array
            return [label_tuple(sub_item, abi_type["components"]) for sub_item in item]
        elif abi_type["type"].endswith("[]"):
            # If the item is an array, label each item in the array
            return [
                label_item(sub_item, {"type": abi_type["type"][:-2]})
                for sub_item in item
            ]
        elif abi_type["type"] == "bytes":
            return "0x" + item.hex()
        else:
            return item

    # Helper function to label tuple data
    def label_tuple(tuple_data, tuple_abi):
        result = {}
        # Iterate through the data items
        for i, data_item in enumerate(tuple_data):
            # Label the data item and add it to the result dictionary
            # using the corresponding ABI name as the key
            result[tuple_abi[i]["name"]] = label_item(data_item, tuple_abi[i])
        return result

    # Start the labeling process by treating the top-level data as a tuple
    return label_tuple(data, abi)

def decode_call_data(data, func, abi):
    func_fragment = next(filter(lambda v: v["name"] == func, abi), None)
    outputs = func_fragment["outputs"]

    ## Convert outputs to a types string
    types = get_type(outputs, False)

    ## Use types to decode the return data
    decoded = decode(types, Web3.to_bytes(hexstr=data))

    ## Label & Return the decoded data
    return label_data_with_abi(decoded, outputs)
