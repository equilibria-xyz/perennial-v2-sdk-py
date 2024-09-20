from perennial_sdk.main.markets.market_info import MarketInfo
from perennial_sdk.config import *


market_address = "link"
account_address = account_address

def print_market_info(account_address, market_address):
    # Fetch all the relevant data
    market_price_info, latest_market_price, pre_update_market_price = MarketInfo.fetch_market_price(account,account_address, market_address)
    (market_funding_rate, funding_fee_long_annual, funding_fee_long_hourly, interest_fee_long_annual,
     interest_fee_long_hourly, funding_rate_long_annual, funding_rate_long_hourly, funding_fee_short_annual,
     funding_fee_short_hourly, interest_fee_short_annual, interest_fee_short_hourly, funding_rate_short_annual,
     funding_rate_short_hourly) = MarketInfo.fetch_market_funding_rate(account,account_address, market_address)
    margin_maintenance_info, margin_fee, min_margin, maintenance_fee, min_maintenance = MarketInfo.fetch_margin_maintenance_info(account,
        account_address, market_address)

    # Print the market price info
    print('---------------------------------------------------------------')
    print(f"Market:                     {market_address.upper()}")
    print('---------------------------------------------------------------')
    print(f"Market price pre update:    {pre_update_market_price:.2f} USD")
    print(f"Latest market price:        {latest_market_price:.2f} USD")
    print('---------------------------------------------------------------')

    # Print the margin and maintenance info
    print(f"Margin fee (Min.):          {margin_fee}% ({min_margin} USD)")
    print(f"Maintenance fee (Min.):     {maintenance_fee}% ({min_maintenance} USD)")
    print('---------------------------------------------------------------')

    # Print the funding rate info
    print(f"Funding fee (LONG):   {funding_fee_long_hourly}% (hourly) / {funding_fee_long_annual}% (annual)")
    print(f"Interest fee (LONG):  {interest_fee_long_hourly}% (hourly) / {interest_fee_long_annual}% (annual)")
    print(f"Funding rate (LONG):  {funding_rate_long_hourly}% (hourly) / {funding_rate_long_annual}% (annual)")
    print('---------------------------------------------------------------')
    print(f"Funding fee (SHORT):  {funding_fee_short_hourly}% (hourly) / {funding_fee_short_annual}% (annual)")
    print(f"Interest fee (SHORT): {interest_fee_short_hourly}% (hourly) / {interest_fee_short_annual}% (annual)")
    print(f"Funding rate (SHORT): {funding_rate_short_hourly}% (hourly) / {funding_rate_short_annual}% (annual)")
    print('---------------------------------------------------------------')


print_market_info(account_address, market_address)
