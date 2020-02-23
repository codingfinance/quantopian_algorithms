import talib
 
def initialize(context):    
    
    schedule_function(setAlerts, date_rules.every_day(), time_rules.market_close())
    schedule_function(rebalance, date_rules.every_day(), time_rules.market_open())
    set_commission(commission.PerTrade(cost=5.00))
    set_slippage(slippage.VolumeShareSlippage(volume_limit=0.025, price_impact=0.1))
    set_benchmark(symbol('SPY'))
    
    context.asset = symbol('SPY')
    
    context.rsi_period = 2
    context.OB = 70
    context.OS = 30
    context.pct_alloc = 1.00
    context.leverage = 1.00
    
    #Alert to buy or sell next day.
    context.buyAssetAlert = False
    context.sellAssetAlert = False
    
def setAlerts(context, data):    
    
    asset_price = data.history(context.asset, 'price', 3, '1d')
    
    rsi = talib.RSI(asset_price, context.rsi_period)
 
    if rsi[-1] < context.OS and data.can_trade(context.asset):        
        #order_target_percent(asset, context.pct_alloc * leverage)
        context.buyAssetAlert = True
    elif rsi[-1] > context.OB and data.can_trade(context.asset):
        #order_target_percent(asset, 0.00 * leverage)
        context.sellAssetAlert = True
 
    
    
def rebalance(context, data):
    
    if context.buyAssetAlert and data.can_trade(context.asset) and context.portfolio.positions[context.asset].amount == 0:  
        order_target_percent(context.asset, context.pct_alloc * context.leverage)
        context.buyAssetAlert = False
    if context.sellAssetAlert and data.can_trade(context.asset):
        order_target_percent(context.asset, 0.00 * context.leverage)
        context.sellAssetAlert = False
        
    all_positions = context.portfolio.positions
        
    log.info(all_positions)

    """

Returns
302.99%
Alpha
0.03
Beta
0.68
Sharpe
0.67
Drawdown
-31.09%

289% - Algo
310% - SPY
"""