'''
This Strategy mimics the Dogs of Dow Strategy with a few key differences.
- It uses Total Yield versus just Dividend Yield
- It uses S&P 500 Index vs Dow Jones Index
- It also screens for positive 6 momentum
- The total yield is the yield that shareholders can expect, by summing Dividend Yield and Buyback Yield

Rules are Every Month end

- Get the 6 month Momentum of all Stocks in S&P 500 Index
- Get the Latest Total Yield of all Stocks in S&P 500 Index
- Combine these factors to Rank the stocks
- Select the top 30 stocks and buy them in Equal Weights.
- Rebalance every Month

'''

'''
Back Test Results
From 2003/9/2 To 2020/1/29

Returns
577.3%
Alpha 
0.03
Beta
1.02
Sharpe
0.7
Drawdown
-55.41

'''

from quantopian.algorithm import attach_pipeline, pipeline_output
from quantopian.pipeline import Pipeline
from quantopian.pipeline.data import morningstar
from quantopian.pipeline.data.morningstar import Fundamentals
from quantopian.pipeline.filters import Q500US
from quantopian.pipeline.data import USEquityPricing
from quantopian.pipeline.factors import Returns
from quantopian.pipeline.factors import CustomFactor

stock = symbol('SPY')
days = 21
periods = 6
set_slippage(slippage.FixedSlippage(spread = 0))


def initialize(context):
    
    pipe = make_pipeline()
    attach_pipeline(pipe, "my_pipeline")
    
    context.bonds = sid(25485)
    
    schedule_function(rebalance,
                      date_rules.month_end(),
                      time_rules.market_close())
    
class mom_score(CustomFactor):
    
    inputs = [USEquityPricing.close]
    window_length = 126
    
    def compute(self,today, asset, out, close):
        
        out[:] = close[-1] / close[0] - 1
        
    
    

def make_pipeline():
    
    universe = Q500US()
    
    close = USEquityPricing.close.latest
    
    total_yield = Fundamentals.total_yield.latest
    
    top_yield = total_yield.top(100, mask = universe)
    
    mom_score_6 = mom_score()
    mom_score_6 = mom_score_6.top(30, mask = top_yield)
    
    pipe = Pipeline(
    
        columns = {
            
            'close':close,
            'total_yield':total_yield,
            'mask':top_yield,
            'mom_score':mom_score_6
        }, screen = universe & top_yield & mom_score_6
    
    )
    
    return pipe

def before_trading_start(context, data):
    """
    Called every day before market open.
    """
    context.output = pipeline_output('my_pipeline')

    # These are the securities that we are interested in trading each day.
    
    context.longs = context.output.index.tolist()



def rebalance(context,data):
    
    my_positions = context.portfolio.positions
    
    if (len(context.longs) > 0):
        long_weight = 1.0/len(context.longs)
        
    for sec in context.longs:
        if sec in context.longs and data.can_trade(sec):
            if sec not in my_positions:
                order_target_percent(sec,long_weight)
    
            
    for sec in my_positions:
        if sec not in context.longs and data.can_trade(sec):
            order_target_percent(sec,0)
            
    record(leverage = context.account.leverage,
          positions = len(my_positions))
          

    
