import requests
import time
from perennial_sdk.config import *
from perennial_sdk.utils.logger import logger

# Get VAA (Validator Action Approval)
def get_vaa(id, min_valid_time):
    try:

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
    
    except Exception as e:
        logger.error(f'pyth_utils.py/get_vaa() - Error while calling VAA data: {e}', exc_info=True)
        return None