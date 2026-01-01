"""
Configuration module for autonomous trading
Loads settings from environment variables and provides configuration objects
"""

import os
from typing import List
from dotenv import load_dotenv
from pybroker import StrategyConfig
from pybroker.common import FeeMode, PositionMode

# Load environment variables from .env file
load_dotenv()

# ============================================
# BROKER CONFIGURATION
# ============================================
ALPACA_API_KEY = os.getenv('ALPACA_API_KEY')
ALPACA_API_SECRET = os.getenv('ALPACA_API_SECRET')
IS_PAPER_TRADING = os.getenv('ALPACA_PAPER', 'true').lower() == 'true'

# Validate credentials
if not ALPACA_API_KEY or not ALPACA_API_SECRET:
    raise ValueError(
        "Missing Alpaca credentials. "
        "Please set ALPACA_API_KEY and ALPACA_API_SECRET in .env file"
    )

# ============================================
# CAPITAL MANAGEMENT
# ============================================
INITIAL_CAPITAL = float(os.getenv('INITIAL_CAPITAL', 1000))
MAX_POSITION_SIZE = float(os.getenv('MAX_POSITION_SIZE', 200))

# ============================================
# RISK MANAGEMENT
# ============================================
STOP_LOSS_PERCENT = float(os.getenv('STOP_LOSS_PERCENT', 2))
TAKE_PROFIT_PERCENT = float(os.getenv('TAKE_PROFIT_PERCENT', 5))
MAX_POSITIONS = int(os.getenv('MAX_POSITIONS', 5))
MAX_DAILY_LOSS = float(os.getenv('MAX_DAILY_LOSS', 100))
MAX_DAILY_TRADES = int(os.getenv('MAX_DAILY_TRADES', 10))

# ============================================
# TRADING SCHEDULE
# ============================================
EXECUTION_FREQUENCY = int(os.getenv('EXECUTION_FREQUENCY', 5))
COOLDOWN_PERIOD = int(os.getenv('COOLDOWN_PERIOD', 60))

# ============================================
# NOTIFICATION SETTINGS
# ============================================
ALERT_EMAIL = os.getenv('ALERT_EMAIL', '')
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
SMTP_USERNAME = os.getenv('SMTP_USERNAME', '')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
ENABLE_EMAIL_ALERTS = os.getenv('ENABLE_EMAIL_ALERTS', 'false').lower() == 'true'

# ============================================
# STRATEGY PARAMETERS
# ============================================
TIMEFRAME = os.getenv('TIMEFRAME', '1day')
INDICATOR_PERIOD = int(os.getenv('INDICATOR_PERIOD', 20))
MIN_VOLUME = int(os.getenv('MIN_VOLUME', 1000000))

# Symbols to trade (customize based on your preferences)
SYMBOLS: List[str] = [
    'AAPL',   # Apple
    'MSFT',   # Microsoft
    'GOOGL',  # Google
    'AMZN',   # Amazon
    'TSLA',   # Tesla
]

# Alternative symbol lists (uncomment to use)
# SYMBOLS_DIVIDEND = ['KO', 'PEP', 'JNJ', 'PG', 'XOM']  # Dividend stocks
# SYMBOLS_ETF = ['SPY', 'QQQ', 'IWM', 'DIA']  # ETFs
# SYMBOLS_CRYPTO = ['BTC/USD', 'ETH/USD']  # Crypto (requires enable_fractional_shares)

# ============================================
# MONITORING
# ============================================
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'trading.log')
PERFORMANCE_LOG = os.getenv('PERFORMANCE_LOG', 'performance.json')

# ============================================
# PYBROKER STRATEGY CONFIGURATION
# ============================================
strategy_config = StrategyConfig(
    initial_cash=INITIAL_CAPITAL,
    
    # Fee configuration (adjust based on your broker)
    fee_mode=FeeMode.ORDER_PERCENT,
    fee_amount=0.001,  # 0.1% per order
    
    # Position limits
    max_long_positions=MAX_POSITIONS,
    max_short_positions=0,  # Set to 0 for long-only strategy
    
    # Position mode
    position_mode=PositionMode.LONG_ONLY,  # Long only trading
    
    # Order execution delays
    buy_delay=1,   # Place buy orders on next bar
    sell_delay=1,  # Place sell orders on next bar
    
    # Fractional shares (enable for crypto)
    enable_fractional_shares=False,
    
    # Price rounding
    round_fill_price=True,
    
    # Exit configuration
    exit_on_last_bar=True,  # Close positions at end of data
    
    # Evaluation metrics
    bootstrap_samples=10000,
    bootstrap_sample_size=1000,
    
    # Return signals for analysis
    return_signals=True,
    return_stops=True,
)

# ============================================
# VALIDATION
# ============================================
def validate_config():
    """Validate configuration settings."""
    errors = []
    
    # Check capital
    if INITIAL_CAPITAL < 100:
        errors.append("INITIAL_CAPITAL should be at least $100")
    
    if MAX_POSITION_SIZE > INITIAL_CAPITAL:
        errors.append("MAX_POSITION_SIZE cannot exceed INITIAL_CAPITAL")
    
    # Check risk parameters
    if STOP_LOSS_PERCENT <= 0 or STOP_LOSS_PERCENT > 50:
        errors.append("STOP_LOSS_PERCENT should be between 0 and 50")
    
    if MAX_POSITIONS < 1:
        errors.append("MAX_POSITIONS should be at least 1")
    
    # Check if paper trading is enabled for safety
    if not IS_PAPER_TRADING:
        print("WARNING: Paper trading is DISABLED. You are using LIVE TRADING!")
        print("Make sure you understand the risks before proceeding.")
    
    if errors:
        raise ValueError("Configuration errors:\n" + "\n".join(f"- {e}" for e in errors))

# Validate on import
validate_config()

# ============================================
# HELPER FUNCTIONS
# ============================================
def get_config_summary() -> str:
    """Get a summary of current configuration."""
    return f"""
    ========================================
    AUTONOMOUS TRADING CONFIGURATION
    ========================================
    Trading Mode: {'PAPER' if IS_PAPER_TRADING else 'LIVE'}
    Initial Capital: ${INITIAL_CAPITAL:,.2f}
    Max Position Size: ${MAX_POSITION_SIZE:,.2f}
    Max Positions: {MAX_POSITIONS}
    Stop Loss: {STOP_LOSS_PERCENT}%
    Take Profit: {TAKE_PROFIT_PERCENT}%
    Max Daily Loss: ${MAX_DAILY_LOSS:,.2f}
    Symbols: {', '.join(SYMBOLS)}
    Timeframe: {TIMEFRAME}
    Execution Frequency: {EXECUTION_FREQUENCY} minutes
    ========================================
    """

if __name__ == "__main__":
    # Print configuration when run directly
    print(get_config_summary())
