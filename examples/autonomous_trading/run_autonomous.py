"""
Autonomous Trading Runner

This script runs the trading strategy continuously during market hours.
It checks the market periodically and executes the strategy when appropriate.

Usage:
    python run_autonomous.py

To stop: Press Ctrl+C
"""

import schedule
import time
import pytz
from datetime import datetime
from strategy import create_strategy, logger
from config import (
    EXECUTION_FREQUENCY,
    IS_PAPER_TRADING,
    get_config_summary
)

# Market configuration
MARKET_TIMEZONE = pytz.timezone('US/Eastern')
MARKET_OPEN_HOUR = 9
MARKET_OPEN_MINUTE = 30
MARKET_CLOSE_HOUR = 16
MARKET_CLOSE_MINUTE = 0


def is_market_open() -> bool:
    """
    Check if the US stock market is currently open.
    
    Returns:
        True if market is open, False otherwise
    """
    now = datetime.now(MARKET_TIMEZONE)
    
    # Check if it's a weekend
    if now.weekday() >= 5:  # Saturday = 5, Sunday = 6
        return False
    
    # Check if within trading hours
    market_open = now.replace(
        hour=MARKET_OPEN_HOUR,
        minute=MARKET_OPEN_MINUTE,
        second=0,
        microsecond=0
    )
    market_close = now.replace(
        hour=MARKET_CLOSE_HOUR,
        minute=MARKET_CLOSE_MINUTE,
        second=0,
        microsecond=0
    )
    
    is_open = market_open <= now <= market_close
    
    # Note: This doesn't account for market holidays
    # For production, use a market calendar library like pandas_market_calendars
    
    return is_open


def check_market_holiday() -> bool:
    """
    Check if today is a market holiday.
    
    Note: This is a basic implementation. For production use,
    consider using pandas_market_calendars or similar library.
    
    Returns:
        True if today is a holiday, False otherwise
    """
    # TODO: Implement proper holiday checking
    # For now, returning False
    return False


def execute_strategy():
    """
    Execute the trading strategy if market is open.
    
    This function is called periodically by the scheduler.
    """
    # Check if market is open
    if not is_market_open():
        logger.debug("Market is closed. Skipping execution.")
        return
    
    if check_market_holiday():
        logger.info("Market holiday. Skipping execution.")
        return
    
    try:
        logger.info("-" * 60)
        logger.info(f"Executing strategy at {datetime.now(MARKET_TIMEZONE)}")
        logger.info("-" * 60)
        
        # Create strategy with current date
        strategy = create_strategy()
        
        # For paper trading / backtesting
        # Note: For actual live trading, you would need to integrate
        # with your broker's live trading API
        
        logger.info("Strategy check completed.")
        
        # In a real implementation, you would:
        # 1. Get current positions from your broker
        # 2. Get current market data
        # 3. Run your strategy logic
        # 4. Place orders if signals are generated
        # 5. Update stop losses on existing positions
        
        logger.info("-" * 60)
        
    except Exception as e:
        logger.error(f"Error executing strategy: {e}", exc_info=True)
        # Send alert email if configured
        # send_alert("Strategy Execution Error", str(e))


def health_check():
    """Perform a health check of the system."""
    try:
        now = datetime.now(MARKET_TIMEZONE)
        market_status = "OPEN" if is_market_open() else "CLOSED"
        
        logger.info("=" * 60)
        logger.info("SYSTEM HEALTH CHECK")
        logger.info("=" * 60)
        logger.info(f"Time: {now.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        logger.info(f"Market Status: {market_status}")
        logger.info(f"Paper Trading: {IS_PAPER_TRADING}")
        logger.info("Status: OK")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)


def run_autonomous():
    """
    Run the autonomous trading system.
    
    This sets up the scheduler and runs the main loop.
    """
    logger.info("=" * 60)
    logger.info("AUTONOMOUS TRADING SYSTEM STARTING")
    logger.info("=" * 60)
    logger.info(get_config_summary())
    
    if not IS_PAPER_TRADING:
        logger.warning("!" * 60)
        logger.warning("WARNING: LIVE TRADING IS ENABLED!")
        logger.warning("Real money will be used for trades!")
        logger.warning("!" * 60)
        response = input("Type 'YES' to continue with live trading: ")
        if response != "YES":
            logger.info("Exiting...")
            return
    
    logger.info(f"Checking market every {EXECUTION_FREQUENCY} minutes")
    logger.info("Press Ctrl+C to stop")
    logger.info("=" * 60 + "\n")
    
    # Schedule strategy execution
    schedule.every(EXECUTION_FREQUENCY).minutes.do(execute_strategy)
    
    # Schedule health check every hour
    schedule.every(1).hours.do(health_check)
    
    # Run initial health check
    health_check()
    
    # Run initial execution if market is open
    if is_market_open():
        execute_strategy()
    else:
        logger.info("Market is currently closed. Waiting for market to open...")
        next_market_open = get_next_market_open()
        logger.info(f"Next market open: {next_market_open}")
    
    # Main loop
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("\n" + "=" * 60)
        logger.info("SHUTTING DOWN AUTONOMOUS TRADING SYSTEM")
        logger.info("=" * 60)
        logger.info("System stopped successfully.")
    except Exception as e:
        logger.error(f"Fatal error in main loop: {e}", exc_info=True)
        raise


def get_next_market_open() -> datetime:
    """
    Calculate the next market open time.
    
    Returns:
        Datetime of next market open
    """
    from datetime import timedelta
    
    now = datetime.now(MARKET_TIMEZONE)
    
    # If it's before market open today, return today's open
    market_open_today = now.replace(
        hour=MARKET_OPEN_HOUR,
        minute=MARKET_OPEN_MINUTE,
        second=0,
        microsecond=0
    )
    
    if now < market_open_today and now.weekday() < 5:
        return market_open_today
    
    # Otherwise, calculate next weekday
    days_ahead = 1
    if now.weekday() == 4:  # Friday
        days_ahead = 3  # Skip to Monday
    elif now.weekday() == 5:  # Saturday
        days_ahead = 2  # Skip to Monday
    
    next_open = now.replace(
        hour=MARKET_OPEN_HOUR,
        minute=MARKET_OPEN_MINUTE,
        second=0,
        microsecond=0
    )
    next_open = next_open + timedelta(days=days_ahead)
    
    return next_open


def main():
    """Main entry point."""
    try:
        run_autonomous()
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
