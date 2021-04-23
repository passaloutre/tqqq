# tqqq
trading strategy for minimizing downside with TQQQ

Most of this was cobbled together from various stackoverflow examples

tqqq_volatility.py is the main idea

Update 2021-04-22:

  Fixed backtesting model and bad news
  The model was using today's indicator to know whether to buy or sell today, but you can't know today's indicator until after today!
  Obviously if you know today's closing price before buying at todays opening price, you can turn $1k into $1M pretty easily
  I fixed it to use yesterday's indicator to buy/sell today, and, predictably, it does worse. Worse than just HODLing TQQQ, but better than HODLing regular QQQ.
  It does avoid pants-shitting drops like late 2018 or early 2020, where you lose half your money in a month but it is overconservative during some long rises, missing out on gains that overcome the drops. HODLing TQQQ always wins unless you cherry pick the start date right before a big drop, and even then it still beats the algorithm within a couple years.

  We need to find a way to be a little riskier on the rise and a little tighter on the drops.

  Possibilities: 
  - averaging into positions rather than simple on/off
  - test it with just a trailing 10-20% stop loss, still need to find the right buy trigger
  - limit orders instead of market orders
  - use opening price (or even premarket) for indicators, it's more up to date than yesterday's close
  - along the same lines, trading in the middle of the day rather than the beginning
  - hedging with TMF or SQQQ (see below)
  - simpler moving-average calculations

  The good news (for making money at least) is that HODLing $1k in TQQQ from 2011 through today (even with the covid drop) earns over $57k. Still, the last 10 years have been anomalously good for the NASDAQ, so maybe it's not surprising.

Update 2021-04-23

This could be of some use: https://www.reddit.com/r/stocks/comments/mx27u0/move_over_bloomberg_terminal_here_comes_gamestonk/

Also I got my second vaccination today


TODO
1. Include dividends/expense ratio in backtest
1. Might be good to modularize the algorithm and the backtesting model rather than one script?
2. Would love to deploy to a web server to send me daily emails with graphs and shit
3. The strategy could be enhanced (and definitely up the danger factor) buying SQQQ when selling TQQQ
   * SQQQ attempts to INVERSE TRIPLE QQQ (i.e. QQQ down 1%, SQQQ up 3%)
4. Monte Carlo Sims - obviously not all possible market conditions are reflected in the <10 years of data available for TQQQ
4. STRETCH GOAL: STOCK TRADING DART BOARD

Further Inspiration

This is an approach to long-term holding UPRO (like TQQQ but for the whole SP500), which doesn't aim to sell at downturns but minimizes loss through holding an uncorrelated triple-leveraged bond ETF

* https://www.bogleheads.org/forum/viewtopic.php?f=10&t=272007
* https://www.bogleheads.org/forum/viewtopic.php?f=10&t=288192


Here's a bunch of other triple-leveraged funds that we should gamble on

* https://etfdb.com/themes/leveraged-3x-etfs/

This Canadian dude has something similar going on. He doesn't give up his algorithm, but he does suggest several places he's getting his indicators (scroll down):

https://www.bredincapital.com/weeklycommentary/2-13-2021-t5cr8-agakj-j5l2n-2fxjd-te9xr-8g4tx-hcknr-h5apr-fjnpk

Just to be clear, the github procedure is (?):

* git pull https://github.com/passaloutre/tqqq
* make whatever changes
* git commit 'file.py' -m 'whatever message'
* git push

Is that correct? I tried as much today and it seems to have worked
