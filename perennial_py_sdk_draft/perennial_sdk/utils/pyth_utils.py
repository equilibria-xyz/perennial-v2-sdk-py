import requests
import time

# Get VAA (Validator Action Approval)
def get_vaa(id, min_valid_time):

    # pyth_url = "https://hermes.pyth.network/api/get_vaa" OLDDDDDD
    pyth_url = "https://hermes.pyth.network/v2/updates/price/latest"

    # Calculate the query time
    current_time = int(time.time())
    query_time = current_time - min_valid_time

    # Construct the full URL with query parameters
    # url = f"{pyth_url}?id={id}&publish_time={query_time}" OLDDD
    url = f"{pyth_url}?ids%5B%5D={id}"

    # Make the GET request
    response = requests.get(url)
    data = response.json()

    # Extract VAA data (base64-encoded) and publish time
    vaa_data = data['binary']['data'][0]
    parsed_data = data['parsed'][0]
    publish_time = parsed_data['price']['publish_time']

    return vaa_data, publish_time