from datetime import datetime
from decimal import Decimal, getcontext


getcontext().prec = 100  # Setting a high precision for Decimal calculations

class Big6Math:
    BASE = Decimal('1000000')
    ZERO = Decimal('0')
    ONE = Decimal('1000000')
    TWO = Decimal('2000000')

    @staticmethod
    def mul(a: Decimal, b: Decimal) -> Decimal:
        return (a * b) / Big6Math.BASE

    @staticmethod
    def div(a: Decimal, b: Decimal) -> Decimal:
        return (a * Big6Math.BASE) / b

    @staticmethod
    def add(a: Decimal, b: Decimal) -> Decimal:
        return a + b

    @staticmethod
    def sub(a: Decimal, b: Decimal) -> Decimal:
        return a - b

    @staticmethod
    def abs(a: Decimal) -> Decimal:
        return abs(a)

    @staticmethod
    def max(a: Decimal, b: Decimal) -> Decimal:
        return max(a, b)

    @staticmethod
    def min(a: Decimal, b: Decimal) -> Decimal:
        return min(a, b)

    @staticmethod
    def sqrt(a: Decimal) -> Decimal:
        return a.sqrt()

    @staticmethod
    def to_unsafe_float(a: Decimal) -> float:
        return float(a)

    @staticmethod
    def from_float_string(a: str) -> Decimal:
        return Decimal(a) * Big6Math.BASE

    @staticmethod
    def to_float_string(a: Decimal) -> str:
        return str(a / Big6Math.BASE)

def linear_interpolation(start_x, start_y, end_x, end_y, target_x):
    if target_x < start_x or target_x > end_x:
        raise ValueError('CurveMath18OutOfBoundsError')

    x_range = end_x - start_x
    y_range = end_y - start_y
    x_ratio = Big6Math.div(target_x - start_x, x_range)
    return Big6Math.mul(y_range, x_ratio) + start_y

def compute_interest_rate(curve, utilization):
    if utilization < Big6Math.ZERO:
        return curve['minRate']

    if utilization < curve['targetUtilization']:
        return linear_interpolation(Big6Math.ZERO, curve['minRate'], curve['targetUtilization'], curve['targetRate'], utilization)

    if utilization < Big6Math.ONE:
        return linear_interpolation(curve['targetUtilization'], curve['targetRate'], Big6Math.ONE, curve['maxRate'], utilization)

    return curve['maxRate']

def calculate_funding_and_interest_for_sides(snapshot):
    p_accumulator = snapshot["result"]["postUpdate"]["marketSnapshots"][0]['global']['pAccumulator']
    funding_fee = snapshot["result"]["postUpdate"]["marketSnapshots"][0]['parameter']['fundingFee']
    interest_fee = snapshot["result"]["postUpdate"]["marketSnapshots"][0]['parameter']['interestFee']
    p_controller = snapshot["result"]["postUpdate"]["marketSnapshots"][0]['riskParameter']['pController']
    utilization_curve = snapshot["result"]["postUpdate"]["marketSnapshots"][0]['riskParameter']['utilizationCurve']
    efficiency_limit = snapshot["result"]["postUpdate"]["marketSnapshots"][0]['riskParameter']['efficiencyLimit']
    maker = snapshot["result"]["postUpdate"]["marketSnapshots"][0]['nextPosition']['maker']
    long = snapshot["result"]["postUpdate"]["marketSnapshots"][0]['nextPosition']['long']
    short = snapshot["result"]["postUpdate"]["marketSnapshots"][0]['nextPosition']['short']
    timestamp = snapshot["result"]["postUpdate"]["marketSnapshots"][0]['nextPosition']['timestamp']

    time_delta = Decimal(datetime.now().timestamp()) - timestamp
    market_funding = p_accumulator['_value'] + Big6Math.mul(time_delta, Big6Math.div(p_accumulator['_skew'], p_controller['k']))
    funding = Big6Math.max(Big6Math.min(market_funding, p_controller['max']), p_controller['min'])

    major = Big6Math.max(long, short)
    minor = Big6Math.min(long, short)

    net_utilization = Big6Math.div(major, maker + minor) if (maker + minor) > 0 else Big6Math.ZERO
    efficiency_utilization = Big6Math.mul(major, Big6Math.div(efficiency_limit, maker)) if maker > 0 else 100 * Big6Math.ONE
    utilization = Big6Math.min(100 * Big6Math.ONE, Big6Math.max(net_utilization, efficiency_utilization))

    interest_rate = compute_interest_rate(utilization_curve, utilization)
    applicable_notional = Big6Math.min(maker, long + short)
    interest = Big6Math.div(Big6Math.mul(interest_rate, applicable_notional), long + short) if (long + short) > 0 else Big6Math.ZERO
    total_interest_fee = Big6Math.mul(interest, interest_fee)

    total_funding_fee = Big6Math.mul(Big6Math.abs(funding), funding_fee) / 2
    long_funding = funding + total_funding_fee
    short_funding = -funding + total_funding_fee

    maker_util = Big6Math.max(Big6Math.min(Big6Math.div(long - short, maker), Big6Math.ONE), -Big6Math.ONE) if maker > 0 else Big6Math.ZERO
    maker_funding = Big6Math.mul(maker_util, funding)
    maker_funding_fee = Big6Math.mul(Big6Math.abs(maker_util), total_funding_fee)
    maker_rate = (maker_funding - maker_funding_fee + (interest - total_interest_fee)) * -1

    # Create usable variables:
    funding_fee_long_annual = round((funding + total_funding_fee)/10000,4)
    funding_fee_long_hourly = round(funding_fee_long_annual/(365*24),4)
    interest_fee_long_annual = round(interest/10000,4)
    interest_fee_long_hourly = round(interest_fee_long_annual/(365*24),4)
    funding_rate_long_annual = round((long_funding + interest)/10000,4)
    funding_rate_long_hourly = round(funding_rate_long_annual/(365*24),4)

    # prints were here

    funding_fee_short_annual = round((-funding + total_funding_fee)/10000,4)
    funding_fee_short_hourly = round(funding_fee_short_annual/(365*24),4)
    interest_fee_short_annual = round(interest/10000,4)
    interest_fee_short_hourly = round(interest_fee_short_annual/(365*24),4)
    funding_rate_short_annual = round((short_funding + interest)/10000,4)
    funding_rate_short_hourly = round(funding_rate_short_annual/(365*24),4)

    return (funding_fee_long_annual, funding_fee_long_hourly, interest_fee_long_annual, interest_fee_long_hourly,
            funding_rate_long_annual,funding_rate_long_hourly, funding_fee_short_annual, funding_fee_short_hourly,
            interest_fee_short_annual, interest_fee_short_hourly, funding_rate_short_annual, funding_rate_short_hourly)