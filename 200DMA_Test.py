# Research libraries

from quantopian.algorithm import attach_pipeline, pipeline_output
from quantopian.algorithm import order_optimal_portfolio
import quantopian.optimize as opt

from quantopian.pipeline import Pipeline
from quantopian.pipeline.data.builtin import USEquityPricing
from quantopian.pipeline.filters import QTradableStocksUS, StaticAssets
from quantopian.pipeline.factors import SimpleMovingAverage


def initialize(context):
    
    
    set_benchmark(sid(8554))
    
    schedule_function(
    
        rebalance,
        date_rules.month_start(),
        time_rules.market_open()
    )
    
    attach_pipeline(make_pipeline(), 'my_pipeline')
    
def make_pipeline():
    
    universe = StaticAssets(symbols('SPY'))
    
    dma_200 = SimpleMovingAverage(
    
        inputs = [USEquityPricing.close],
        window_length = 200,
        mask = universe
    )
    
    close = USEquityPricing.close.latest
    
    longs = close > dma_200
      
    securities_to_trade = (longs)
    
    return Pipeline(
        columns={
            'longs': longs
        },
        screen=(securities_to_trade),
    )

def before_trading_start(context,data):
    
    pipe_results = pipeline_output('my_pipeline')
    
    context.longs = []
    
    for sec in pipe_results[pipe_results['longs']].index.tolist():
        
        if data.can_trade(sec):
            context.longs.append(sec)

def compute_target_weight(context,data):
    
    weights = {}
    
    # If there are securities in the long/short list
    # compute the target weight
    if context.longs:
        
        long_weight = 0.99 / len(context.longs)
    else:
        return weights
    
    for security in context.portfolio.positions:
        
        if security not in context.longs and data.can_trade(security):
            weights[security] = 0
            
    for security in context.longs:
        
        weights[security] = long_weight
        
    return weights

def rebalance(context,data):
    
    target_weights = compute_target_weight(context,data)
    
    if target_weights:
        order_optimal_portfolio(
        
            objective = opt.TargetWeights(target_weights),
            constraints = []
        )