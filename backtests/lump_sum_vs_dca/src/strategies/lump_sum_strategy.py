"""
일시투자 전략
"""
import pandas as pd
from typing import Dict, Any
# 모듈 경로 설정
import sys
import os
import importlib.util

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_dir))))
base_strategy_path = os.path.join(project_root, 'src', 'strategies', 'base_strategy.py')

# BaseStrategy 직접 import
spec = importlib.util.spec_from_file_location("base_strategy", base_strategy_path)
base_strategy_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base_strategy_module)
BaseStrategy = base_strategy_module.BaseStrategy


class LumpSumStrategy(BaseStrategy):
    """일시투자 전략"""
    
    def execute(self, data: pd.DataFrame) -> Dict[str, Any]:
        """일시투자 실행"""
        # 투자 시작 년월의 첫 거래일 찾기
        data['date'] = data['Date']
        data['year'] = pd.to_datetime(data['Date']).dt.year
        data['month'] = pd.to_datetime(data['Date']).dt.month
        
        # 시작 년월 데이터 필터링
        start_data = data[
            (data['year'] == self.config.start_year) & 
            (data['month'] == self.config.start_month)
        ]
        
        if start_data.empty:
            raise ValueError(f"투자 시작 시점({self.config.start_year}-{self.config.start_month:02d})에 데이터가 없습니다.")
        
        # 첫 거래일 데이터
        first_trade_day = start_data.iloc[0]
        investment_price = first_trade_day['Close']
        investment_amount = self.config.initial_capital
        shares = investment_amount / investment_price
        
        # 거래 기록
        self.add_trade(
            date=str(first_trade_day['date']),
            price=investment_price,
            amount=investment_amount,
            shares=shares
        )
        
        return {
            'strategy': 'lump_sum',
            'trades': self.trades,
            'portfolio': self.portfolio,
            'data': data
        }