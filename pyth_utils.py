import requests
import time


def get_vaa(id, min_valid_time):
    """
    Fetch a Verifiable Asset Address (VAA) from the Pyth Network.

    Args:
    id (str): The identifier for the VAA.
    min_valid_time (int): Minimum time in seconds for which the VAA should be valid.

    Returns:
    tuple: A tuple containing the VAA and its publish time.
    """
    # Define the base URL and endpoint
    pyth_url = "https://hermes.pyth.network/api/get_vaa"

    # Calculate the query time
    current_time = int(time.time())
    query_time = current_time - min_valid_time

    # Construct the full URL with query parameters
    url = f"{pyth_url}?id={id}&publish_time={query_time}"

    # Make the GET request
    response = requests.get(url)
    data = response.json()

    # Return the VAA and publish time
    return data["vaa"], data["publishTime"]
