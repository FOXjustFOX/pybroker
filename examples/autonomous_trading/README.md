# Autonomous Trading Example

This directory contains a complete example of setting up PyBroker for autonomous trading with limited capital.

## What's Included

- **config.py** - Configuration management with environment variables
- **strategy.py** - Simple momentum trading strategy
- **run_autonomous.py** - Autonomous trading runner with scheduling
- **risk_manager.py** - Risk management and position sizing utilities
- **.env.example** - Template for environment variables
- **setup.sh / setup.bat** - Automated setup scripts
- **GETTING_STARTED.md** - Step-by-step beginner guide

## Quick Start

**New to trading bots?** Start with [GETTING_STARTED.md](GETTING_STARTED.md) for a beginner-friendly walkthrough.

**Experienced user?** Follow the steps below:

### 1. Install Dependencies

```bash
pip install lib-pybroker python-dotenv schedule
```

### 2. Configure Your Settings

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your settings
nano .env
```

**Important**: Get your Alpaca API credentials from https://alpaca.markets/

### 3. Test the Strategy

```bash
# Run a backtest first
python strategy.py
```

This will:
- Download historical data
- Run the strategy over the past 6 months
- Show performance metrics
- Cache data for faster future runs

### 4. Start Autonomous Trading (Paper Trading)

```bash
# Make sure ALPACA_PAPER=true in your .env file
python run_autonomous.py
```

This will:
- Check the market every 5 minutes (configurable)
- Execute trades during market hours
- Log all activity
- Skip when market is closed

## Safety Features

### Built-in Risk Controls

1. **Position Limits**: Maximum 5 positions by default
2. **Stop Losses**: 2% stop loss on every trade
3. **Position Sizing**: Limited to $200 per position
4. **Daily Loss Limit**: Stops trading after $100 daily loss
5. **Paper Trading**: Test with simulated money first

### Before Live Trading

- [ ] Test with paper trading for at least 30 days
- [ ] Verify profitability in backtests
- [ ] Understand all risks involved
- [ ] Start with minimal capital ($500-$1000)
- [ ] Set up monitoring and alerts

## Customization

### Change Trading Symbols

Edit `config.py`:

```python
SYMBOLS = ['AAPL', 'MSFT', 'GOOGL']  # Your preferred stocks
```

### Adjust Risk Parameters

Edit `.env`:

```
STOP_LOSS_PERCENT=3       # 3% stop loss
MAX_POSITION_SIZE=300     # $300 per position
MAX_POSITIONS=3           # Max 3 positions
```

### Modify Strategy Logic

Edit `strategy.py` - the `exec_momentum_strategy()` function:

```python
def exec_momentum_strategy(ctx: ExecContext):
    # Your custom logic here
    pass
```

## File Structure

```
autonomous_trading/
├── .env.example           # Environment variables template
├── config.py              # Configuration loader
├── strategy.py            # Trading strategy implementation
├── run_autonomous.py      # Autonomous runner
├── risk_manager.py        # Risk management utilities
└── README.md             # This file
```

## Understanding the Strategy

The included momentum strategy:

1. **Monitors** stock prices continuously
2. **Buys** when a stock makes a new 20-day high
3. **Sets** a 2% stop loss on entry
4. **Limits** position size to protect capital
5. **Exits** automatically on stop loss

This is a **starter strategy**. Real trading requires:
- More sophisticated entry/exit rules
- Better risk management
- Regular monitoring and adjustment
- Backtesting across different market conditions

## Monitoring Your Bot

### View Logs

```bash
# Real-time logs
tail -f trading.log

# Search logs
grep "BUY SIGNAL" trading.log
grep "ERROR" trading.log
```

### Check Performance

```bash
# View configuration
python config.py

# Run backtest
python strategy.py
```

## Deployment Options

### Local Machine

```bash
# Run in background
nohup python run_autonomous.py > output.log 2>&1 &

# Stop
pkill -f run_autonomous.py
```

### Cloud Server (AWS, DigitalOcean, etc.)

See the main [AUTONOMOUS_TRADING_SETUP.md](../../AUTONOMOUS_TRADING_SETUP.md) for detailed deployment instructions including:
- AWS EC2 setup
- Docker deployment
- Systemd service configuration
- Cloud instance recommendations

## Troubleshooting

### "Missing Alpaca credentials"

Make sure you've:
1. Created a `.env` file (copy from `.env.example`)
2. Added your API keys from Alpaca
3. Set `ALPACA_PAPER=true` for testing

### "Connection error"

Check that:
- Your API keys are correct
- You have internet connection
- Alpaca service is operational

### "Insufficient funds"

Adjust in `.env`:
- Reduce `MAX_POSITION_SIZE`
- Reduce `MAX_POSITIONS`
- Check your Alpaca account balance

### Data Download Issues

```bash
# Clear cache and retry
rm -rf data_cache/
rm -rf indicator_cache/
python strategy.py
```

## Resources

- **Main Setup Guide**: [AUTONOMOUS_TRADING_SETUP.md](../../AUTONOMOUS_TRADING_SETUP.md)
- **PyBroker Docs**: https://www.pybroker.com
- **Alpaca Docs**: https://alpaca.markets/docs

## Disclaimer

**Trading involves significant risk of loss.**

- This is educational material only
- Start with paper trading
- Never invest more than you can afford to lose
- Past performance doesn't guarantee future results
- Consult a financial advisor before live trading

## Support

For issues or questions:
- Check the main documentation
- Review PyBroker examples
- Open an issue on GitHub
- Contact the project maintainers

---

**Happy Trading!** Remember: Start small, test thoroughly, and always manage your risk.
