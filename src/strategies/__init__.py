"""
Investment strategies module
"""

from .base_strategy import BaseStrategy
from .strategy_factory import StrategyFactory

__all__ = ['BaseStrategy', 'StrategyFactory']