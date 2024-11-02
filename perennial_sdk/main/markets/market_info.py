from perennial_sdk.main.markets import *
from perennial_sdk.utils.calc_funding_rate_draft_two import calculate_funding_and_interest_for_sides

class MarketPriceInfo:
    def __init__(self, market, pre_update_price, latest_price):
        self.market = market
        self.pre_update_price = pre_update_price
        self.latest_price = latest_price

    def get_market_prices(self) -> dict:
        return {
            "Market": self.market,
            "Pre-update Market Price": self.pre_update_price,
            "Latest Market Price": self.latest_price
        }

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

    def get_all_rates(self) -> dict:
       return {
            "market": self.market,
            "funding_fee_long_hourly": self.funding_fee_long_hourly,
            "interest_fee_long_hourly": self.interest_fee_long_hourly,
            "funding_rate_long_hourly": self.funding_rate_long_hourly,
            "funding_fee_short_hourly": self.funding_fee_short_hourly,
            "interest_fee_short_hourly": self.interest_fee_short_hourly,
            "funding_rate_short_hourly": self.funding_rate_short_hourly,
}


    def get_net_rates(self) -> dict:
        hourly_net_rate_long = self.funding_rate_long_annual - (self.funding_fee_long_hourly + self.interest_fee_long_hourly)
        hourly_net_rate_short = self.funding_rate_short_annual - (self.funding_fee_short_hourly + self.interest_fee_short_hourly)
        return {
            "Market": self.market,
            "net_rate_long_1hr": hourly_net_rate_long,
            "net_rate_short_1hr": hourly_net_rate_short
        }

class MarginMaintenanceInfo:
    def __init__(self, market, margin_fee, min_margin, maintenance_fee, min_maintenance):
        self.market = market
        self.margin_fee = margin_fee
        self.min_margin = min_margin
        self.maintenance_fee = maintenance_fee
        self.min_maintenance = min_maintenance

    def get_maintenence_margin(self) -> dict:
        return {
            "market": self.market,
            "margin_fee": self.margin_fee,
            "min_margin": self.min_margin,
            "maintenance_fee": self.maintenance_fee,
            "min_maintenance": self.min_maintenance
        }

class MarketInfo:
    def __init__(self, market_address):
        self.market_address = market_address

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
        ).get_net_rates()

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
        ).get_maintenence_margin()
