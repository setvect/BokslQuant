"""
일시투자 vs 적립식투자 백테스팅 모듈
"""
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np


@dataclass
class InvestmentConfig:
    """투자 설정 클래스"""
    initial_capital: float = 100000  # 일시투자 초기 자본금
    monthly_amount: float = 1000     # 월 적립금액
    start_date: str = "2020-01-01"   # 투자 시작일
    end_date: str = "2023-12-31"     # 투자 종료일
    commission_rate: float = 0.001   # 수수료율 (0.1%)
    frequency: str = "monthly"       # 적립 주기 ('monthly', 'weekly', 'daily')


@dataclass
class BacktestResult:
    """백테스팅 결과 클래스"""
    portfolio_value: pd.Series      # 일별 포트폴리오 가치
    total_invested: pd.Series       # 누적 투자원금
    returns: pd.Series              # 수익률 시계열
    shares_held: pd.Series          # 보유 주식 수
    metrics: Dict                   # 성과 지표
    
    def get_final_return(self) -> float:
        """최종 수익률 반환"""
        return (self.portfolio_value.iloc[-1] / self.total_invested.iloc[-1] - 1) * 100
    
    def get_total_profit(self) -> float:
        """총 수익 반환"""
        return self.portfolio_value.iloc[-1] - self.total_invested.iloc[-1]


class LumpSumStrategy:
    """일시투자 전략"""
    
    def __init__(self, config: InvestmentConfig):
        self.config = config
    
    def backtest(self, price_data: pd.DataFrame) -> BacktestResult:
        """일시투자 백테스팅 실행"""
        # 날짜 범위로 데이터 필터링
        start_date = pd.to_datetime(self.config.start_date, utc=True)
        end_date = pd.to_datetime(self.config.end_date, utc=True)
        
        # 인덱스가 이미 datetime 형태인 경우 그대로 사용
        if not isinstance(price_data.index, pd.DatetimeIndex):
            price_data.index = pd.to_datetime(price_data.index, utc=True)
        filtered_data = price_data[(price_data.index >= start_date) & 
                                  (price_data.index <= end_date)].copy()
        
        if filtered_data.empty:
            raise ValueError("지정된 기간에 해당하는 데이터가 없습니다.")
        
        # 첫 거래일에 일시투자
        initial_price = filtered_data['Close'].iloc[0]
        commission = self.config.initial_capital * self.config.commission_rate
        investable_amount = self.config.initial_capital - commission
        shares = investable_amount / initial_price
        
        # 일별 포트폴리오 가치 계산
        portfolio_value = shares * filtered_data['Close']
        total_invested = pd.Series(self.config.initial_capital, 
                                  index=filtered_data.index)
        shares_held = pd.Series(shares, index=filtered_data.index)
        
        # 수익률 계산 (전일 대비)
        returns = portfolio_value.pct_change().fillna(0)
        
        # 성과 지표 계산
        metrics = self._calculate_metrics(portfolio_value, total_invested, returns)
        
        return BacktestResult(
            portfolio_value=portfolio_value,
            total_invested=total_invested,
            returns=returns,
            shares_held=shares_held,
            metrics=metrics
        )
    
    def _calculate_metrics(self, portfolio_value: pd.Series, 
                          total_invested: pd.Series, 
                          returns: pd.Series) -> Dict:
        """성과 지표 계산"""
        final_value = portfolio_value.iloc[-1]
        initial_investment = total_invested.iloc[0]
        
        # 총 수익률
        total_return = (final_value / initial_investment - 1) * 100
        
        # 연평균 수익률
        years = len(portfolio_value) / 252  # 252 영업일 = 1년
        annualized_return = ((final_value / initial_investment) ** (1/years) - 1) * 100
        
        # 변동성 (연환산)
        volatility = returns.std() * np.sqrt(252) * 100
        
        # 샤프 비율 (무위험 수익률 2% 가정)
        risk_free_rate = 0.02
        sharpe_ratio = (annualized_return / 100 - risk_free_rate) / (volatility / 100)
        
        # 최대 손실 (MDD)
        cumulative_returns = (portfolio_value / initial_investment)
        rolling_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - rolling_max) / rolling_max * 100
        max_drawdown = drawdown.min()
        
        return {
            'total_return': total_return,
            'annualized_return': annualized_return,
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'final_value': final_value,
            'total_invested': initial_investment
        }


class DollarCostAveraging:
    """적립식투자 전략 (달러 코스트 애버리징)"""
    
    def __init__(self, config: InvestmentConfig):
        self.config = config
    
    def backtest(self, price_data: pd.DataFrame) -> BacktestResult:
        """적립식투자 백테스팅 실행"""
        # 날짜 범위로 데이터 필터링
        start_date = pd.to_datetime(self.config.start_date, utc=True)
        end_date = pd.to_datetime(self.config.end_date, utc=True)
        
        # 인덱스가 이미 datetime 형태인 경우 그대로 사용
        if not isinstance(price_data.index, pd.DatetimeIndex):
            price_data.index = pd.to_datetime(price_data.index, utc=True)
        filtered_data = price_data[(price_data.index >= start_date) & 
                                  (price_data.index <= end_date)].copy()
        
        if filtered_data.empty:
            raise ValueError("지정된 기간에 해당하는 데이터가 없습니다.")
        
        # 투자 일정 생성
        investment_dates = self._generate_investment_schedule(start_date, end_date, 
                                                            filtered_data.index)
        
        # 초기화
        total_shares = 0
        total_invested_amount = 0
        portfolio_values = []
        total_invested_series = []
        shares_held_series = []
        
        for date in filtered_data.index:
            # 해당 날짜에 투자가 있는지 확인
            if date in investment_dates:
                commission = self.config.monthly_amount * self.config.commission_rate
                investable_amount = self.config.monthly_amount - commission
                current_price = filtered_data.loc[date, 'Close']
                new_shares = investable_amount / current_price
                total_shares += new_shares
                total_invested_amount += self.config.monthly_amount
            
            # 현재 포트폴리오 가치 계산
            current_price = filtered_data.loc[date, 'Close']
            portfolio_value = total_shares * current_price
            
            portfolio_values.append(portfolio_value)
            total_invested_series.append(total_invested_amount)
            shares_held_series.append(total_shares)
        
        # Series 변환
        portfolio_value = pd.Series(portfolio_values, index=filtered_data.index)
        total_invested = pd.Series(total_invested_series, index=filtered_data.index)
        shares_held = pd.Series(shares_held_series, index=filtered_data.index)
        
        # 수익률 계산
        returns = portfolio_value.pct_change().fillna(0)
        
        # 성과 지표 계산
        metrics = self._calculate_metrics(portfolio_value, total_invested, returns)
        
        return BacktestResult(
            portfolio_value=portfolio_value,
            total_invested=total_invested,
            returns=returns,
            shares_held=shares_held,
            metrics=metrics
        )
    
    def _generate_investment_schedule(self, start_date: datetime, 
                                    end_date: datetime, 
                                    available_dates: pd.DatetimeIndex) -> List[datetime]:
        """투자 일정 생성"""
        investment_dates = []
        
        if self.config.frequency == "monthly":
            # 매월 첫 거래일에 투자
            current_date = start_date
            while current_date <= end_date:
                # 해당 월의 첫 거래일 찾기
                month_start = current_date.replace(day=1)
                month_dates = [d for d in available_dates 
                              if d.year == month_start.year and d.month == month_start.month]
                if month_dates:
                    investment_dates.append(min(month_dates))
                
                # 다음 달로 이동
                if current_date.month == 12:
                    current_date = current_date.replace(year=current_date.year + 1, month=1)
                else:
                    current_date = current_date.replace(month=current_date.month + 1)
        
        elif self.config.frequency == "weekly":
            # 매주 첫 거래일에 투자 (간단히 7일 간격으로 구현)
            current_date = start_date
            while current_date <= end_date:
                # 가장 가까운 거래일 찾기
                closest_date = min(available_dates, key=lambda x: abs((x - current_date).days))
                if abs((closest_date - current_date).days) <= 3:  # 3일 이내
                    investment_dates.append(closest_date)
                current_date += timedelta(days=7)
        
        elif self.config.frequency == "daily":
            # 매일 투자 (모든 거래일)
            investment_dates = available_dates.tolist()
        
        return sorted(list(set(investment_dates)))
    
    def _calculate_metrics(self, portfolio_value: pd.Series, 
                          total_invested: pd.Series, 
                          returns: pd.Series) -> Dict:
        """성과 지표 계산"""
        final_value = portfolio_value.iloc[-1]
        total_investment = total_invested.iloc[-1]
        
        if total_investment == 0:
            return {}
        
        # 총 수익률
        total_return = (final_value / total_investment - 1) * 100
        
        # 연평균 수익률
        years = len(portfolio_value) / 252
        annualized_return = ((final_value / total_investment) ** (1/years) - 1) * 100
        
        # 변동성 (연환산)
        volatility = returns.std() * np.sqrt(252) * 100
        
        # 샤프 비율
        risk_free_rate = 0.02
        sharpe_ratio = (annualized_return / 100 - risk_free_rate) / (volatility / 100) if volatility > 0 else 0
        
        # 최대 손실 (MDD)
        # 적립식의 경우 투자원금이 계속 증가하므로 조정된 계산 필요
        cumulative_returns = portfolio_value / total_invested
        cumulative_returns = cumulative_returns.dropna()
        if len(cumulative_returns) > 0:
            rolling_max = cumulative_returns.expanding().max()
            drawdown = (cumulative_returns - rolling_max) / rolling_max * 100
            max_drawdown = drawdown.min()
        else:
            max_drawdown = 0
        
        return {
            'total_return': total_return,
            'annualized_return': annualized_return,
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'final_value': final_value,
            'total_invested': total_investment
        }