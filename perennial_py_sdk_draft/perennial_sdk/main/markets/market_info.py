# TODO fetch_market_volume

from perennial_sdk.main.markets import *
from perennial_sdk.utils.calc_funding_rate_draft_two import calculate_funding_and_interest_for_sides


class MarketInfo:
    def __init__(self, market_ad):
        self.market_ad = market_ad

    def fetch_market_price(self, account_address, market_address):

        snapshot = fetch_market_snapshot([market_address], account_address)
        pre_update_market_price = snapshot["result"]["preUpdate"]["marketSnapshots"][0]["global"]["latestPrice"] / 1000000
        latest_market_price = snapshot["result"]["postUpdate"]["marketSnapshots"][0]["global"]["latestPrice"] / 1000000

        market_price_info = {
            'Market': market_address.upper(),
            'Pre update market price': pre_update_market_price,
            'Latest market price': latest_market_price
        }
        return market_price_info, latest_market_price, pre_update_market_price

    def fetch_market_funding_rate(self, account_address, market_address):

        # Generate current market snapshot:
        snapshot = fetch_market_snapshot([market_address], account_address)

        # Set needed variables:
        (funding_fee_long_annual, funding_fee_long_hourly, interest_fee_long_annual, interest_fee_long_hourly,
         funding_rate_long_annual, funding_rate_long_hourly, funding_fee_short_annual, funding_fee_short_hourly,
         interest_fee_short_annual, interest_fee_short_hourly, funding_rate_short_annual,
         funding_rate_short_hourly) = calculate_funding_and_interest_for_sides(snapshot)

        # Structure data in a dictionary
        market_funding_rate = {
            'Market': market_address.upper(),
            'Funding  fee  LONG':  {'hourly': funding_fee_long_hourly, 'annual': funding_fee_long_annual},
            'Interest fee  LONG':  {'hourly': interest_fee_long_hourly, 'annual': interest_fee_long_annual},
            'Funding  rate LONG':  {'hourly': funding_rate_long_hourly, 'annual': funding_rate_long_annual},
            'Funding  fee  SHORT': {'hourly': funding_fee_short_hourly, 'annual': funding_fee_short_annual},
            'Interest fee  SHORT': {'hourly': interest_fee_short_hourly, 'annual': interest_fee_short_annual},
            'Funding  rate SHORT': {'hourly': funding_rate_short_hourly, 'annual': funding_rate_short_annual}
        }
        return (market_funding_rate,funding_fee_long_annual, funding_fee_long_hourly, interest_fee_long_annual,
                interest_fee_long_hourly, funding_rate_long_annual, funding_rate_long_hourly, funding_fee_short_annual,
                funding_fee_short_hourly, interest_fee_short_annual, interest_fee_short_hourly, funding_rate_short_annual,
                funding_rate_short_hourly)

    def fetch_margin_maintenance_info(self, account_address, market_address):

        # Generate current market snapshot:
        snapshot = fetch_market_snapshot([market_address], account_address)

        # Extract the needed margin and maintenance fee data
        margin_fee = snapshot["result"]["postUpdate"]["marketSnapshots"][0]["riskParameter"]["margin"] / 10000
        min_margin = snapshot["result"]["postUpdate"]["marketSnapshots"][0]["riskParameter"]["minMargin"] / 1000000
        maintenance_fee = snapshot["result"]["postUpdate"]["marketSnapshots"][0]["riskParameter"]["maintenance"] / 10000
        min_maintenance = snapshot["result"]["postUpdate"]["marketSnapshots"][0]["riskParameter"][
                              "minMaintenance"] / 1000000

        # Structure the data in a dictionary
        margin_maintenance_info = {
            'Market': market_address.upper(),
            'Margin fee %': margin_fee,
            'Min margin USD': min_margin,
            'Maintenance fee %': maintenance_fee,
            'Min maintenance USD': min_maintenance
        }
        return margin_maintenance_info,margin_fee,min_margin,maintenance_fee,min_maintenance

