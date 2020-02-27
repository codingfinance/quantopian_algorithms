"""
RAY DALIO's All Weather Portfolio
In this Algo we will implement Ray Dalio's All Weather Portfolio Strategy
Suggested Weights

Stocks:30%
Long Term Bonds:40%
Intermediate Bonds:15%
Gold:7.5%
Commodities:7.5%

We will use the following ETFs
Stocks:SPY
Long Bonds:TLT
Intermediate Bonds:AGG
Gold:GLD
Commodities:DBC

"""
import quantopian.algorithm as algo
from quantopian.pipeline import Pipeline
from quantopian.pipeline.data.builtin import USEquityPricing
from quantopian.pipeline.filters import QTradableStocksUS

set_slippage(slippage.FixedSlippage(spread=0.00))


def initialize(context):
    """
    Called once at the start of the algorithm.
    """
    
    context.spy = sid(8554)
    context.tlt = sid(23921)
    context.agg = sid(25485)
    context.gld = sid(26807)
    context.dbc = sid(28054)
    
    # Rebalance every month end, 30 minutes before market close.
    schedule_function(
        rebalance,
        date_rules.month_end(),
        time_rules.market_close(minutes = 30),
    )

    # Record tracking variables at the end of each day.
    schedule_function(
        record_vars,
        date_rules.every_day(),
        time_rules.market_close(),
    )
    
      
def rebalance(context, data):
    """
    Execute orders according to our schedule_function() timing.
    """
    order_target_percent(context.spy,0.3)
    order_target_percent(context.tlt,0.4)
    order_target_percent(context.agg,0.15)
    order_target_percent(context.gld,0.075)
    order_target_percent(context.dbc,0.075)
    


def record_vars(context, data):
    """
    Plot variables at the end of each day.
    """
    record(lev = context.account.leverage)
    record(pos = len(context.portfolio.positions))
    
    
'''
Backtest Results
From 2006/2/4 To 2020/1/29


Returns
139.44%
Alpha
0.05
Beta
0.19
Sharpe
0.93
Drawdown
-18.39%


'''
