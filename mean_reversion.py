'''
Sample Mean-reversion algorithm. 
The algorithm's thesis is that top performing stocks from last week will do poorly this week and weak stock's from last week will do better this week.

Rules.
1. Every Monday rank all the stocks in our Universe, based on previous 5 day returns
2. Enter long position on the worst performers those in the bottom 10%
3. Enter short positions on the best performers those in the top 10%
4. No leverage
5. Max position per stock 0.1%
6. Portfolio positions will be optimized using the Quantopian optimizer

'''

# importing the libraries
import quantopian.algorithm as algo
import quantopian.optimize as opt
from quantopian.pipeline import Pipeline
from quantopian.pipeline.data import USEquityPricing
from quantopian.pipeline.factors import Returns
from quantopian.pipeline.filters import QTradableStocksUS

# define the max leverage
max_leverage = 1

# define the max position size 0.1%
max_exposure = 0.001

# define lookback period
lookback_days = 5

def initialize(context):
    
    algo.schedule_function(
        rebalance,
        algo.date_rules.week_start(days_offset = 0),
        algo.time_rules.market_open(hours = 1, minutes = 30)
    )
    
    algo.attach_pipeline(make_pipeline(context), 'mean_reversion')
    
    
def make_pipeline(context):
    
    # Universe of top 2000 liquid stocks
    universe = QTradableStocksUS()
    
    recent_returns = Returns(
        window_length = lookback_days,
        mask = universe
    )
    
    # Convert returns into a factor
    
    recent_returns_z_score = recent_returns.zscore()
    
    low_returns = recent_returns_z_score.percentile_between(0,10)
    high_returns = recent_returns_z_score.percentile_between(90,100)
    
    securities_to_trade = (low_returns | high_returns)
    
    pipe = Pipeline(
        columns = {
            'recent_returns_zscore':recent_returns_z_score
        },
        screen = securities_to_trade
    )
    
    return pipe


def before_trading_start(context,data):
    
    context.output = algo.pipeline_output('mean_reversion')
    
    context.recent_returns_z_score = context.output['recent_returns_zscore']
    
    
def rebalance(context,data):
    
    # Define the objective
    
    objective = opt.MaximizeAlpha(-context.recent_returns_z_score)
    
    max_gross_exposure = opt.MaxGrossExposure(max_leverage)
    
    max_position_concentration = opt.PositionConcentration.with_equal_bounds(-max_exposure, max_exposure)
    
    dollar_neutral = opt.DollarNeutral()
    
    constraints = [
            max_gross_exposure,
            max_position_concentration,
            dollar_neutral
            ]
    
    algo.order_optimal_portfolio(objective, constraints)




    
    
    
    
    