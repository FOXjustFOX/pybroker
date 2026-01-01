# Going Live: Transitioning to Real Money Trading

This guide explains how to transition from paper trading to live trading with real money using PyBroker.

## ⚠️ CRITICAL WARNING

**Live trading involves real money and significant risk of loss.**

Before proceeding:
- You must be 100% comfortable with potential losses
- Only use money you can afford to lose completely
- Understand that past performance does not guarantee future results
- This is NOT financial advice - consult with a licensed financial advisor

## Prerequisites for Live Trading

Before switching to live trading, ensure you have:

- [ ] **Tested in paper trading for at least 30 days**
- [ ] **Achieved consistent profitability in paper trading**
- [ ] **Backtested strategy over multiple years of data**
- [ ] **Tested during different market conditions** (bull, bear, sideways)
- [ ] **Reviewed all risk parameters** and understand them completely
- [ ] **Set up monitoring and alerts**
- [ ] **Have a written trading plan** including entry/exit rules
- [ ] **Defined your maximum loss tolerance** (daily, monthly, total)
- [ ] **Funded your Alpaca live trading account**
- [ ] **Completed identity verification** with Alpaca

## Step-by-Step Guide to Go Live

### Step 1: Review Your Paper Trading Performance

Analyze your paper trading results:

```bash
cd examples/autonomous_trading
python strategy.py
```

Key metrics to check:
- **Win Rate**: Should be > 50%
- **Profit Factor**: Should be > 1.5
- **Max Drawdown**: Should be acceptable to you (e.g., < 20%)
- **Sharpe Ratio**: Should be > 1.0
- **Total Return**: Should be positive over 30+ days

### Step 2: Start with Minimal Capital

**Recommendation**: Start with $500-$2,000 for live trading, even if you have more available.

Why start small:
- Psychological adjustment to real money
- Validate strategy works in live market
- Identify any execution issues
- Build confidence gradually

Edit your `.env` file:

```bash
# Reduce capital for initial live trading
INITIAL_CAPITAL=500          # Start very small
MAX_POSITION_SIZE=100        # Limit per position
MAX_POSITIONS=3              # Reduce number of positions
MAX_DAILY_LOSS=50            # Strict daily loss limit
```

### Step 3: Fund Your Alpaca Live Trading Account

1. **Log in to Alpaca**: https://alpaca.markets/
2. **Switch to "Live Trading"** section (not Paper Trading)
3. **Link your bank account**:
   - Follow Alpaca's instructions for ACH transfer
   - Wait for verification (1-2 business days)
4. **Transfer funds**:
   - Start with your minimum amount (e.g., $500)
   - Wait for funds to settle (typically 1-2 business days)
5. **Verify funds are available**:
   - Check your Live Trading account balance
   - Ensure buying power shows the correct amount

### Step 4: Get Your Live Trading API Keys

**IMPORTANT**: Live and paper trading use different API keys!

1. **Log in to Alpaca**
2. **Navigate to "Live Trading" section** (not Paper Trading)
3. **Go to API Keys settings**
4. **Generate new Live Trading API keys**:
   - Click "Generate New Key"
   - Save both the API Key and Secret Key immediately
   - You won't be able to see the Secret Key again!
5. **Store keys securely**

### Step 5: Update Your Configuration

Edit your `.env` file:

```bash
# LIVE TRADING CONFIGURATION
# WARNING: These are your LIVE trading keys - keep them secure!

# Replace with your LIVE trading API keys (NOT paper trading keys)
ALPACA_API_KEY=your_live_api_key_here
ALPACA_API_SECRET=your_live_api_secret_here

# CRITICAL: Set to false for live trading
ALPACA_PAPER=false

# Conservative settings for live trading
INITIAL_CAPITAL=500          # Match your actual account balance
MAX_POSITION_SIZE=100        # Smaller positions
MAX_POSITIONS=3              # Fewer concurrent positions
STOP_LOSS_PERCENT=2          # Keep tight stops
MAX_DAILY_LOSS=50            # Very strict daily limit
MAX_DAILY_TRADES=5           # Limit trade frequency
```

**Double-check**: Make sure `ALPACA_PAPER=false`

### Step 6: Verify Your Setup

Before running live, verify everything:

```bash
# Test configuration
python config.py
```

You should see:
```
Trading Mode: LIVE
```

If it says "PAPER", do NOT proceed!

### Step 7: Run a Final Backtest

```bash
python strategy.py
```

Verify:
- Strategy still profitable
- Risk parameters are acceptable
- No errors in execution

### Step 8: Start Live Trading

**The moment of truth**. Take a deep breath.

```bash
python run_autonomous.py
```

You'll see a warning:
```
WARNING: LIVE TRADING IS ENABLED!
Real money will be used for trades!
Type 'YES' to continue with live trading:
```

Type `YES` and press Enter to confirm.

### Step 9: Monitor Closely (First Week)

During your first week of live trading:

**Do:**
- ✅ Check logs every hour during market hours
- ✅ Verify trades are executing correctly
- ✅ Monitor for any errors or issues
- ✅ Compare execution prices to expected
- ✅ Track actual vs. expected performance
- ✅ Keep a trading journal

**Don't:**
- ❌ Panic over small losses
- ❌ Override the system manually
- ❌ Increase position sizes immediately
- ❌ Add more strategies without testing
- ❌ Ignore the daily loss limit

**Monitor these logs:**

```bash
# Real-time monitoring
tail -f trading.log

# Check for errors
grep ERROR trading.log

# View all trades
grep "BUY SIGNAL\|SELL" trading.log
```

### Step 10: Scale Gradually

After 1-2 weeks of successful live trading:

1. **Review performance**:
   - Compare to paper trading results
   - Check if strategy is working as expected
   - Verify no execution issues

2. **Scale up cautiously** (if profitable):
   ```bash
   # Increase gradually - example progression:
   # Week 1-2: $500
   # Week 3-4: $1,000
   # Month 2: $2,000
   # Month 3: $3,000
   # Only increase if consistently profitable
   ```

3. **Update `.env` accordingly**:
   ```bash
   INITIAL_CAPITAL=1000      # Gradual increase
   MAX_POSITION_SIZE=200     # Proportional increase
   ```

## Important Differences: Paper vs. Live Trading

### What Changes with Live Trading

1. **Execution Prices**:
   - Paper: Uses mid-market prices (often optimistic)
   - Live: Actual market prices with slippage
   - **Impact**: Lower actual returns than paper trading

2. **Order Fills**:
   - Paper: Orders fill instantly at expected prices
   - Live: Orders may not fill, or fill at worse prices
   - **Impact**: Some expected trades won't execute

3. **Psychological Factors**:
   - Paper: No emotional stress
   - Live: Real money creates stress and emotional decisions
   - **Impact**: May be tempted to override the system

4. **Market Impact**:
   - Paper: No impact on market
   - Live: Large orders can move prices (usually not an issue with small accounts)
   - **Impact**: Minimal for typical retail accounts

### Expect Lower Performance

**Reality Check**: Live trading performance is typically 10-30% worse than paper trading due to:
- Slippage (difference between expected and actual prices)
- Partial fills (orders not fully executed)
- Fees and costs (even if minimal)
- Psychological factors
- Market timing differences

If your paper trading shows 20% annual return, expect 14-18% live.

## Risk Management for Live Trading

### Enhanced Safety Measures

When going live, consider adding:

1. **Circuit Breakers**:
   ```python
   # Add to config.py or strategy.py
   EMERGENCY_STOP_LOSS = 0.10  # Stop all trading at 10% account loss
   ```

2. **Position Size Limits**:
   ```bash
   # More conservative than paper trading
   MAX_POSITION_SIZE=100  # Even if you could do $200
   ```

3. **Diversification**:
   - Trade 5-10 different symbols
   - Use different timeframes
   - Consider multiple uncorrelated strategies

4. **Regular Reviews**:
   - Weekly performance review
   - Monthly risk assessment
   - Quarterly strategy optimization

### Daily Checklist for Live Trading

Every trading day:

- [ ] Check bot is running (`ps aux | grep python`)
- [ ] Review overnight logs for errors
- [ ] Verify account balance in Alpaca dashboard
- [ ] Check open positions match expectations
- [ ] Monitor first trade of the day closely
- [ ] Review daily P&L before market close

## Troubleshooting Live Trading Issues

### Issue: Orders Not Filling

**Symptoms**: Strategy generates signals but no trades execute

**Possible Causes**:
1. Insufficient funds in account
2. Stock not available for trading
3. Market closed or halted
4. Position limits reached

**Solution**:
```bash
# Check account status
# Log in to Alpaca dashboard and verify:
# - Account balance
# - Buying power
# - Account status (active/restricted)
```

### Issue: Unexpected Losses

**Symptoms**: Losses higher than expected from backtests

**Possible Causes**:
1. Slippage (normal in live trading)
2. Market conditions changed
3. Strategy not working as expected
4. Emotional overrides

**Solution**:
1. Review execution logs
2. Compare fill prices to expected
3. Check if you're respecting stop losses
4. Consider reducing position sizes

### Issue: Bot Stopped Running

**Symptoms**: No recent log entries, trades not executing

**Solution**:
```bash
# Check if process is running
ps aux | grep python

# Check logs for errors
tail -100 trading.log | grep ERROR

# Restart if needed (and verify it's using live credentials)
python run_autonomous.py
```

### Issue: Accidentally Used Wrong API Keys

**Symptoms**: Trades going to paper account instead of live

**Solution**:
```bash
# Check your .env file
cat .env | grep ALPACA

# Verify it shows:
# ALPACA_PAPER=false
# ALPACA_API_KEY=<your live key>
# ALPACA_API_SECRET=<your live secret>
```

## Emergency Stop Procedures

### How to Stop Trading Immediately

If you need to stop everything right now:

1. **Stop the bot**:
   ```bash
   # Press Ctrl+C if running in terminal
   # Or kill the process
   ps aux | grep "run_autonomous.py"
   kill <PID>
   ```

2. **Close all positions** (if needed):
   - Log in to Alpaca dashboard
   - Go to Positions
   - Click "Close All" or close individually

3. **Prevent restart**:
   ```bash
   # Temporarily disable by changing config
   echo "ALPACA_PAPER=true" >> .env
   ```

### When to Stop Trading

Stop immediately if:
- ❌ You've hit your maximum loss tolerance
- ❌ Bot is behaving unexpectedly
- ❌ You see unusual market conditions
- ❌ Multiple trades hitting stop losses rapidly
- ❌ You feel uncomfortable or stressed

**Remember**: You can always stop, review, and restart. Better safe than sorry!

## Tax and Legal Considerations

### Important Reminders

1. **Trading Taxes**:
   - Keep records of all trades
   - Alpaca provides tax documents (1099)
   - Consult a tax professional
   - Capital gains rules apply

2. **Pattern Day Trading Rule** (US):
   - If you make 4+ day trades in 5 business days
   - AND those trades are more than 6% of your total trades
   - You need $25,000 minimum in your account
   - Alpaca will flag and restrict your account if violated

3. **Regulatory Compliance**:
   - Ensure you're allowed to trade in your jurisdiction
   - Understand your broker's terms of service
   - Know your tax obligations

## Success Tips for Live Trading

### Mental Preparation

1. **Accept Losses**:
   - Losses are part of trading
   - No strategy wins 100% of the time
   - Focus on long-term results

2. **Don't Overtrade**:
   - Stick to your system
   - Don't add strategies impulsively
   - Don't increase size after wins

3. **Keep Learning**:
   - Review what works and what doesn't
   - Adjust parameters based on evidence
   - Stay informed about markets

4. **Manage Stress**:
   - Don't check constantly
   - Trust your system
   - Take breaks if needed

### Performance Tracking

Create a trading journal:

```python
# Add to your strategy
import json
from datetime import datetime

def log_trade_to_journal(symbol, action, price, shares, reason):
    entry = {
        'date': datetime.now().isoformat(),
        'symbol': symbol,
        'action': action,
        'price': price,
        'shares': shares,
        'reason': reason,
    }
    with open('trading_journal.json', 'a') as f:
        f.write(json.dumps(entry) + '\n')
```

Review weekly:
- What worked?
- What didn't?
- Any patterns in losses?
- Any execution issues?

## Final Checklist Before Going Live

- [ ] **Completed 30+ days of paper trading**
- [ ] **Paper trading is profitable** (positive returns)
- [ ] **Understand all risk parameters** completely
- [ ] **Have live trading API keys** from Alpaca
- [ ] **Funded live trading account** with minimal capital
- [ ] **Updated .env with live keys** and ALPACA_PAPER=false
- [ ] **Verified configuration** shows "LIVE" mode
- [ ] **Set up monitoring** (logs, alerts)
- [ ] **Defined maximum loss** I'm willing to accept
- [ ] **Have emergency stop procedure** ready
- [ ] **Informed family/partner** (if applicable)
- [ ] **Written trading plan** in place
- [ ] **Accept I may lose money** and I'm okay with that
- [ ] **Will not panic** over normal losses
- [ ] **Will follow the system** and not override it
- [ ] **Understand tax implications**
- [ ] **Ready to monitor closely** for first week

## Summary

Going live is a big step. Here's what you need to remember:

1. ✅ **Start small** - Use minimal capital initially
2. ✅ **Test thoroughly** - 30+ days paper trading minimum
3. ✅ **Set strict limits** - Daily loss, position size, etc.
4. ✅ **Monitor closely** - First week especially
5. ✅ **Scale gradually** - Only increase if profitable
6. ✅ **Expect lower returns** - Live ≠ Paper performance
7. ✅ **Have a plan** - Know when to stop
8. ✅ **Manage emotions** - Stick to your system
9. ✅ **Keep learning** - Review and improve
10. ✅ **Stay safe** - Only risk what you can afford to lose

**Remember**: There's no rush. Take your time, test thoroughly, and only go live when you're truly ready.

Good luck, and trade safely! 🚀

---

## Additional Resources

- **Alpaca Live Trading Docs**: https://alpaca.markets/docs/trading/
- **PyBroker Documentation**: https://www.pybroker.com
- **Risk Management**: Read "Trade Your Way to Financial Freedom" by Van Tharp
- **Psychology**: Read "Trading in the Zone" by Mark Douglas

## Disclaimer

This guide is for educational purposes only. Trading involves substantial risk of loss. The author and contributors are not responsible for any trading losses. Always consult with a licensed financial advisor before making investment decisions.
