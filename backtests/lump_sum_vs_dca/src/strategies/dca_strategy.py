"""
적립투자 전략
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


class DollarCostAverageStrategy(BaseStrategy):
    """적립투자 전략"""
    
    def execute(self, data: pd.DataFrame) -> Dict[str, Any]:
        """적립투자 실행"""
        # 날짜 컬럼 처리
        data['date'] = data['Date']
        data['year'] = pd.to_datetime(data['Date']).dt.year
        data['month'] = pd.to_datetime(data['Date']).dt.month
        
        monthly_amount = self.config.get_dca_monthly_amount()
        
        # 적립투자 실행
        current_year = self.config.start_year
        current_month = self.config.start_month
        
        for i in range(self.config.dca_months):
            # 해당 년월의 첫 거래일 찾기
            month_data = data[
                (data['year'] == current_year) & 
                (data['month'] == current_month)
            ]
            
            if not month_data.empty:
                first_trade_day = month_data.iloc[0]
                investment_price = first_trade_day['Close']
                shares = monthly_amount / investment_price
                
                # 거래 기록
                self.add_trade(
                    date=str(first_trade_day['date']),
                    price=investment_price,
                    amount=monthly_amount,
                    shares=shares
                )
            
            # 다음 월로 이동
            current_month += 1
            if current_month > 12:
                current_month = 1
                current_year += 1
        
        return {
            'strategy': 'dca',
            'trades': self.trades,
            'portfolio': self.portfolio,
            'data': data
        }