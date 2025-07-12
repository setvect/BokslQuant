"""
성과 분석 지표 계산 모듈
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from ..strategies.investment_types import BacktestResult


class PerformanceAnalyzer:
    """성과 분석 클래스"""
    
    @staticmethod
    def calculate_detailed_metrics(result: BacktestResult) -> Dict:
        """
        상세 성과 지표 계산
        
        Args:
            result: 백테스팅 결과
            
        Returns:
            상세 성과 지표 딕셔너리
        """
        portfolio_value = result.portfolio_value
        total_invested = result.total_invested
        returns = result.returns
        
        metrics = {}
        
        # 기본 지표
        final_value = portfolio_value.iloc[-1]
        total_investment = total_invested.iloc[-1]
        
        metrics['basic'] = {
            'final_value': final_value,
            'total_invested': total_investment,
            'total_profit': final_value - total_investment,
            'total_return_pct': (final_value / total_investment - 1) * 100 if total_investment > 0 else 0
        }
        
        # 시간 기반 수익률
        trading_days = len(portfolio_value)
        years = trading_days / 252  # 252 영업일 = 1년
        
        if years > 0 and total_investment > 0:
            annualized_return = ((final_value / total_investment) ** (1/years) - 1) * 100
        else:
            annualized_return = 0
            
        metrics['time_based'] = {
            'trading_days': trading_days,
            'years': years,
            'annualized_return': annualized_return,
            'monthly_return': PerformanceAnalyzer._calculate_monthly_returns(portfolio_value),
            'yearly_return': PerformanceAnalyzer._calculate_yearly_returns(portfolio_value)
        }
        
        # 위험 지표
        metrics['risk'] = PerformanceAnalyzer._calculate_risk_metrics(returns, annualized_return)
        
        # 드로다운 분석
        metrics['drawdown'] = PerformanceAnalyzer._calculate_drawdown_metrics(portfolio_value, total_invested)
        
        # 승률 및 분포 분석
        metrics['distribution'] = PerformanceAnalyzer._calculate_distribution_metrics(returns)
        
        return metrics
    
    @staticmethod
    def _calculate_monthly_returns(portfolio_value: pd.Series) -> Dict:
        """월별 수익률 계산"""
        monthly_data = portfolio_value.resample('M').last()
        monthly_returns = monthly_data.pct_change().dropna() * 100
        
        return {
            'mean': monthly_returns.mean(),
            'std': monthly_returns.std(),
            'min': monthly_returns.min(),
            'max': monthly_returns.max(),
            'positive_months': (monthly_returns > 0).sum(),
            'negative_months': (monthly_returns < 0).sum(),
            'win_rate': (monthly_returns > 0).mean() * 100
        }
    
    @staticmethod
    def _calculate_yearly_returns(portfolio_value: pd.Series) -> Dict:
        """연도별 수익률 계산"""
        yearly_data = portfolio_value.resample('Y').last()
        yearly_returns = yearly_data.pct_change().dropna() * 100
        
        return {
            'mean': yearly_returns.mean(),
            'std': yearly_returns.std(),
            'min': yearly_returns.min(),
            'max': yearly_returns.max(),
            'positive_years': (yearly_returns > 0).sum(),
            'negative_years': (yearly_returns < 0).sum(),
            'win_rate': (yearly_returns > 0).mean() * 100
        }
    
    @staticmethod
    def _calculate_risk_metrics(returns: pd.Series, annualized_return: float) -> Dict:
        """위험 지표 계산"""
        # 변동성 (연환산)
        volatility = returns.std() * np.sqrt(252) * 100
        
        # 샤프 비율 (무위험 수익률 2% 가정)
        risk_free_rate = 2.0
        if volatility > 0:
            sharpe_ratio = (annualized_return - risk_free_rate) / volatility
        else:
            sharpe_ratio = 0
        
        # 소르티노 비율 (하방 위험만 고려)
        negative_returns = returns[returns < 0]
        if len(negative_returns) > 0:
            downside_deviation = negative_returns.std() * np.sqrt(252) * 100
            sortino_ratio = (annualized_return - risk_free_rate) / downside_deviation if downside_deviation > 0 else 0
        else:
            downside_deviation = 0
            sortino_ratio = float('inf') if annualized_return > risk_free_rate else 0
        
        # VaR (Value at Risk) - 5% 신뢰수준
        var_5 = np.percentile(returns, 5) * 100
        
        # CVaR (Conditional Value at Risk)
        cvar_5 = returns[returns <= np.percentile(returns, 5)].mean() * 100
        
        return {
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'sortino_ratio': sortino_ratio,
            'var_5': var_5,
            'cvar_5': cvar_5,
            'skewness': returns.skew(),
            'kurtosis': returns.kurtosis()
        }
    
    @staticmethod
    def _calculate_drawdown_metrics(portfolio_value: pd.Series, total_invested: pd.Series) -> Dict:
        """드로다운 지표 계산"""
        # 적립식투자의 경우 투자원금이 계속 증가하므로 비율로 계산
        if len(total_invested.unique()) > 1:  # 적립식투자
            cumulative_returns = portfolio_value / total_invested
        else:  # 일시투자
            cumulative_returns = portfolio_value / portfolio_value.iloc[0]
        
        # 최고점 대비 현재 손실률
        rolling_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - rolling_max) / rolling_max * 100
        
        # 최대 손실 (MDD)
        max_drawdown = drawdown.min()
        
        # 최대 손실 기간
        mdd_start_idx = drawdown.idxmin()
        recovery_value = rolling_max.loc[mdd_start_idx]
        
        # 회복 기간 계산
        recovery_dates = cumulative_returns[cumulative_returns.index > mdd_start_idx]
        recovery_idx = recovery_dates[recovery_dates >= recovery_value].index
        
        if len(recovery_idx) > 0:
            recovery_days = (recovery_idx[0] - mdd_start_idx).days
        else:
            recovery_days = (cumulative_returns.index[-1] - mdd_start_idx).days
        
        # 드로다운 발생 빈도
        drawdown_periods = []
        in_drawdown = False
        start_date = None
        
        for date, dd in drawdown.items():
            if dd < -1 and not in_drawdown:  # 1% 이상 손실시 드로다운 시작
                in_drawdown = True
                start_date = date
            elif dd >= 0 and in_drawdown:  # 회복시 드로다운 종료
                in_drawdown = False
                if start_date:
                    drawdown_periods.append((date - start_date).days)
        
        return {
            'max_drawdown': max_drawdown,
            'max_drawdown_date': mdd_start_idx,
            'recovery_days': recovery_days,
            'avg_drawdown_length': np.mean(drawdown_periods) if drawdown_periods else 0,
            'drawdown_frequency': len(drawdown_periods),
            'current_drawdown': drawdown.iloc[-1]
        }
    
    @staticmethod
    def _calculate_distribution_metrics(returns: pd.Series) -> Dict:
        """수익률 분포 분석"""
        positive_returns = returns[returns > 0]
        negative_returns = returns[returns < 0]
        
        return {
            'win_rate': (returns > 0).mean() * 100,
            'avg_win': positive_returns.mean() * 100 if len(positive_returns) > 0 else 0,
            'avg_loss': negative_returns.mean() * 100 if len(negative_returns) > 0 else 0,
            'profit_factor': abs(positive_returns.sum() / negative_returns.sum()) if len(negative_returns) > 0 and negative_returns.sum() != 0 else float('inf'),
            'best_day': returns.max() * 100,
            'worst_day': returns.min() * 100,
            'consecutive_wins': PerformanceAnalyzer._max_consecutive(returns > 0),
            'consecutive_losses': PerformanceAnalyzer._max_consecutive(returns < 0)
        }
    
    @staticmethod
    def _max_consecutive(series: pd.Series) -> int:
        """연속 발생 최대 횟수 계산"""
        max_count = 0
        current_count = 0
        
        for value in series:
            if value:
                current_count += 1
                max_count = max(max_count, current_count)
            else:
                current_count = 0
        
        return max_count


class ComparisonAnalyzer:
    """전략 비교 분석 클래스"""
    
    @staticmethod
    def compare_strategies(lump_sum_result: BacktestResult, 
                         dca_result: BacktestResult) -> Dict:
        """
        일시투자 vs 적립식투자 비교 분석
        
        Args:
            lump_sum_result: 일시투자 결과
            dca_result: 적립식투자 결과
            
        Returns:
            비교 분석 결과 딕셔너리
        """
        # 각 전략의 상세 지표 계산
        ls_metrics = PerformanceAnalyzer.calculate_detailed_metrics(lump_sum_result)
        dca_metrics = PerformanceAnalyzer.calculate_detailed_metrics(dca_result)
        
        comparison = {
            'lump_sum': ls_metrics,
            'dca': dca_metrics,
            'comparison': {}
        }
        
        # 수익률 비교
        ls_return = ls_metrics['basic']['total_return_pct']
        dca_return = dca_metrics['basic']['total_return_pct']
        
        comparison['comparison']['return_difference'] = ls_return - dca_return
        comparison['comparison']['better_strategy'] = 'lump_sum' if ls_return > dca_return else 'dca'
        
        # 위험 조정 수익률 비교
        ls_sharpe = ls_metrics['risk']['sharpe_ratio']
        dca_sharpe = dca_metrics['risk']['sharpe_ratio']
        
        comparison['comparison']['sharpe_difference'] = ls_sharpe - dca_sharpe
        comparison['comparison']['better_risk_adjusted'] = 'lump_sum' if ls_sharpe > dca_sharpe else 'dca'
        
        # 최대 손실 비교
        ls_mdd = ls_metrics['drawdown']['max_drawdown']
        dca_mdd = dca_metrics['drawdown']['max_drawdown']
        
        comparison['comparison']['mdd_difference'] = ls_mdd - dca_mdd
        comparison['comparison']['lower_risk'] = 'lump_sum' if ls_mdd > dca_mdd else 'dca'
        
        # 변동성 비교
        ls_vol = ls_metrics['risk']['volatility']
        dca_vol = dca_metrics['risk']['volatility']
        
        comparison['comparison']['volatility_difference'] = ls_vol - dca_vol
        
        # 투자 효율성 분석
        ls_invested = ls_metrics['basic']['total_invested']
        dca_invested = dca_metrics['basic']['total_invested']
        ls_profit = ls_metrics['basic']['total_profit']
        dca_profit = dca_metrics['basic']['total_profit']
        
        comparison['comparison']['investment_efficiency'] = {
            'ls_profit_per_invested': ls_profit / ls_invested if ls_invested > 0 else 0,
            'dca_profit_per_invested': dca_profit / dca_invested if dca_invested > 0 else 0,
            'absolute_profit_difference': ls_profit - dca_profit
        }
        
        return comparison
    
    @staticmethod
    def generate_summary_report(comparison: Dict) -> str:
        """
        비교 분석 요약 리포트 생성
        
        Args:
            comparison: 비교 분석 결과
            
        Returns:
            요약 리포트 문자열
        """
        ls_data = comparison['lump_sum']
        dca_data = comparison['dca']
        comp_data = comparison['comparison']
        
        report = []
        report.append("📊 투자 전략 비교 분석 리포트")
        report.append("=" * 50)
        
        # 기본 성과
        report.append("\n📈 수익률 비교:")
        report.append(f"일시투자: {ls_data['basic']['total_return_pct']:.2f}%")
        report.append(f"적립식투자: {dca_data['basic']['total_return_pct']:.2f}%")
        report.append(f"차이: {comp_data['return_difference']:.2f}%p")
        
        # 위험 조정 수익률
        report.append(f"\n⚖️ 샤프 비율 비교:")
        report.append(f"일시투자: {ls_data['risk']['sharpe_ratio']:.3f}")
        report.append(f"적립식투자: {dca_data['risk']['sharpe_ratio']:.3f}")
        report.append(f"차이: {comp_data['sharpe_difference']:.3f}")
        
        # 위험 분석
        report.append(f"\n📉 최대 손실 비교:")
        report.append(f"일시투자: {ls_data['drawdown']['max_drawdown']:.2f}%")
        report.append(f"적립식투자: {dca_data['drawdown']['max_drawdown']:.2f}%")
        
        # 승률 비교
        report.append(f"\n🎯 월별 승률 비교:")
        report.append(f"일시투자: {ls_data['time_based']['monthly_return']['win_rate']:.1f}%")
        report.append(f"적립식투자: {dca_data['time_based']['monthly_return']['win_rate']:.1f}%")
        
        # 결론
        better_strategy = comp_data['better_strategy']
        report.append(f"\n🏆 종합 결론:")
        strategy_name = "일시투자" if better_strategy == 'lump_sum' else "적립식투자"
        report.append(f"수익률 기준 우수 전략: {strategy_name}")
        
        better_risk_adjusted = comp_data['better_risk_adjusted']
        risk_strategy_name = "일시투자" if better_risk_adjusted == 'lump_sum' else "적립식투자"
        report.append(f"위험조정 수익률 기준 우수 전략: {risk_strategy_name}")
        
        return "\n".join(report)