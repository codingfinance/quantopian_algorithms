'''
This is a simple 60/40 strategy
Weight:

SPY:60%
TLT:40%

Monthly Rebalance
'''

def initialize(context):
    """
    Called once at the start of the algorithm.
    """
    
    context.spy = sid(8554)
    context.tlt = sid(23921)
    
    # Rebalance month end, 30 minutes before market close.
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
    
    set_slippage(slippage.FixedSlippage(spread=0.00))  

def rebalance(context, data):
    """
    Execute orders according to our schedule_function() timing.
    """
    order_target_percent(context.spy,0.6)
    order_target_percent(context.tlt,0.4)
    


def record_vars(context, data):
    """
    Plot variables at the end of each day.
    """
    record(lev = context.account.leverage)
    record(pos = len(context.portfolio.positions))
    
    
'''
Backtest Results
From 2002/7/25 To 2020/1/29


Returns
332.83%
Alpha
0.04
Beta
0.46
Sharpe
0.91
Drawdown
-32.65%

'''
