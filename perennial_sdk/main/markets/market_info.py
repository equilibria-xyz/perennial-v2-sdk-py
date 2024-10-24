from perennial_sdk.main.markets import *
from perennial_sdk.utils.calc_funding_rate_draft_two import calculate_funding_and_interest_for_sides

class MarketPriceInfo:
    def __init__(self, market, pre_update_price, latest_price):
        self.market = market
        self.pre_update_price = pre_update_price
        self.latest_price = latest_price

    def __str__(self):
        return (f"Market Price Info:\n"
                f"Market: {self.market}\n"
                f"Pre-update Market Price: ${self.pre_update_price}\n"
                f"Latest Market Price: ${self.latest_price}\n")

class MarketFundingRateInfo:
    def __init__(self, market, funding_fee_long_annual, funding_fee_long_hourly, interest_fee_long_annual,
                 interest_fee_long_hourly, funding_rate_long_annual, funding_rate_long_hourly,
                 funding_fee_short_annual, funding_fee_short_hourly, interest_fee_short_annual,
                 interest_fee_short_hourly, funding_rate_short_annual, funding_rate_short_hourly):
        self.market = market
        self.funding_fee_long_annual = funding_fee_long_annual
        self.funding_fee_long_hourly = funding_fee_long_hourly
        self.interest_fee_long_annual = interest_fee_long_annual
        self.interest_fee_long_hourly = interest_fee_long_hourly
        self.funding_rate_long_annual = funding_rate_long_annual
        self.funding_rate_long_hourly = funding_rate_long_hourly
        self.funding_fee_short_annual = funding_fee_short_annual
        self.funding_fee_short_hourly = funding_fee_short_hourly
        self.interest_fee_short_annual = interest_fee_short_annual
        self.interest_fee_short_hourly = interest_fee_short_hourly
        self.funding_rate_short_annual = funding_rate_short_annual
        self.funding_rate_short_hourly = funding_rate_short_hourly

    def __str__(self):
        return (f"Market Funding Rate Info:\n"
                f"Market: {self.market}\n"
                f"Funding Fee LONG (Hourly): {self.funding_fee_long_hourly}% | (Annual): {self.funding_fee_long_annual}%\n"
                f"Interest Fee LONG (Hourly): {self.interest_fee_long_hourly}% | (Annual): {self.interest_fee_long_annual}%\n"
                f"Funding Rate LONG (Hourly): {self.funding_rate_long_hourly}% | (Annual): {self.funding_rate_long_annual}%\n"
                f"Funding Fee SHORT (Hourly): {self.funding_fee_short_hourly}% | (Annual): {self.funding_fee_short_annual}%\n"
                f"Interest Fee SHORT (Hourly): {self.interest_fee_short_hourly}% | (Annual): {self.interest_fee_short_annual}%\n"
                f"Funding Rate SHORT (Hourly): {self.funding_rate_short_hourly}% | (Annual): {self.funding_rate_short_annual}%\n")

class MarginMaintenanceInfo:
    def __init__(self, market, margin_fee, min_margin, maintenance_fee, min_maintenance):
        self.market = market
        self.margin_fee = margin_fee
        self.min_margin = min_margin
        self.maintenance_fee = maintenance_fee
        self.min_maintenance = min_maintenance

    def __str__(self):
        return (f"Margin Maintenance Info:\n"
                f"Market: {self.market}\n"
                f"Margin Fee: {self.margin_fee}%\n"
                f"Min Margin: ${self.min_margin}\n"
                f"Maintenance Fee: {self.maintenance_fee}%\n"
                f"Min Maintenance: ${self.min_maintenance}\n")

class MarketInfo:
    def __init__(self, market_ad):
        self.market_ad = market_ad

    @staticmethod
    def fetch_market_price(market_address):
        snapshot = fetch_market_snapshot([market_address])
        pre_update_market_price = snapshot["result"]["preUpdate"]["marketSnapshots"][0]["global"]["latestPrice"] / 1e6
        latest_market_price = snapshot["result"]["postUpdate"]["marketSnapshots"][0]["global"]["latestPrice"] / 1e6

        return MarketPriceInfo(market=market_address.upper(),
                               pre_update_price=pre_update_market_price,
                               latest_price=latest_market_price)

    @staticmethod
    def fetch_market_funding_rate(market_address):
        snapshot = fetch_market_snapshot([market_address])

        (funding_fee_long_annual, funding_fee_long_hourly, interest_fee_long_annual, interest_fee_long_hourly,
         funding_rate_long_annual, funding_rate_long_hourly, funding_fee_short_annual, funding_fee_short_hourly,
         interest_fee_short_annual, interest_fee_short_hourly, funding_rate_short_annual,
         funding_rate_short_hourly) = calculate_funding_and_interest_for_sides(snapshot)

        return MarketFundingRateInfo(
            market=market_address.upper(),
            funding_fee_long_annual=funding_fee_long_annual,
            funding_fee_long_hourly=funding_fee_long_hourly,
            interest_fee_long_annual=interest_fee_long_annual,
            interest_fee_long_hourly=interest_fee_long_hourly,
            funding_rate_long_annual=funding_rate_long_annual,
            funding_rate_long_hourly=funding_rate_long_hourly,
            funding_fee_short_annual=funding_fee_short_annual,
            funding_fee_short_hourly=funding_fee_short_hourly,
            interest_fee_short_annual=interest_fee_short_annual,
            interest_fee_short_hourly=interest_fee_short_hourly,
            funding_rate_short_annual=funding_rate_short_annual,
            funding_rate_short_hourly=funding_rate_short_hourly
        )

    @staticmethod
    def fetch_margin_maintenance_info(market_address):
        snapshot = fetch_market_snapshot([market_address])

        margin_fee = snapshot["result"]["postUpdate"]["marketSnapshots"][0]["riskParameter"]["margin"] / 1e4
        min_margin = snapshot["result"]["postUpdate"]["marketSnapshots"][0]["riskParameter"]["minMargin"] / 1e6
        maintenance_fee = snapshot["result"]["postUpdate"]["marketSnapshots"][0]["riskParameter"]["maintenance"] / 1e4
        min_maintenance = snapshot["result"]["postUpdate"]["marketSnapshots"][0]["riskParameter"]["minMaintenance"] / 1e6

        return MarginMaintenanceInfo(
            market=market_address.upper(),
            margin_fee=margin_fee,
            min_margin=min_margin,
            maintenance_fee=maintenance_fee,
            min_maintenance=min_maintenance
        )
