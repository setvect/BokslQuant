"""
성과 분석 모듈
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List
from datetime import datetime


class PerformanceAnalyzer:
    """성과 분석기"""
    
    def __init__(self):
        self.risk_free_rate = 0.02  # 무위험 수익률 2%
    
    def calculate_metrics(self, backtest_result: Dict[str, Any]) -> Dict[str, Any]:
        """성과 지표 계산"""
        daily_returns = backtest_result['daily_returns']
        portfolio = backtest_result['portfolio']
        
        if daily_returns.empty:
            return self._empty_metrics()
        
        # 최종 수익률 계산
        final_value = daily_returns.iloc[-1]['current_value']
        total_invested = daily_returns.iloc[-1]['invested_amount']
        final_return = (final_value - total_invested) / total_invested
        
        # CAGR 계산
        days = len(daily_returns)
        years = days / 365.25
        cagr = (final_value / total_invested) ** (1/years) - 1 if years > 0 else 0
        
        # MDD 계산
        mdd = self._calculate_mdd(daily_returns)
        
        # 샤프 지수 계산
        sharpe_ratio = self._calculate_sharpe_ratio(daily_returns)
        
        # 변동성 계산
        volatility = self._calculate_volatility(daily_returns)
        
        # 승률 계산 (일별 수익률 기준)
        win_rate = self._calculate_win_rate(daily_returns)
        
        return {
            'final_return': final_return,
            'cagr': cagr,
            'mdd': mdd,
            'sharpe_ratio': sharpe_ratio,
            'volatility': volatility,
            'win_rate': win_rate,
            'total_invested': total_invested,
            'final_value': final_value,
            'average_price': portfolio['average_price'],
            'total_shares': portfolio['total_shares'],
            'investment_period_days': days,
            'investment_period_years': years
        }
    
    def _calculate_mdd(self, daily_returns: pd.DataFrame) -> float:
        """최대 손실(MDD) 계산"""
        if daily_returns.empty:
            return 0
        
        # 백테스터에서 계산된 drawdown 컬럼 사용
        if 'drawdown' in daily_returns.columns:
            # drawdown 컬럼의 최솟값이 MDD (가장 큰 손실)
            return abs(daily_returns['drawdown'].min())
        
        # 백업: drawdown 컬럼이 없는 경우 기존 방식 사용
        values = daily_returns['current_value'].values
        invested = daily_returns['invested_amount'].values
        
        # 각 시점에서의 수익률
        returns = (values - invested) / invested
        
        # 최고점 대비 하락폭 계산
        peak = np.maximum.accumulate(returns)
        drawdown = (peak - returns)
        
        return np.max(drawdown)
    
    def _calculate_sharpe_ratio(self, daily_returns: pd.DataFrame) -> float:
        """샤프 지수 계산"""
        if len(daily_returns) < 2:
            return 0
        
        # 포트폴리오 수익률 기준으로 일별 수익률 계산
        # total_return 컬럼의 일별 변화를 사용
        daily_returns_df = daily_returns.copy()
        daily_returns_df['portfolio_daily_return'] = daily_returns_df['total_return'].diff()
        daily_returns_pct = daily_returns_df['portfolio_daily_return'].dropna()
        
        if daily_returns_pct.empty or daily_returns_pct.std() == 0:
            return 0
        
        # 연평균 수익률과 변동성
        mean_return = daily_returns_pct.mean() * 365.25
        volatility = daily_returns_pct.std() * np.sqrt(365.25)
        
        return (mean_return - self.risk_free_rate) / volatility
    
    def _calculate_volatility(self, daily_returns: pd.DataFrame) -> float:
        """변동성 계산"""
        if len(daily_returns) < 2:
            return 0
        
        # 포트폴리오 수익률 기준으로 일별 수익률 계산
        # total_return 컬럼의 일별 변화를 사용
        daily_returns_df = daily_returns.copy()
        daily_returns_df['portfolio_daily_return'] = daily_returns_df['total_return'].diff()
        daily_returns_pct = daily_returns_df['portfolio_daily_return'].dropna()
        
        if daily_returns_pct.empty:
            return 0
        
        # 연환산 변동성
        return daily_returns_pct.std() * np.sqrt(365.25)
    
    def _calculate_win_rate(self, daily_returns: pd.DataFrame) -> float:
        """승률 계산"""
        if len(daily_returns) < 2:
            return 0
        
        # 일별 수익률 변화
        daily_changes = daily_returns['total_return'].diff().dropna()
        
        if daily_changes.empty:
            return 0
        
        # 상승 일수 / 전체 일수
        win_days = (daily_changes > 0).sum()
        total_days = len(daily_changes)
        
        return win_days / total_days
    
    def _empty_metrics(self) -> Dict[str, Any]:
        """빈 지표 반환"""
        return {
            'final_return': 0,
            'cagr': 0,
            'mdd': 0,
            'sharpe_ratio': 0,
            'volatility': 0,
            'win_rate': 0,
            'total_invested': 0,
            'final_value': 0,
            'average_price': 0,
            'total_shares': 0,
            'investment_period_days': 0,
            'investment_period_years': 0
        }
    
    def compare_strategies(self, lump_sum_metrics: Dict[str, Any], 
                          dca_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """전략 비교 분석"""
        comparison = {}
        
        # 각 지표별 비교
        metrics_to_compare = [
            'final_return', 'cagr', 'mdd', 'sharpe_ratio', 
            'volatility', 'win_rate', 'final_value'
        ]
        
        for metric in metrics_to_compare:
            lump_sum_value = lump_sum_metrics.get(metric, 0)
            dca_value = dca_metrics.get(metric, 0)
            
            if metric in ['mdd', 'volatility']:  # 낮을수록 좋은 지표
                better_strategy = 'dca' if dca_value < lump_sum_value else 'lump_sum'
            else:  # 높을수록 좋은 지표
                better_strategy = 'lump_sum' if lump_sum_value > dca_value else 'dca'
            
            comparison[metric] = {
                'lump_sum': lump_sum_value,
                'dca': dca_value,
                'difference': lump_sum_value - dca_value,
                'better_strategy': better_strategy
            }
        
        return comparison
    
    def generate_summary(self, comparison_result: Dict[str, Any]) -> str:
        """분석 요약 생성"""
        lump_sum_metrics = self.calculate_metrics(comparison_result['lump_sum'])
        dca_metrics = self.calculate_metrics(comparison_result['dca'])
        
        summary = f"""
=== 일시투자 vs 적립투자 분석 결과 ===

투자 설정:
- 지수: {comparison_result.get('lump_sum', {}).get('symbol', 'N/A')}
- 투자 기간: {lump_sum_metrics.get('investment_period_years', 0):.1f}년
- 총 투자금: {lump_sum_metrics.get('total_invested', 0):,.0f}원

일시투자 결과:
- 최종 수익률: {lump_sum_metrics.get('final_return', 0)*100:.2f}%
- CAGR: {lump_sum_metrics.get('cagr', 0)*100:.2f}%
- MDD: {lump_sum_metrics.get('mdd', 0)*100:.2f}%
- 샤프 지수: {lump_sum_metrics.get('sharpe_ratio', 0):.3f}

적립투자 결과:
- 최종 수익률: {dca_metrics.get('final_return', 0)*100:.2f}%
- CAGR: {dca_metrics.get('cagr', 0)*100:.2f}%
- MDD: {dca_metrics.get('mdd', 0)*100:.2f}%
- 샤프 지수: {dca_metrics.get('sharpe_ratio', 0):.3f}

결론:
- 최종 수익률: {'일시투자' if lump_sum_metrics.get('final_return', 0) > dca_metrics.get('final_return', 0) else '적립투자'} 우세
- 위험 관리: {'일시투자' if lump_sum_metrics.get('mdd', 0) < dca_metrics.get('mdd', 0) else '적립투자'} 우세
"""
        
        return summary