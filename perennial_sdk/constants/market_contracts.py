from perennial_sdk.config.connection import *
from perennial_sdk.constants import *
from perennial_sdk.abi import *
from web3.contract import Contract

USDC_CONTRACT: Contract = web3.eth.contract(address=USDC_ADDRESS,abi=USDC_ABI)
DSU_CONTRACT: Contract = web3.eth.contract(address=DSU_ADDRESS,abi=DSU_ABI)
MULTI_INVOKER_CONTRACT: Contract = web3.eth.contract(address=MULTI_INVOKER_ADDRESS,abi=MULTI_INVOKER_ABI)