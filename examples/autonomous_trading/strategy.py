"""
Simple Momentum Strategy for Autonomous Trading

This strategy implements a momentum-based approach that:
1. Buys stocks making new 20-day highs
2. Uses stop losses for risk management
3. Limits position sizes to manage capital
4. Tracks performance for continuous improvement

This is a starter strategy. Customize it based on your risk tolerance and goals.
"""

import pybroker
from pybroker import Strategy, ExecContext
from pybroker.ext.data import Alpaca
from pybroker.indicator import highest, lowest
from datetime import datetime, timedelta
import logging
from typing import Optional

# Import configuration
from config import (
    ALPACA_API_KEY,
    ALPACA_API_SECRET,
    strategy_config,
    SYMBOLS,
    TIMEFRAME,
    MAX_POSITION_SIZE,
    STOP_LOSS_PERCENT,
    INDICATOR_PERIOD,
)

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

# Enable caching for faster performance
pybroker.enable_data_source_cache('data_cache')
pybroker.enable_indicator_cache('indicator_cache')


def calculate_position_size(ctx: ExecContext, price: float) -> int:
    """
    Calculate position size based on available cash and max position size.
    
    Args:
        ctx: Execution context with portfolio information
        price: Current price per share
    
    Returns:
        Number of shares to buy
    """
    available_cash = ctx.portfolio.cash
    
    # Calculate max shares we can afford
    max_shares_by_cash = int(available_cash / price) if price > 0 else 0
    
    # Calculate max shares based on position size limit
    max_shares_by_limit = int(MAX_POSITION_SIZE / price) if price > 0 else 0
    
    # Take the minimum to respect both constraints
    shares = min(max_shares_by_cash, max_shares_by_limit)
    
    # Ensure at least some shares if we have enough cash
    if shares > 0 and (shares * price) < 10:  # Don't trade less than $10
        return 0
    
    return shares


def exec_momentum_strategy(ctx: ExecContext):
    """
    Momentum Strategy Execution Logic
    
    Entry Rules:
    - Buy when price makes a new 20-day high
    - Only enter if we have available capital
    - Respect position size limits
    
    Exit Rules:
    - Automatic stop loss at configured percentage
    - PyBroker handles the stop loss execution
    
    Args:
        ctx: Execution context with market data and portfolio state
    """
    try:
        # Get indicator data
        high_20d = ctx.indicator('high_20d')
        low_20d = ctx.indicator('low_20d')
        
        # Need at least 2 periods to compare
        if high_20d is None or len(high_20d) < 2:
            return
        
        # Get current price
        current_price = ctx.bars[-1].close
        
        # ENTRY LOGIC: New 20-day high
        if not ctx.long_pos():  # No current position
            # Check if we're making a new high
            is_new_high = high_20d[-1] > high_20d[-2]
            
            if is_new_high:
                # Calculate position size
                shares = calculate_position_size(ctx, current_price)
                
                if shares > 0:
                    # Place buy order
                    ctx.buy_shares = shares
                    ctx.stop_loss_pct = STOP_LOSS_PERCENT
                    
                    logger.info(
                        f"BUY SIGNAL: {ctx.symbol} @ ${current_price:.2f}, "
                        f"Shares: {shares}, "
                        f"Total: ${shares * current_price:.2f}, "
                        f"Stop Loss: {STOP_LOSS_PERCENT}%"
                    )
                else:
                    logger.debug(
                        f"Skipping {ctx.symbol}: insufficient capital for position"
                    )
        
        # EXIT LOGIC: Handled automatically by stop loss
        # You can add additional exit logic here if needed
        
    except Exception as e:
        logger.error(f"Error in execution for {ctx.symbol}: {e}", exc_info=True)


def create_strategy(start_date: Optional[datetime] = None, 
                   end_date: Optional[datetime] = None) -> Strategy:
    """
    Create and configure the trading strategy.
    
    Args:
        start_date: Start date for backtest (defaults to 6 months ago)
        end_date: End date for backtest (defaults to now)
    
    Returns:
        Configured Strategy object
    """
    # Initialize Alpaca data source
    alpaca = Alpaca(
        api_key=ALPACA_API_KEY,
        api_secret=ALPACA_API_SECRET
    )
    
    # Set default date range if not provided
    if end_date is None:
        end_date = datetime.now()
    if start_date is None:
        start_date = end_date - timedelta(days=180)  # 6 months
    
    logger.info(f"Creating strategy from {start_date.date()} to {end_date.date()}")
    
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
            highest('high_20d', 'close', period=INDICATOR_PERIOD),
            lowest('low_20d', 'close', period=INDICATOR_PERIOD),
        ]
    )
    
    return strategy


def backtest_strategy() -> pybroker.strategy.TestResult:
    """
    Run backtest to evaluate strategy performance.
    
    Returns:
        TestResult object with performance metrics
    """
    logger.info("="*60)
    logger.info("STARTING BACKTEST")
    logger.info("="*60)
    
    try:
        # Create strategy
        strategy = create_strategy()
        
        # Run backtest with warmup period
        result = strategy.backtest(warmup=INDICATOR_PERIOD)
        
        # Log results
        logger.info("\n" + "="*60)
        logger.info("BACKTEST RESULTS")
        logger.info("="*60)
        logger.info(f"Initial Capital:    ${strategy_config.initial_cash:,.2f}")
        logger.info(f"Final Value:        ${result.total_return + strategy_config.initial_cash:,.2f}")
        logger.info(f"Total Return:       ${result.total_return:,.2f}")
        logger.info(f"Total Profit:       ${result.total_profit:,.2f}")
        logger.info(f"Win Rate:           {result.win_rate:.2%}")
        logger.info(f"Max Drawdown:       {result.max_drawdown:.2%}")
        logger.info(f"Sharpe Ratio:       {result.sharpe_ratio:.2f}")
        logger.info(f"Profit Factor:      {result.profit_factor:.2f}")
        logger.info(f"Total Trades:       {result.total_trades}")
        logger.info(f"Winning Trades:     {result.total_wins}")
        logger.info(f"Losing Trades:      {result.total_losses}")
        logger.info("="*60 + "\n")
        
        # Performance summary
        if result.total_return > 0:
            logger.info("✓ Strategy is profitable in backtest")
            return_pct = (result.total_return / strategy_config.initial_cash) * 100
            logger.info(f"✓ Return: {return_pct:.2f}%")
        else:
            logger.warning("✗ Strategy is NOT profitable in backtest")
            logger.warning("✗ Consider adjusting parameters before live trading")
        
        if result.win_rate >= 0.5:
            logger.info(f"✓ Win rate is acceptable: {result.win_rate:.2%}")
        else:
            logger.warning(f"✗ Win rate is low: {result.win_rate:.2%}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error during backtest: {e}", exc_info=True)
        raise


def main():
    """Main entry point for the strategy."""
    try:
        # Run backtest
        result = backtest_strategy()
        
        # Provide guidance based on results
        logger.info("\n" + "="*60)
        logger.info("NEXT STEPS")
        logger.info("="*60)
        
        if result.total_return > 0:
            logger.info("1. Review the backtest results above")
            logger.info("2. Consider testing with different date ranges")
            logger.info("3. When ready, proceed to paper trading")
            logger.info("4. Use run_autonomous.py for automated execution")
        else:
            logger.info("1. Strategy needs optimization")
            logger.info("2. Try adjusting parameters in config.py:")
            logger.info("   - INDICATOR_PERIOD (currently {})".format(INDICATOR_PERIOD))
            logger.info("   - STOP_LOSS_PERCENT (currently {}%)".format(STOP_LOSS_PERCENT))
            logger.info("   - Different SYMBOLS")
            logger.info("3. Re-run backtest after changes")
        
        logger.info("="*60 + "\n")
        
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
