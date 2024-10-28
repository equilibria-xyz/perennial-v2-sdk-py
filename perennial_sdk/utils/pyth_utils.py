import requests
import time
from perennial_sdk.config import *

# Get VAA (Validator Action Approval)
def get_vaa(id, min_valid_time):

    # Construct the full URL with query parameters
    url = f"{pyth_url}?ids%5B%5D={id}"
    # Make the GET request
    response = requests.get(url)
    data = response.json()

    # Extract VAA data (base64-encoded) and publish time
    vaa_data = data['binary']['data'][0]
    parsed_data = data['parsed'][0]
    publish_time = parsed_data['price']['publish_time']

    return vaa_data, publish_time