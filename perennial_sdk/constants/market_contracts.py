from perennial_sdk.config.connection import *
from perennial_sdk.constants import *
from perennial_sdk.abi import *

usdc_contract = web3.eth.contract(address=usdc_address,abi=usdc_abi)
dsu_contract = web3.eth.contract(address=dsu_address,abi=dsu_abi)
multi_invoker_contract = web3.eth.contract(address=multi_invoker_address,abi=multi_invoker_abi)