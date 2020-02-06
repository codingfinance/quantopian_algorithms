"""
Testing High and Low PE Stocks
"""
import quantopian.algorithm as algo
import quantopian.optimize as opt
from quantopian.pipeline import Pipeline
from quantopian.pipeline.data import USEquityPricing
from quantopian.pipeline.filters import QTradableStocksUS
from quantopian.pipeline.data.morningstar import Fundamentals
from quantopian.pipeline.classifiers.morningstar import Sector

def initialize(context):
    """
    Called once at the start of the algorithm.
    """
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
    
    
    universe = QTradableStocksUS()
    
    pe_ratio = Fundamentals.pe_ratio.latest
    
    top = pe_ratio.percentile_between(90,100)
    
    bottom = pe_ratio.percentile_between(0,10)
    
    return Pipeline(
    
        columns = {
            
            'pe':pe_ratio,
            'top':top,
            'bottom':bottom
        }, screen  = universe & (top | bottom)
    )

def before_trading_start(context, data):
    """
    Called every day before market open.
    """
    context.output = algo.pipeline_output('pipeline')

    # These are the securities that we are interested in trading each day.
    context.longs = context.output.bottom.index.tolist()
    context.shorts = context.output.top.index.tolist()
    
def compute_target_weights(context,data):
    
    # Mapping stocks and weights
    
    weights = {}
    
    if context.longs and context.shorts:
        long_weight = 0.5 / len(context.longs)
        short_weight = -0.5 / len(context.shorts)  
    else:
        return weights
    
    for security in context.portfolio.positions:
        if security not in context.longs and security not in context.shorts and data.can_trade(security):
            weights[security] = 0

    for security in context.longs:
        weights[security] = long_weight

    for security in context.shorts:
        weights[security] = short_weight

    return weights    

def rebalance(context, data):
    """
    Execute orders according to our schedule_function() timing.
    """
    target_weights = compute_target_weights(context,data)
    
    if target_weights:
        order_optimal_portfolio(
            objective = opt.TargetWeights(target_weights),
            constraints = [])


def record_vars(context, data):
    """
    Record variables at the end of each day.
    """
    pass


def handle_data(context, data):
    """
    Called every minute.
    """
    pass