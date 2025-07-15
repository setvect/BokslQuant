"""
투자 전략 기본 클래스
"""
from abc import ABC, abstractmethod
from typing import Dict, Any
import pandas as pd


class BaseStrategy(ABC):
    """투자 전략 기본 클래스"""
    
    def __init__(self, config):
        self.config = config
        self.trades = []
        self.portfolio = {
            'total_invested': 0,
            'total_shares': 0,
            'average_price': 0
        }
    
    @abstractmethod
    def execute(self, data: pd.DataFrame) -> Dict[str, Any]:
        """전략 실행 메서드"""
        pass
    
    def add_trade(self, date: str, price: float, amount: float, shares: float):
        """거래 기록 추가"""
        self.trades.append({
            'date': date,
            'price': price,
            'amount': amount,
            'shares': shares
        })
        
        # 포트폴리오 업데이트
        self.portfolio['total_invested'] += amount
        self.portfolio['total_shares'] += shares
        if self.portfolio['total_shares'] > 0:
            self.portfolio['average_price'] = self.portfolio['total_invested'] / self.portfolio['total_shares']