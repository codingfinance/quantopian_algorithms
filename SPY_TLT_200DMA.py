"""
## SPY &  TLT Algo
In this algorithm we will
- Buy SPY when its closing price is above the 200 Day Moving Average
- Sell SPY and reinvest the money in TLT if the SPY 200 Day moving average is above the SPY closing price.
"""
import quantopian.algorithm as algo
from quantopian.algorithm import attach_pipeline, pipeline_output


from quantopian.pipeline import Pipeline
from quantopian.pipeline.data import USEquityPricing
from quantopian.pipeline.filters import StaticAssets
from quantopian.pipeline.factors import SimpleMovingAverage

set_slippage(slippage.FixedSlippage(spread=0.00))  

def initialize(context):
    
    context.spy = sid(8554)
    context.tlt = sid(23921)
    
    attach_pipeline(make_pipeline(),
                    "my_pipe")
    
    schedule_function(rebalance,
                      date_rules.month_end(),
                      time_rules.market_close(minutes = 30))
                      
    schedule_function(record_vars,
                      date_rules.every_day(),
                      time_rules.market_close())  
            

def make_pipeline():
    
    universe = StaticAssets(symbols('SPY'))
    
    close = USEquityPricing.close.latest
    
    sma_200 = SimpleMovingAverage(
    
        inputs = [USEquityPricing.close],
        window_length = 200,
        mask = universe
    )
    
    logic = close > sma_200
    
    return Pipeline(
    
        columns = {
            
            'close':close,
            'sma_200':sma_200,
            'logic':logic
        }, screen = universe
    )

def before_trading_start(context,data):

    context.output = pipeline_output("my_pipe")
                          
def rebalance(context,data):
    
    if context.output['close'].values >= context.output['sma_200'].values:
        order_target_percent(context.spy,1.0)
        order_target_percent(context.tlt,0)
    else:
        order_target_percent(context.spy,0)
        order_target_percent(context.tlt,1.0)
    
    
                      
def record_vars(context, data):
    """
    Plot variables at the end of each day.
    """
    record(lev = context.account.leverage)
    record(pos = len(context.portfolio.positions))
    
    
'''
Backtest results
From 2003/1/1 To 2020/1/29

Returns
643.44%
Alpha
0.09
Beta
0.32
Sharpe
0.91
Drawdown
-26.47%


'''
                      
                  
