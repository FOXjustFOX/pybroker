# Getting Started with Autonomous Trading

This quick start guide will help you set up and run your first autonomous trading bot in under 10 minutes.

## Prerequisites

Before you begin, make sure you have:

- [ ] Python 3.9 or higher installed
- [ ] An Alpaca account (sign up at https://alpaca.markets/)
- [ ] Your Alpaca API credentials (API Key and Secret)
- [ ] Basic understanding of command line usage

## Step-by-Step Setup

### Step 1: Navigate to the Example Directory

```bash
cd examples/autonomous_trading
```

### Step 2: Run the Setup Script

**On Linux/Mac:**
```bash
./setup.sh
```

**On Windows:**
```cmd
setup.bat
```

The setup script will:
- Check Python version
- Create a virtual environment
- Install all dependencies
- Create configuration files
- Set up cache directories

### Step 3: Configure Your Credentials

Edit the `.env` file with your Alpaca credentials:

```bash
# On Linux/Mac
nano .env

# On Windows
notepad .env
```

Update these lines:
```
ALPACA_API_KEY=your_actual_api_key_here
ALPACA_API_SECRET=your_actual_api_secret_here
ALPACA_PAPER=true
```

**Important**: Keep `ALPACA_PAPER=true` for paper trading (recommended)!

### Step 4: Run Your First Backtest

Test the strategy with historical data:

```bash
python strategy.py
```

You should see output like:
```
============================================================
BACKTEST RESULTS
============================================================
Initial Capital:    $1,000.00
Final Value:        $1,123.45
Total Return:       $123.45
Win Rate:           55.23%
Max Drawdown:       -8.45%
Sharpe Ratio:       1.23
Total Trades:       12
============================================================
```

### Step 5: Start Autonomous Trading

If the backtest looks good, start the autonomous trading bot:

```bash
python run_autonomous.py
```

The bot will:
- Check the market every 5 minutes
- Execute trades during market hours
- Log all activity to `trading.log`
- Automatically stop when market closes

**To stop the bot**: Press `Ctrl+C`

## Understanding Your Configuration

### Capital Settings (in .env)

```
INITIAL_CAPITAL=1000        # Start with $1,000
MAX_POSITION_SIZE=200       # Max $200 per position
MAX_POSITIONS=5             # Max 5 positions at once
```

This means:
- You start with $1,000
- Each position is limited to $200
- You can hold up to 5 stocks simultaneously
- You'll always have cash reserves

### Risk Settings (in .env)

```
STOP_LOSS_PERCENT=2         # 2% stop loss
MAX_DAILY_LOSS=100          # Max $100 loss per day
MAX_DAILY_TRADES=10         # Max 10 trades per day
```

This means:
- Every position has a 2% stop loss
- Trading stops if you lose $100 in a day
- Maximum 10 trades per day
- Automatic risk management

### Trading Symbols (in config.py)

```python
SYMBOLS = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']
```

These are the stocks your bot will trade. You can customize this list!

## Monitoring Your Bot

### View Real-Time Logs

```bash
tail -f trading.log
```

Look for:
- `BUY SIGNAL` - When the bot buys a stock
- `SELL SIGNAL` - When the bot sells (on stop loss)
- `ERROR` - Any issues that need attention

### Check Performance

Run another backtest to see recent performance:

```bash
python strategy.py
```

## Customizing Your Strategy

### Change Trading Frequency

Edit `.env`:
```
EXECUTION_FREQUENCY=15  # Check every 15 minutes instead of 5
```

### Adjust Risk Parameters

Edit `.env`:
```
STOP_LOSS_PERCENT=3        # Wider stop loss
MAX_POSITION_SIZE=150      # Smaller positions
```

### Add Different Stocks

Edit `config.py`:
```python
SYMBOLS = [
    'SPY',   # S&P 500 ETF
    'QQQ',   # Nasdaq ETF
    'IWM',   # Russell 2000 ETF
]
```

### Modify Strategy Logic

Edit `strategy.py` - look for the `exec_momentum_strategy()` function:

```python
def exec_momentum_strategy(ctx: ExecContext):
    # Your custom trading logic here
    # Current: Buys on 20-day highs
    # You can change to any strategy you want
    pass
```

## Common Issues and Solutions

### Issue: "Missing Alpaca credentials"

**Solution**: Make sure you've edited `.env` with your actual API keys.

### Issue: "Connection error"

**Solution**: 
- Check your internet connection
- Verify your API keys are correct
- Make sure Alpaca service is running

### Issue: "No trades being placed"

**Solution**:
- Check if market is open (9:30 AM - 4:00 PM ET, weekdays)
- Review backtest results - strategy might not generate signals
- Check logs for any errors

### Issue: "Insufficient funds"

**Solution**:
- Reduce `MAX_POSITION_SIZE` in `.env`
- Reduce `MAX_POSITIONS` in `.env`
- Check your Alpaca account balance

## Safety Checklist

Before going live with real money:

- [ ] Tested with paper trading for 30+ days
- [ ] Strategy is profitable in backtests
- [ ] Understand all risk parameters
- [ ] Set up monitoring and alerts
- [ ] Have a plan for when things go wrong
- [ ] Start with minimal capital ($500-$1000)
- [ ] Reviewed all configuration settings

## Next Steps

### For Beginners

1. Keep paper trading for at least 30 days
2. Study the strategy code to understand how it works
3. Read the full documentation in AUTONOMOUS_TRADING_SETUP.md
4. Learn about different trading strategies

### For Advanced Users

1. Implement more sophisticated strategies
2. Add machine learning models (see PyBroker docs)
3. Set up cloud deployment for 24/7 operation
4. Implement advanced risk management
5. Add multiple strategies for diversification

## Getting Help

- **Documentation**: Check AUTONOMOUS_TRADING_SETUP.md for detailed info
- **PyBroker Docs**: https://www.pybroker.com
- **Alpaca Docs**: https://alpaca.markets/docs
- **Issues**: Open a GitHub issue if you find bugs

## Important Reminders

⚠️ **Always start with paper trading**

⚠️ **Never invest more than you can afford to lose**

⚠️ **Past performance doesn't guarantee future results**

⚠️ **Trading involves significant risk of loss**

⚠️ **This is educational material, not financial advice**

---

**Congratulations!** You've set up your first autonomous trading bot. Remember to start small, test thoroughly, and always manage your risk.

For questions or issues, refer to the main documentation or open an issue on GitHub.

Happy trading! 🚀
