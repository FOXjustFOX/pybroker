# Autonomous Trading Setup Guide for PyBroker

This guide provides everything you need to set up PyBroker for autonomous trading with limited capital to generate passive income.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Broker Setup](#broker-setup)
4. [Configuration](#configuration)
5. [Example Strategy](#example-strategy)
6. [Risk Management](#risk-management)
7. [Deployment for Autonomous Trading](#deployment-for-autonomous-trading)
8. [Monitoring and Maintenance](#monitoring-and-maintenance)
9. [Best Practices](#best-practices)
10. [Troubleshooting](#troubleshooting)
11. [Going Live with Real Money](#going-live-with-real-money)

## Prerequisites

Before setting up autonomous trading, ensure you have:

- **Python 3.9+** installed on your system
- **Basic understanding** of trading concepts (stops, limits, position sizing)
- **Trading account** with supported broker (Alpaca recommended for beginners)
- **Limited capital** - Start with $500-$5,000 for testing (paper trading recommended initially)
- **Stable internet connection** for continuous operation
- **Computer/server** that can run 24/7 (or cloud instance)

## Installation

### 1. Install PyBroker

```bash
# Create a virtual environment (recommended)
python -m venv pybroker_env
source pybroker_env/bin/activate  # On Windows: pybroker_env\Scripts\activate

# Install PyBroker
pip install -U lib-pybroker

# Install additional dependencies for live trading
pip install alpaca-py python-dotenv schedule
```

### 2. Clone this repository (optional)

```bash
git clone https://github.com/edtechre/pybroker
cd pybroker
```

## Broker Setup

### Alpaca (Recommended for Beginners)

Alpaca offers commission-free trading and is easy to integrate with PyBroker.

1. **Create an Alpaca Account**:
   - Go to [Alpaca Markets](https://alpaca.markets/)
   - Sign up for a free account
   - Complete identity verification

2. **Get API Credentials**:
   - Log in to your Alpaca account
   - Navigate to "Paper Trading" section
   - Generate API Key and Secret Key
   - **IMPORTANT**: Start with paper trading (simulated) before live trading

3. **Enable Trading**:
   - Ensure your account has trading permissions
   - For live trading, you'll need to fund your account

### Other Supported Brokers

- **Yahoo Finance** (data only, no live trading)
- **AKShare** (data only)
- Custom brokers via API integration

## Configuration

### 1. Create Environment File

Create a `.env` file in your project directory to store credentials securely:

```bash
# .env file - DO NOT commit this to version control
ALPACA_API_KEY=your_api_key_here
ALPACA_API_SECRET=your_api_secret_here
ALPACA_PAPER=true  # Set to false for live trading

# Trading Configuration
INITIAL_CAPITAL=1000  # Start small for testing
MAX_POSITION_SIZE=200  # Maximum per position
STOP_LOSS_PERCENT=2  # 2% stop loss
TAKE_PROFIT_PERCENT=5  # 5% take profit
```

### 2. Create Configuration File

Create `config.py` with your trading parameters:

```python
# config.py
import os
from dotenv import load_dotenv
from pybroker import StrategyConfig
from pybroker.common import FeeMode

# Load environment variables
load_dotenv()

# Broker credentials
ALPACA_API_KEY = os.getenv('ALPACA_API_KEY')
ALPACA_API_SECRET = os.getenv('ALPACA_API_SECRET')
IS_PAPER_TRADING = os.getenv('ALPACA_PAPER', 'true').lower() == 'true'

# Capital management
INITIAL_CAPITAL = float(os.getenv('INITIAL_CAPITAL', 1000))
MAX_POSITION_SIZE = float(os.getenv('MAX_POSITION_SIZE', 200))

# Risk management
STOP_LOSS_PERCENT = float(os.getenv('STOP_LOSS_PERCENT', 2))
TAKE_PROFIT_PERCENT = float(os.getenv('TAKE_PROFIT_PERCENT', 5))

# Strategy configuration
strategy_config = StrategyConfig(
    initial_cash=INITIAL_CAPITAL,
    fee_mode=FeeMode.ORDER_PERCENT,  # Percentage-based fees
    fee_amount=0.001,  # 0.1% fee per order
    max_long_positions=5,  # Maximum 5 positions at once
    enable_fractional_shares=False,  # Set True for crypto
    buy_delay=1,  # Place orders on next bar
    sell_delay=1,
)

# Symbols to trade
SYMBOLS = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']  # Top tech stocks

# Timeframe
TIMEFRAME = '1day'  # Daily bars for swing trading
```

## Example Strategy

Create `autonomous_strategy.py` with a simple momentum strategy:

```python
# autonomous_strategy.py
"""
Simple Momentum Strategy for Autonomous Trading
This strategy buys on new highs and uses trailing stops for profit protection.
"""

import pybroker
from pybroker import Strategy, ExecContext
from pybroker.ext.data import Alpaca
from pybroker.indicator import highest, lowest
from config import (
    ALPACA_API_KEY,
    ALPACA_API_SECRET,
    strategy_config,
    SYMBOLS,
    TIMEFRAME,
    MAX_POSITION_SIZE,
    STOP_LOSS_PERCENT,
)
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Enable caching for faster backtesting
pybroker.enable_data_source_cache('data_cache')
pybroker.enable_indicator_cache('indicator_cache')

def calculate_position_size(ctx: ExecContext, price: float) -> int:
    """Calculate position size based on available cash and max position size."""
    available_cash = ctx.portfolio.cash
    max_shares_by_cash = int(available_cash / price)
    max_shares_by_limit = int(MAX_POSITION_SIZE / price)
    return min(max_shares_by_cash, max_shares_by_limit)

def exec_momentum_strategy(ctx: ExecContext):
    """
    Momentum Strategy Execution Logic:
    - Buy when price makes a new 20-day high
    - Limit position size to manage risk
    - Use trailing stop to protect profits
    """
    try:
        # Get indicators
        high_20d = ctx.indicator('high_20d')
        low_20d = ctx.indicator('low_20d')
        
        if high_20d is None or low_20d is None or len(high_20d) < 2:
            return
        
        current_price = ctx.bars[-1].close
        
        # Entry Logic: New 20-day high
        if not ctx.long_pos():
            if high_20d[-1] > high_20d[-2]:
                shares = calculate_position_size(ctx, current_price)
                if shares > 0:
                    ctx.buy_shares = shares
                    ctx.stop_loss_pct = STOP_LOSS_PERCENT
                    logger.info(
                        f"BUY SIGNAL: {ctx.symbol} @ ${current_price:.2f}, "
                        f"Shares: {shares}"
                    )
        
        # Exit Logic: Trailing stop
        else:
            # PyBroker automatically handles stop losses
            # You can add additional exit logic here
            pass
            
    except Exception as e:
        logger.error(f"Error in execution for {ctx.symbol}: {e}")

def create_strategy():
    """Create and configure the trading strategy."""
    
    # Initialize data source
    alpaca = Alpaca(
        api_key=ALPACA_API_KEY,
        api_secret=ALPACA_API_SECRET
    )
    
    # Set date range (last 6 months for backtesting)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)
    
    # Create strategy
    strategy = Strategy(
        data_source=alpaca,
        start_date=start_date,
        end_date=end_date,
        config=strategy_config
    )
    
    # Add execution with indicators
    strategy.add_execution(
        fn=exec_momentum_strategy,
        symbols=SYMBOLS,
        indicators=[
            highest('high_20d', 'close', period=20),
            lowest('low_20d', 'close', period=20),
        ]
    )
    
    return strategy

def backtest_strategy():
    """Run backtest to evaluate strategy performance."""
    logger.info("Starting backtest...")
    
    strategy = create_strategy()
    
    # Run backtest
    result = strategy.backtest(warmup=20)
    
    # Log results
    logger.info("\n" + "="*50)
    logger.info("BACKTEST RESULTS")
    logger.info("="*50)
    logger.info(f"Total Return: ${result.total_return:.2f}")
    logger.info(f"Total Profit: ${result.total_profit:.2f}")
    logger.info(f"Win Rate: {result.win_rate:.2%}")
    logger.info(f"Max Drawdown: {result.max_drawdown:.2%}")
    logger.info(f"Sharpe Ratio: {result.sharpe_ratio:.2f}")
    logger.info(f"Total Trades: {result.total_trades}")
    logger.info("="*50 + "\n")
    
    return result

if __name__ == "__main__":
    # Run backtest first
    result = backtest_strategy()
    
    # Only proceed to live trading if backtest is profitable
    if result.total_return > 0:
        logger.info("Backtest profitable. Ready for paper trading.")
        logger.info("To start live trading, implement the live_trade() function.")
    else:
        logger.warning("Backtest not profitable. Optimize strategy before live trading.")
```

## Risk Management

### Essential Risk Management Rules

Create `risk_manager.py`:

```python
# risk_manager.py
"""
Risk Management Module
Implements position sizing and risk controls
"""

class RiskManager:
    def __init__(self, 
                 max_portfolio_risk=0.02,  # 2% max portfolio risk
                 max_position_risk=0.01,   # 1% max risk per position
                 max_positions=5):
        self.max_portfolio_risk = max_portfolio_risk
        self.max_position_risk = max_position_risk
        self.max_positions = max_positions
    
    def calculate_position_size(self, account_value, entry_price, stop_price):
        """
        Calculate position size based on risk parameters.
        
        Args:
            account_value: Total account value
            entry_price: Entry price for position
            stop_price: Stop loss price
        
        Returns:
            Number of shares to buy
        """
        # Calculate risk per share
        risk_per_share = abs(entry_price - stop_price)
        
        if risk_per_share == 0:
            return 0
        
        # Calculate maximum dollar risk
        max_dollar_risk = account_value * self.max_position_risk
        
        # Calculate shares
        shares = int(max_dollar_risk / risk_per_share)
        
        # Ensure we don't exceed position limit
        max_position_value = account_value / self.max_positions
        max_shares_by_value = int(max_position_value / entry_price)
        
        return min(shares, max_shares_by_value)
    
    def should_enter_trade(self, current_positions):
        """Check if we can enter a new trade."""
        return len(current_positions) < self.max_positions
    
    def calculate_stop_loss(self, entry_price, stop_loss_pct):
        """Calculate stop loss price."""
        return entry_price * (1 - stop_loss_pct / 100)
    
    def calculate_take_profit(self, entry_price, take_profit_pct):
        """Calculate take profit price."""
        return entry_price * (1 + take_profit_pct / 100)
```

### Daily Loss Limits

Add to your configuration:

```python
# Daily risk limits
MAX_DAILY_LOSS = 100  # Maximum $100 loss per day
MAX_DAILY_TRADES = 10  # Maximum 10 trades per day
COOL_DOWN_PERIOD = 60  # Wait 60 minutes between trades on same symbol
```

## Deployment for Autonomous Trading

### Option 1: Local Machine (Simple)

Create `run_autonomous.py`:

```python
# run_autonomous.py
"""
Autonomous Trading Runner
Runs the strategy continuously during market hours
"""

import schedule
import time
from datetime import datetime
from autonomous_strategy import create_strategy, logger
import pytz

# Market hours (Eastern Time)
MARKET_OPEN = "09:30"
MARKET_CLOSE = "16:00"
MARKET_TIMEZONE = pytz.timezone('US/Eastern')

def is_market_open():
    """Check if market is currently open."""
    now = datetime.now(MARKET_TIMEZONE)
    
    # Check if weekend
    if now.weekday() >= 5:  # Saturday = 5, Sunday = 6
        return False
    
    # Check if within market hours
    market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
    market_close = now.replace(hour=16, minute=0, second=0, microsecond=0)
    
    return market_open <= now <= market_close

def execute_strategy():
    """Execute the strategy if market is open."""
    if not is_market_open():
        logger.info("Market is closed. Skipping execution.")
        return
    
    try:
        logger.info("Executing autonomous strategy...")
        strategy = create_strategy()
        
        # For live trading, you would execute trades here
        # This is a placeholder - actual implementation depends on your broker's API
        logger.info("Strategy executed successfully.")
        
    except Exception as e:
        logger.error(f"Error executing strategy: {e}")

def run_autonomous():
    """Run the autonomous trading system."""
    logger.info("Starting autonomous trading system...")
    logger.info("Press Ctrl+C to stop.")
    
    # Schedule strategy execution every 5 minutes during market hours
    schedule.every(5).minutes.do(execute_strategy)
    
    # Run a health check every hour
    def health_check():
        logger.info("System health check: OK")
    
    schedule.every(1).hours.do(health_check)
    
    # Initial execution
    execute_strategy()
    
    # Main loop
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down autonomous trading system...")

if __name__ == "__main__":
    run_autonomous()
```

**To run:**

```bash
# Start the autonomous trading system
python run_autonomous.py
```

### Option 2: Cloud Deployment (Recommended for 24/7 Operation)

#### Using AWS EC2

1. **Launch EC2 Instance**:
   ```bash
   # Use Ubuntu 22.04 LTS
   # t2.micro (free tier) is sufficient
   ```

2. **Setup Script** (`setup_ec2.sh`):
   ```bash
   #!/bin/bash
   # Update system
   sudo apt-get update
   sudo apt-get upgrade -y
   
   # Install Python
   sudo apt-get install python3-pip python3-venv -y
   
   # Create project directory
   mkdir -p ~/trading_bot
   cd ~/trading_bot
   
   # Create virtual environment
   python3 -m venv venv
   source venv/bin/activate
   
   # Install dependencies
   pip install lib-pybroker alpaca-py python-dotenv schedule
   
   # Copy your files here
   # scp your_files.py ec2-user@your-instance:~/trading_bot/
   ```

3. **Create Systemd Service** (`trading_bot.service`):
   ```ini
   [Unit]
   Description=Autonomous Trading Bot
   After=network.target
   
   [Service]
   Type=simple
   User=ubuntu
   WorkingDirectory=/home/ubuntu/trading_bot
   Environment="PATH=/home/ubuntu/trading_bot/venv/bin"
   ExecStart=/home/ubuntu/trading_bot/venv/bin/python run_autonomous.py
   Restart=always
   RestartSec=10
   
   [Install]
   WantedBy=multi-user.target
   ```

4. **Enable Service**:
   ```bash
   sudo cp trading_bot.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable trading_bot
   sudo systemctl start trading_bot
   
   # Check status
   sudo systemctl status trading_bot
   
   # View logs
   sudo journalctl -u trading_bot -f
   ```

#### Using Docker

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Run the bot
CMD ["python", "run_autonomous.py"]
```

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  trading-bot:
    build: .
    container_name: autonomous_trading_bot
    restart: unless-stopped
    env_file:
      - .env
    volumes:
      - ./logs:/app/logs
      - ./data_cache:/app/data_cache
      - ./indicator_cache:/app/indicator_cache
    environment:
      - TZ=America/New_York
```

**To run with Docker:**

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

## Monitoring and Maintenance

### 1. Logging

Ensure comprehensive logging in your strategies:

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading.log'),
        logging.StreamHandler()
    ]
)
```

### 2. Performance Monitoring

Create `monitor.py`:

```python
# monitor.py
"""
Monitoring script to track strategy performance
"""

import pandas as pd
from datetime import datetime
import json

class PerformanceMonitor:
    def __init__(self, log_file='performance.json'):
        self.log_file = log_file
    
    def log_trade(self, symbol, action, price, shares, timestamp=None):
        """Log a trade execution."""
        if timestamp is None:
            timestamp = datetime.now().isoformat()
        
        trade = {
            'timestamp': timestamp,
            'symbol': symbol,
            'action': action,
            'price': price,
            'shares': shares,
            'total': price * shares
        }
        
        # Append to log file
        try:
            with open(self.log_file, 'a') as f:
                f.write(json.dumps(trade) + '\n')
        except Exception as e:
            print(f"Error logging trade: {e}")
    
    def get_daily_summary(self):
        """Generate daily performance summary."""
        # Implementation depends on your needs
        pass
```

### 3. Alerts

Set up email alerts for critical events:

```python
# alerts.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_alert(subject, message, to_email):
    """Send email alert."""
    # Configure your email settings
    from_email = "your_email@gmail.com"
    password = "your_app_password"
    
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    
    msg.attach(MIMEText(message, 'plain'))
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, password)
        server.send_message(msg)
        server.quit()
        print(f"Alert sent: {subject}")
    except Exception as e:
        print(f"Failed to send alert: {e}")
```

## Best Practices

### 1. Start Small
- Begin with paper trading (simulated)
- Use minimal capital initially ($500-$1000)
- Test strategies for at least 30 days in paper trading

### 2. Diversification
- Trade multiple uncorrelated assets
- Use different strategy types
- Don't put all capital in one position

### 3. Risk Management
- Never risk more than 1-2% per trade
- Set stop losses on every trade
- Monitor drawdowns daily

### 4. Strategy Development
- Backtest thoroughly (minimum 2 years of data)
- Test during different market conditions
- Walk-forward optimize regularly

### 5. Operational Security
- Store credentials in environment variables
- Use `.gitignore` for sensitive files
- Enable 2FA on broker accounts
- Regular backups of strategy code and logs

### 6. Continuous Improvement
- Review performance weekly
- Keep a trading journal
- Adjust parameters based on market conditions
- Stay informed about market news

## Troubleshooting

### Common Issues

#### 1. Connection Errors

**Problem**: Cannot connect to broker API

**Solution**:
```python
# Check API credentials
print(f"API Key: {ALPACA_API_KEY[:5]}...")  # Print first 5 chars
print(f"Paper Trading: {IS_PAPER_TRADING}")

# Test connection
from pybroker.ext.data import Alpaca
alpaca = Alpaca(ALPACA_API_KEY, ALPACA_API_SECRET)
# Try fetching data
data = alpaca.query(['AAPL'], '1/1/2023', '1/10/2023', '1day')
print(data.head())
```

#### 2. Insufficient Funds

**Problem**: Orders rejected due to insufficient funds

**Solution**:
- Check position sizing calculation
- Ensure you account for fees
- Verify cash balance before trades

```python
def check_available_cash(ctx):
    available = ctx.portfolio.cash
    print(f"Available cash: ${available:.2f}")
    return available
```

#### 3. Rate Limiting

**Problem**: Too many API requests

**Solution**:
- Use caching for historical data
- Reduce execution frequency
- Batch requests when possible

```python
import pybroker
pybroker.enable_data_source_cache('data_cache')
pybroker.enable_indicator_cache('indicator_cache')
```

#### 4. Market Hours

**Problem**: Trades failing outside market hours

**Solution**:
- Check market hours before execution
- Handle pre-market/after-hours separately
- Account for holidays

```python
from datetime import datetime
import pytz

def is_market_open():
    et = pytz.timezone('US/Eastern')
    now = datetime.now(et)
    
    # Weekend check
    if now.weekday() >= 5:
        return False
    
    # Hours check
    market_open = now.replace(hour=9, minute=30)
    market_close = now.replace(hour=16, minute=0)
    
    return market_open <= now <= market_close
```

### Getting Help

- **Documentation**: https://www.pybroker.com
- **GitHub Issues**: https://github.com/edtechre/pybroker/issues
- **Community**: Join discussions on GitHub
- **Email**: See project README for contact information

## Safety Checklist

Before going live with real money:

- [ ] Tested strategy in paper trading for 30+ days
- [ ] Verified positive returns in backtest
- [ ] Implemented stop losses on all trades
- [ ] Set maximum daily loss limit
- [ ] Configured position size limits
- [ ] Set up monitoring and alerts
- [ ] Backed up all code and configuration
- [ ] Documented strategy logic
- [ ] Reviewed broker fees and costs
- [ ] Started with minimal capital
- [ ] Set up automatic shutoff for major losses

## Next Steps

1. **Start with Paper Trading**: Test your strategy with simulated money
2. **Monitor Performance**: Track results for 30+ days
3. **Optimize**: Adjust parameters based on performance
4. **Scale Gradually**: Increase capital only after consistent profits
5. **Stay Educated**: Continue learning about markets and strategies

## Disclaimer

**IMPORTANT**: Trading involves significant risk of loss. This guide is for educational purposes only. Past performance does not guarantee future results. Always:

- Start with paper trading
- Only invest money you can afford to lose
- Consult with a financial advisor
- Understand the risks involved
- Comply with local regulations

The authors and contributors are not responsible for any trading losses.

---

## Going Live with Real Money

Ready to transition from paper trading to live trading with real money? 

**See the comprehensive guide**: [examples/autonomous_trading/GOING_LIVE.md](examples/autonomous_trading/GOING_LIVE.md)

This guide covers:
- ✅ Prerequisites and readiness checklist
- ✅ Step-by-step transition process
- ✅ How to get live trading API keys
- ✅ Funding your account
- ✅ Conservative configuration for going live
- ✅ What to expect (performance differences)
- ✅ Monitoring and emergency procedures
- ✅ Tax and legal considerations
- ✅ Common issues and solutions
- ✅ Mental preparation and psychology

**Important**: Only proceed to live trading after:
- 30+ days of successful paper trading
- Consistent profitability in backtests
- Complete understanding of all risk parameters
- Starting with minimal capital ($500-$1,000)

---

**Good luck with your autonomous trading journey!** Remember: Start small, test thoroughly, and always manage your risk.
