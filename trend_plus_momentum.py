"""
This Algo selects from the following ETF
['AGG', 'DBC', 'EEM', 'EFA', 'GLD', 'HYG', 'IWM', 'LQD', 'QQQ', 'SPY', 'TLT', 'VNQ']

Rules
- Calculate the 10 month momentum (MOM)
- Calculate the 10 month Simple Moving average(SMA)
- Rank stocks with best momentum score
- If Closing Price is above SMA & MOM is above 0
  - Invest equally in top 5 ETF

- Rebalance Start of Every Month, 30 minutes after open

"""
from quantopian.algorithm import attach_pipeline, pipeline_output
from quantopian.pipeline import Pipeline
from quantopian.pipeline.data import USEquityPricing
from quantopian.pipeline.factors import CustomFactor, SimpleMovingAverage
from quantopian.pipeline.filters import StaticAssets

set_slippage(slippage.FixedSlippage(spread = 0))

def initialize(context):

    schedule_function(rebalance,
                      date_rules.month_start(),
                      time_rules.market_open(minutes = 30))

    attach_pipeline(make_pipeline(),
                    'my_pipeline')

class Mom_10_month(CustomFactor):

    inputs = [USEquityPricing.close]
    window_length = 220

    def compute(self, today, asset, out, close):
        out[:] = close[-1] / close[0] - 1


def make_pipeline():

    etf = symbols('AGG', 'DBC', 'EEM', 'EFA', 'GLD', 'HYG', 'IWM', 'LQD', 'QQQ', 'SPY', 'TLT', 'VNQ')

    universe = StaticAssets(etf)

    mom_10 = Mom_10_month(mask = universe)

    sma_10 = SimpleMovingAverage(

        inputs = [USEquityPricing.close],
        window_length = 220, mask = universe
    )

    close = USEquityPricing.close.latest

    signal = (mom_10 > 0) & (close > sma_10)

    mom_rank = mom_10.rank()
    mom_top = mom_rank.top(5)

    return Pipeline(

        columns = {

            'close':close,
            'sma_10':sma_10,
            'mom_10':mom_10,
            'signal':signal,
            'rank':mom_rank
        }, screen = universe & mom_top & signal
    )

def before_trading_start(context,data):

    context.output = pipeline_output('my_pipeline')

    context.longs = context.output.index.tolist()

def rebalance(context,data):

    my_positions = context.portfolio.positions

    if len(context.longs) > 0:
        long_weight = 0.95/len(context.longs)
    else:
        for sec in my_positions:
            if sec not in context.longs and data.can_trade(sec):
                order_target_percent(sec,0)


    # Open Long Positions

    for sec in context.longs:
        if sec in context.longs and data.can_trade(sec):
            if sec not in my_positions:
                order_target_percent(sec, long_weight)

    # Close Position not meeting criteria

    for sec in my_positions:
        if sec not in context.longs and data.can_trade(sec):
            order_target_percent(sec,0)



    record(leverage = context.account.leverage,
           positions = len(my_positions))
