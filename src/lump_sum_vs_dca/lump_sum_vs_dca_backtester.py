"""
일시투자 vs 적립투자 백테스터
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
# 모듈 경로 설정
import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
sys.path.append(os.path.join(project_root, 'src'))

from backtester import Backtester as BaseBacktester
from strategy_factory import LumpSumVsDcaStrategyFactory


class LumpSumVsDcaBacktester(BaseBacktester):
    """일시투자 vs 적립투자 전용 백테스터"""
    
    def run_backtest(self, symbol: str, strategy_type: str) -> Dict[str, Any]:
        """백테스팅 실행"""
        # 데이터 로드
        data = self.load_data(symbol)
        
        # 전략 생성 및 실행
        strategy = LumpSumVsDcaStrategyFactory.create_strategy(strategy_type, self.config)
        strategy_result = strategy.execute(data)
        
        # 일별 수익률 계산
        daily_returns = self.calculate_daily_returns(data, strategy_result)
        
        # 결과 통합
        result = {
            'strategy_type': strategy_type,
            'symbol': symbol,
            'config': {
                'symbol': self.config.symbol,
                'start_year': self.config.start_year,
                'start_month': self.config.start_month,
                'investment_period_years': self.config.investment_period_years,
                'dca_months': self.config.dca_months,
                'initial_capital': self.config.initial_capital
            },
            'trades': strategy_result['trades'],
            'portfolio': strategy_result['portfolio'],
            'daily_returns': daily_returns,
            'raw_data': self.get_investment_period_data(data)
        }
        
        return result
    
    def run_comparison(self, symbol: str) -> Dict[str, Any]:
        """일시투자 vs 적립투자 비교 분석"""
        lump_sum_result = self.run_backtest(symbol, 'lump_sum')
        dca_result = self.run_backtest(symbol, 'dca')
        
        return {
            'lump_sum': lump_sum_result,
            'dca': dca_result,
            'comparison_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }