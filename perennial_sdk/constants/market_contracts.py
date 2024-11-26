from perennial_sdk.config.connection import *
from perennial_sdk.constants import *
from perennial_sdk.abi import *

usdc_contract = web3.eth.contract(address=USDC_ADDRESS,abi=usdc_abi)
dsu_contract = web3.eth.contract(address=DSU_ADDRESS,abi=dsu_abi)
multi_invoker_contract = web3.eth.contract(address=MULTI_INVOKER_ADDRESS,abi=multi_invoker_abi)