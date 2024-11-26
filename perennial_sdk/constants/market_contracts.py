from perennial_sdk.config.connection import *
from perennial_sdk.constants import *
from perennial_sdk.abi import *

usdc_contract = web3.eth.contract(address=USDC_ADDRESS,abi=USDC_ABI)
dsu_contract = web3.eth.contract(address=DSU_ADDRESS,abi=DSU_ABI)
multi_invoker_contract = web3.eth.contract(address=MULTI_INVOKER_ADDRESS,abi=MULTI_INVOKER_ABI)