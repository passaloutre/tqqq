# tqqq
trading strategy for minimizing downside with TQQQ

Most of this was cobbled together from various stackoverflow examples

tqqq_volatility.py is the main idea

tqqq_optimizer.py is dumb and needs work (or it has served its purpose and we can just ignore it)

TODO
1. I'd like to find a way to eliminate the single-day holds

   * they rarely seem to make any money

   * they're a lot to keep up with if manually trading
     - brokers that offer APIs for trading (etrade, robinhood) require 2FA, so automated trading isn't 100% automated
     - automating 1000s of dollars in a risky investment just makes me nervous anyways

   * you can get in trouble for trading too many times in a single week

   * we could maybe weed them out by analyzing the historical data
     - e.g. maybe single-day holds are more likely to occur after many recent holds
     - maybe they're more likely to pop up after long downturns?
     - if we find a pattern, we could filter them out

   * smaller par1 and par3 lead to shorter average hold times
     - it might be worth looking into whether TQQQ and VXN need different MACD parameters
     - larger par1 and par3 minimize gainz :(

2. Maybe it's better to find someone else who has already come up with a backtesting model

   * I see several out there, but I'm not sure how to incorporate my indicators
     - they mostly seem to be aimed at buying/holding long-term, not active trading

   * it shouldn't be hard to make a simple model, it only needs
     - each day look at indicators from previous day close, determine if buy/sell
     - buy/sell at today's open price
     - keep up with how much $$$ in account, how many shares, and share value

3. Might be good to modularize the algorithm and the backtesting model rather than one script?

4. Would love to deploy to a web server to send me daily emails with graphs and shit

5. STRETCH GOAL: STOCK TRADING DART BOARD
