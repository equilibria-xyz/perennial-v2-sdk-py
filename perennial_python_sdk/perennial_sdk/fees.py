"""
1. calcTradeFee Function
Purpose: This function calculates the trading fees associated with a position, differentiating between maker and taker fees, depending on the trade type (maker or taker) and market conditions.

Parameters:

positionDelta: The change in the size of the position.
marketSnapshot: Provides market conditions, including parameters like takerFee, makerFee, latestPrice, etc.
isMaker: Boolean indicating if the position is a maker (providing liquidity) or a taker (consuming liquidity).
direction: The direction of the trade (e.g., long or short).
referralFee: Optional parameter for applying a fee discount in the case of a referral.
usePreGlobalPosition: A flag to decide whether to use the pre-trade global position values.

Key Steps in Calculation:

Notional Calculation: The notional value of the position is calculated using calcNotional(positionDelta, latestPrice).

Maker Fees:
    Proportional fee and linear fee are computed based on the maker's total adjusted position and notional value.
    The total trade fee is the sum of these fees.

Taker Fees:
    1. Adiabatic, proportional, and linear fees are calculated, considering the skew in market positions (difference between long and short).
        -Adiabatic fee
        -Proportional fee
        -Linear fee
    2. A subtractive fee applies if a referral is used. (no refferal for now)
    3. Market fee is adjusted using the positionFee.

    The total trade fee includes adjustments for adiabatic and proportional factors.

Output: Returns a structured object (TradeFeeInfo) containing details on trade fees, trade impact, fee basis points, and other fee components.
"""

"""
2. calcPriceImpactFromTradeFee Function

Purpose: This function calculates the price impact based on trade fees and position changes.

Parameters:

tradeImpact: Represents the impact of the trade on the market price.
positionDelta: The change in position size.

Key Steps in Calculation:

The price impact is calculated as the ratio of tradeImpact to the absolute value of positionDelta.
If positionDelta is zero, the price impact is zero to avoid division by zero.

"""