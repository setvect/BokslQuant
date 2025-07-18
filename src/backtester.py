"""
백테스팅 엔진 모듈
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class Backtester:
    """백테스팅 엔진"""
    
    def __init__(self, config):
        self.config = config
    
    def load_data(self, symbol: str) -> pd.DataFrame:
        """데이터 로드"""
        file_path = self.config.get_symbol_file_path(symbol)
        data = pd.read_csv(file_path)
        
        # 날짜 컬럼 처리
        data['Date'] = pd.to_datetime(data['Date'], utc=True).dt.date
        data = data.sort_values('Date')
        
        return data
    
    def get_investment_period_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """투자 기간 데이터 필터링"""
        start_date = datetime(self.config.start_year, self.config.start_month, 1).date()
        end_date = start_date + relativedelta(years=self.config.investment_period_years)
        
        return data[(data['Date'] >= start_date) & (data['Date'] < end_date)]
    
    def calculate_daily_returns(self, data: pd.DataFrame, strategy_result: Dict[str, Any]) -> pd.DataFrame:
        """일별 수익률 계산"""
        portfolio = strategy_result['portfolio']
        trades = strategy_result['trades']
        
        # 투자 기간 데이터만 사용
        period_data = self.get_investment_period_data(data)
        
        results = []
        cumulative_invested = 0
        cumulative_shares = 0
        
        # 거래 일정을 딕셔너리로 변환
        trade_schedule = {}
        for trade in trades:
            trade_date = pd.to_datetime(trade['date']).date()
            trade_schedule[trade_date] = trade
        
        for idx, row in period_data.iterrows():
            current_date = row['Date']
            current_price = row['Close']
            
            # 해당 날짜에 거래가 있는지 확인
            if current_date in trade_schedule:
                trade = trade_schedule[current_date]
                cumulative_invested += trade['amount']
                cumulative_shares += trade['shares']
            
            # 평가 계산
            if cumulative_shares > 0:
                current_value = cumulative_shares * current_price
                average_price = cumulative_invested / cumulative_shares
                total_return = (current_value - cumulative_invested) / cumulative_invested
                daily_return = (current_price - average_price) / average_price
            else:
                current_value = 0
                average_price = 0
                total_return = 0
                daily_return = 0
            
            results.append({
                'date': current_date,
                'price': current_price,
                'invested_amount': cumulative_invested,
                'shares': cumulative_shares,
                'average_price': average_price,
                'current_value': current_value,
                'total_return': total_return,
                'daily_return': daily_return
            })
        
        # 전고점 수익률과 손실폭 계산
        df = pd.DataFrame(results)
        if not df.empty:
            # 최고점 수익률 (누적 최대값)
            df['peak_return'] = df['total_return'].cummax()
            
            # 올바른 Drawdown 계산: (현재 수익률 - 최고점 수익률) / (1 + 최고점 수익률)
            # 단, 최고점 수익률이 0보다 클 때만 적용
            df['drawdown'] = df.apply(lambda row: 
                (row['total_return'] - row['peak_return']) / (1 + row['peak_return']) 
                if row['peak_return'] > 0 
                else row['total_return'] - row['peak_return'], axis=1)
        
        return df
    
    def run_backtest(self, symbol: str, strategy_type: str) -> Dict[str, Any]:
        """백테스팅 실행 - 하위 클래스에서 구현"""
        raise NotImplementedError("하위 클래스에서 구현해야 합니다")
    
    def run_comparison(self, symbol: str) -> Dict[str, Any]:
        """비교 분석 - 하위 클래스에서 구현"""
        raise NotImplementedError("하위 클래스에서 구현해야 합니다")