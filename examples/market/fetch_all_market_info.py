from perennial_sdk.main.markets.market_info import MarketInfo
from perennial_sdk.config import *

market_address = "bnb"

def display_market_price_info(market_info):
    """Display the market price information."""
    print('---------------------------------------------------------------')
    print(f"Market:                     {market_info.market}")
    print('---------------------------------------------------------------')
    print(f"Market price pre update:    {market_info.pre_update_price:.2f} USD")
    print(f"Latest market price:        {market_info.latest_price:.2f} USD")
    print('---------------------------------------------------------------')

def display_margin_maintenance_info(margin_info):
    """Display the margin and maintenance information."""
    print(f"Margin fee (Min.):          {margin_info.margin_fee}% ({margin_info.min_margin} USD)")
    print(f"Maintenance fee (Min.):     {margin_info.maintenance_fee}% ({margin_info.min_maintenance} USD)")
    print('---------------------------------------------------------------')

def display_funding_rate_info(long_hourly, long_annual, short_hourly, short_annual, label):
    """Display the funding rate information for a given label."""
    print(f"{label} (LONG):   {long_hourly}% (hourly) / {long_annual}% (annual)")
    print(f"{label} (SHORT):  {short_hourly}% (hourly) / {short_annual}% (annual)")
    print('---------------------------------------------------------------')

def print_market_info(account_address: str, market_address:str) -> None:
    """Fetch and display market information for the specified market."""
    # Fetch all the relevant data
    market_info = MarketInfo(account_address)
    market_price_info = market_info.fetch_market_price(market_address)
    funding_rate_info = market_info.fetch_market_funding_rate(market_address)
    margin_info = market_info.fetch_margin_maintenance_info(market_address)

    # Display fetched information
    display_market_price_info(market_price_info)
    display_margin_maintenance_info(margin_info)
    display_funding_rate_info(
        funding_rate_info.funding_fee_long_hourly, funding_rate_info.funding_fee_long_annual,
        funding_rate_info.funding_fee_short_hourly, funding_rate_info.funding_fee_short_annual, "Funding fee"
    )
    display_funding_rate_info(
        funding_rate_info.interest_fee_long_hourly, funding_rate_info.interest_fee_long_annual,
        funding_rate_info.interest_fee_short_hourly, funding_rate_info.interest_fee_short_annual, "Interest fee"
    )
    display_funding_rate_info(
        funding_rate_info.funding_rate_long_hourly, funding_rate_info.funding_rate_long_annual,
        funding_rate_info.funding_rate_short_hourly, funding_rate_info.funding_rate_short_annual, "Funding rate"
    )

if __name__ == "__main__":
    print_market_info(account_address, market_address)
