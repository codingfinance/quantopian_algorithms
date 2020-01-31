'''
This backtest runs a simple Stocks Bonds strategy
Rules are 

- If the last 6 momths SPY returns are positive, then invest 100% in SPY
- If the last 6 momths SPY returns are negative, then invest 100% in TLT

'''

stock = symbol('SPY')
days = 21
periods = 6

set_slippage(slippage.FixedSlippage(spread=0.00)) 

def initialize(context):
    
    schedule_function(rebalance,
                      date_rules.month_end(),
                      time_rules.market_close(minutes = 30))
    

def rebalance(context,data):
        
    bars = (days+1 * periods)
    monthly_price = data.history(stock,'close', bars, '1d')
    spy_filter = monthly_price.iloc[-1]/monthly_price.iloc[0] - 1
    
    if spy_filter > 0:
        context.signal = 'stocks'
    else:
        context.signal = 'bonds'
        
   
    if context.signal == 'stocks':
        order_target_percent(sid(8554),1.0)
        order_target_percent(sid(23921),0)
    else:
        order_target_percent(sid(8554),0)
        order_target_percent(sid(23921),1.0)
        
        
    record(leverage = context.account.leverage,
           positions = len(context.portfolio.positions))
           
'''
Backtest Results
From 2003/9/2 To 2020/1/29

Returns
225.87%
Alpha
0.05
Beta
0.34
Sharpe
0.57
Drawdown
-28.68%

'''
