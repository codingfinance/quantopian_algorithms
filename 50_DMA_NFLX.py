"""
This is a toy algorithm recipe. Not to be actually used in trading.

For this recipe, we consider a basic strategy based on the SMA. 
The key points of the strategy are as follows: 
When the close price becomes higher than the 50-day SMA, buy one share.
When the close price becomes lower than the 50-day SMA and we have a share, sell it.
We can only have a maximum of one share at any given time.
No short selling is allowed.

We will only Trade one stock Netflix (Netflix)
We will compare the results with Netflix stock as the Benchmark .


Results

Returns
10563.16%
Alpha
0.01
Beta
1.00
Sharpe
0.94
Drawdown
-82.01%

Strategy
10563.16%
Benchmark(NFLX)
10033.28%


"""

import quantopian.algorithm as algo
import quantopian.optimize as opt
from quantopian.pipeline import Pipeline
from quantopian.pipeline.data.builtin import USEquityPricing
from quantopian.pipeline.filters import QTradableStocksUS
from quantopian.pipeline.filters import StaticAssets
from quantopian.pipeline.factors import SimpleMovingAverage

def initialize(context):
    """
    Called once at the start of the algorithm.
    """
    
    # Set Benchmark same as the Stock (Netflix).
    
    set_benchmark(sid(23709))
    
    # Rebalance every day, 1 hour after market open.
    algo.schedule_function(
        rebalance,
        algo.date_rules.every_day(),
        algo.time_rules.market_open(hours=1),
    )

    # Record tracking variables at the end of each day.
    algo.schedule_function(
        record_vars,
        algo.date_rules.every_day(),
        algo.time_rules.market_close(),
    )

    # Create our dynamic stock selector.
    algo.attach_pipeline(make_pipeline(), 'pipeline')


def make_pipeline():
    
    universe = StaticAssets((symbols('NFLX')))
    
    sma = SimpleMovingAverage(inputs=[USEquityPricing.close],
                             window_length = 50)
    close = USEquityPricing.close.latest
    
    signal = sma > close
    
    return Pipeline(
    
        columns = {
            
            'sma':sma,
            'close':close,
            'signal':signal
        }, screen = universe
    )
    

def compute_target_weights(context, data):
    """
    Execute orders according to our schedule_function() timing.
    """
    weight = {}
    
    if context.signal:
        long_wt = 1.0/len(context.signal)
    else:
        return weight
    
    for security in context.portfolio.positions:
        if security not in context.signal and data.can_trade(security):
            weight[security] = 0
            
    for security in context.signal:
        weight[security] = long_wt
        
    return weight
        
    
def before_trading_start(context, data):
    
    pipe_results = algo.pipeline_output("pipeline")
    
    context.signal = []
    
    for sec in pipe_results[pipe_results['signal']].index.tolist():
        if data.can_trade(sec):
            context.signal.append(sec)
            
def rebalance(context, data):
    """
    Rebalance weekly.
    """

    # Calculate target weights to rebalance
    target_weights = compute_target_weights(context, data)

    # If we have target weights, rebalance our portfolio
    if target_weights:
        order_optimal_portfolio(
            objective=opt.TargetWeights(target_weights),
            constraints=[],
        )
    
    

def record_vars(context, data):
    """
    Plot variables at the end of each day.
    """
    record(Leverage = context.account.leverage)
    record(num_positions=len(context.portfolio.positions))


