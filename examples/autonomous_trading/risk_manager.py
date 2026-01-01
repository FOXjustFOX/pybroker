"""
Risk Management Module

Implements position sizing and risk controls for trading strategies.
"""

from typing import Dict, List, Tuple
from datetime import datetime, timedelta


class RiskManager:
    """
    Risk Manager for position sizing and risk controls.
    
    This class helps manage trading risk by:
    - Calculating appropriate position sizes
    - Enforcing maximum position limits
    - Tracking daily losses
    - Implementing cool-down periods
    """
    
    def __init__(self,
                 max_portfolio_risk: float = 0.02,
                 max_position_risk: float = 0.01,
                 max_positions: int = 5,
                 max_daily_loss: float = 100,
                 max_daily_trades: int = 10,
                 cooldown_minutes: int = 60):
        """
        Initialize Risk Manager.
        
        Args:
            max_portfolio_risk: Maximum portfolio risk as decimal (0.02 = 2%)
            max_position_risk: Maximum risk per position as decimal (0.01 = 1%)
            max_positions: Maximum number of concurrent positions
            max_daily_loss: Maximum dollar loss allowed per day
            max_daily_trades: Maximum number of trades per day
            cooldown_minutes: Minutes to wait between trades on same symbol
        """
        self.max_portfolio_risk = max_portfolio_risk
        self.max_position_risk = max_position_risk
        self.max_positions = max_positions
        self.max_daily_loss = max_daily_loss
        self.max_daily_trades = max_daily_trades
        self.cooldown_minutes = cooldown_minutes
        
        # Track daily metrics
        self.daily_loss = 0.0
        self.daily_trades = 0
        self.last_reset = datetime.now().date()
        
        # Track recent trades for cooldown
        self.recent_trades: Dict[str, datetime] = {}
    
    def reset_daily_metrics(self):
        """Reset daily tracking metrics at start of new day."""
        today = datetime.now().date()
        if today > self.last_reset:
            self.daily_loss = 0.0
            self.daily_trades = 0
            self.last_reset = today
            # Clear old cooldowns
            self.recent_trades.clear()
    
    def calculate_position_size(self,
                                account_value: float,
                                entry_price: float,
                                stop_price: float) -> int:
        """
        Calculate position size based on risk parameters.
        
        Uses the risk-based position sizing formula:
        Position Size = (Account Value × Risk %) / (Entry Price - Stop Price)
        
        Args:
            account_value: Total account value
            entry_price: Entry price for position
            stop_price: Stop loss price
        
        Returns:
            Number of shares to buy
        """
        # Calculate risk per share
        risk_per_share = abs(entry_price - stop_price)
        
        if risk_per_share == 0 or entry_price == 0:
            return 0
        
        # Calculate maximum dollar risk per position
        max_dollar_risk = account_value * self.max_position_risk
        
        # Calculate shares based on risk
        shares = int(max_dollar_risk / risk_per_share)
        
        # Ensure we don't exceed position size limit
        # (divide portfolio equally among max positions)
        max_position_value = account_value / self.max_positions
        max_shares_by_value = int(max_position_value / entry_price)
        
        # Take the minimum to respect both constraints
        return min(shares, max_shares_by_value)
    
    def should_enter_trade(self,
                          symbol: str,
                          current_positions: int) -> Tuple[bool, str]:
        """
        Check if we can enter a new trade.
        
        Args:
            symbol: Symbol to trade
            current_positions: Number of current open positions
        
        Returns:
            Tuple of (can_trade, reason)
        """
        self.reset_daily_metrics()
        
        # Check max positions
        if current_positions >= self.max_positions:
            return False, f"Max positions ({self.max_positions}) reached"
        
        # Check daily loss limit
        if self.daily_loss >= self.max_daily_loss:
            return False, f"Daily loss limit (${self.max_daily_loss}) reached"
        
        # Check daily trade limit
        if self.daily_trades >= self.max_daily_trades:
            return False, f"Daily trade limit ({self.max_daily_trades}) reached"
        
        # Check cooldown period for this symbol
        if symbol in self.recent_trades:
            time_since_last = datetime.now() - self.recent_trades[symbol]
            cooldown_remaining = (
                timedelta(minutes=self.cooldown_minutes) - time_since_last
            )
            if cooldown_remaining.total_seconds() > 0:
                minutes = int(cooldown_remaining.total_seconds() / 60)
                return False, f"Cooldown period: {minutes} minutes remaining"
        
        return True, "OK"
    
    def record_trade(self, symbol: str, profit_loss: float):
        """
        Record a trade for tracking.
        
        Args:
            symbol: Symbol that was traded
            profit_loss: Profit or loss on the trade (negative for loss)
        """
        self.reset_daily_metrics()
        
        # Update metrics
        self.daily_trades += 1
        if profit_loss < 0:
            self.daily_loss += abs(profit_loss)
        
        # Record timestamp for cooldown
        self.recent_trades[symbol] = datetime.now()
    
    def calculate_stop_loss(self,
                           entry_price: float,
                           stop_loss_pct: float) -> float:
        """
        Calculate stop loss price.
        
        Args:
            entry_price: Entry price per share
            stop_loss_pct: Stop loss percentage (2 = 2%)
        
        Returns:
            Stop loss price
        """
        return entry_price * (1 - stop_loss_pct / 100)
    
    def calculate_take_profit(self,
                             entry_price: float,
                             take_profit_pct: float) -> float:
        """
        Calculate take profit price.
        
        Args:
            entry_price: Entry price per share
            take_profit_pct: Take profit percentage (5 = 5%)
        
        Returns:
            Take profit price
        """
        return entry_price * (1 + take_profit_pct / 100)
    
    def get_risk_metrics(self) -> Dict[str, any]:
        """
        Get current risk metrics.
        
        Returns:
            Dictionary of risk metrics
        """
        self.reset_daily_metrics()
        
        return {
            'daily_loss': self.daily_loss,
            'daily_trades': self.daily_trades,
            'loss_limit_remaining': max(0, self.max_daily_loss - self.daily_loss),
            'trades_limit_remaining': max(0, self.max_daily_trades - self.daily_trades),
            'last_reset': self.last_reset.isoformat(),
        }


# Example usage
if __name__ == "__main__":
    # Create risk manager
    risk_mgr = RiskManager(
        max_portfolio_risk=0.02,  # 2% max portfolio risk
        max_position_risk=0.01,   # 1% max per position
        max_positions=5,
        max_daily_loss=100,       # $100 max daily loss
        max_daily_trades=10
    )
    
    # Example: Calculate position size
    account_value = 10000  # $10,000 account
    entry_price = 150.00   # Entry at $150
    stop_price = 147.00    # Stop at $147 (2% stop)
    
    shares = risk_mgr.calculate_position_size(
        account_value,
        entry_price,
        stop_price
    )
    
    print(f"Account Value: ${account_value:,.2f}")
    print(f"Entry Price: ${entry_price:.2f}")
    print(f"Stop Price: ${stop_price:.2f}")
    print(f"Risk per share: ${entry_price - stop_price:.2f}")
    print(f"Recommended shares: {shares}")
    print(f"Position value: ${shares * entry_price:,.2f}")
    print(f"Max risk: ${shares * (entry_price - stop_price):.2f}")
    
    # Check if we can trade
    can_trade, reason = risk_mgr.should_enter_trade('AAPL', current_positions=2)
    print(f"\nCan trade AAPL? {can_trade} - {reason}")
    
    # Get risk metrics
    metrics = risk_mgr.get_risk_metrics()
    print(f"\nRisk Metrics:")
    for key, value in metrics.items():
        print(f"  {key}: {value}")
