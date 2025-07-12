"""
시각화 차트 생성 모듈
"""
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import pandas as pd
import numpy as np
from typing import Tuple, Optional
import os
from datetime import datetime
from ..strategies.investment_types import BacktestResult


class InvestmentVisualizer:
    """투자 전략 시각화 클래스"""
    
    def __init__(self, figsize: Tuple[int, int] = (15, 10), style: str = 'seaborn-v0_8'):
        """
        시각화 초기화
        
        Args:
            figsize: 그래프 크기
            style: matplotlib 스타일
        """
        self.figsize = figsize
        plt.style.use('default')  # seaborn 스타일 호환성 문제로 기본 스타일 사용
        sns.set_palette("husl")
        
        # 한글 폰트 설정 (한글 제목을 위해)
        plt.rcParams['font.family'] = 'DejaVu Sans'
        plt.rcParams['axes.unicode_minus'] = False
    
    def plot_portfolio_comparison(self, lump_sum_result: BacktestResult, 
                                dca_result: BacktestResult, 
                                index_name: str,
                                save_path: Optional[str] = None) -> str:
        """
        포트폴리오 가치 비교 차트
        
        Args:
            lump_sum_result: 일시투자 결과
            dca_result: 적립식투자 결과
            index_name: 지수명
            save_path: 저장 경로
            
        Returns:
            저장된 파일 경로
        """
        fig, axes = plt.subplots(2, 2, figsize=self.figsize)
        fig.suptitle(f'{index_name} 투자 전략 비교', fontsize=16, fontweight='bold')
        
        # 1. 포트폴리오 가치 비교
        ax1 = axes[0, 0]
        ax1.plot(lump_sum_result.portfolio_value.index, 
                lump_sum_result.portfolio_value.values,
                label='일시투자', linewidth=2, color='#2E86AB')
        ax1.plot(dca_result.portfolio_value.index, 
                dca_result.portfolio_value.values,
                label='적립식투자', linewidth=2, color='#F24236')
        ax1.set_title('포트폴리오 가치 비교')
        ax1.set_ylabel('포트폴리오 가치 ($)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        self._format_date_axis(ax1)
        
        # 2. 누적 투자금 대비 수익률
        ax2 = axes[0, 1]
        ls_return_ratio = lump_sum_result.portfolio_value / lump_sum_result.total_invested
        dca_return_ratio = dca_result.portfolio_value / dca_result.total_invested
        
        ax2.plot(ls_return_ratio.index, ls_return_ratio.values,
                label='일시투자', linewidth=2, color='#2E86AB')
        ax2.plot(dca_return_ratio.index, dca_return_ratio.values,
                label='적립식투자', linewidth=2, color='#F24236')
        ax2.axhline(y=1, color='gray', linestyle='--', alpha=0.5)
        ax2.set_title('수익률 비율 (포트폴리오 가치 / 투자원금)')
        ax2.set_ylabel('수익률 비율')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        self._format_date_axis(ax2)
        
        # 3. 누적 투자금 비교
        ax3 = axes[1, 0]
        ax3.plot(lump_sum_result.total_invested.index, 
                lump_sum_result.total_invested.values,
                label='일시투자', linewidth=2, color='#2E86AB')
        ax3.plot(dca_result.total_invested.index, 
                dca_result.total_invested.values,
                label='적립식투자', linewidth=2, color='#F24236')
        ax3.set_title('누적 투자 금액')
        ax3.set_ylabel('투자 금액 ($)')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        self._format_date_axis(ax3)
        
        # 4. 보유 주식 수 비교
        ax4 = axes[1, 1]
        ax4.plot(lump_sum_result.shares_held.index, 
                lump_sum_result.shares_held.values,
                label='일시투자', linewidth=2, color='#2E86AB')
        ax4.plot(dca_result.shares_held.index, 
                dca_result.shares_held.values,
                label='적립식투자', linewidth=2, color='#F24236')
        ax4.set_title('시간별 보유 주식 수')
        ax4.set_ylabel('주식 수')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        self._format_date_axis(ax4)
        
        plt.tight_layout()
        
        # 저장
        if save_path is None:
            save_path = f"results/charts/{index_name}_포트폴리오비교_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
        
        return save_path
    
    def plot_returns_analysis(self, lump_sum_result: BacktestResult, 
                            dca_result: BacktestResult, 
                            index_name: str,
                            save_path: Optional[str] = None) -> str:
        """
        수익률 분석 차트
        
        Args:
            lump_sum_result: 일시투자 결과
            dca_result: 적립식투자 결과
            index_name: 지수명
            save_path: 저장 경로
            
        Returns:
            저장된 파일 경로
        """
        fig, axes = plt.subplots(2, 2, figsize=self.figsize)
        fig.suptitle(f'{index_name} 수익률 분석', fontsize=16, fontweight='bold')
        
        # 1. 일별 수익률 분포
        ax1 = axes[0, 0]
        ax1.hist(lump_sum_result.returns * 100, bins=50, alpha=0.7, 
                label='일시투자', color='#2E86AB', density=True)
        ax1.hist(dca_result.returns * 100, bins=50, alpha=0.7, 
                label='적립식투자', color='#F24236', density=True)
        ax1.set_title('일별 수익률 분포')
        ax1.set_xlabel('일별 수익률 (%)')
        ax1.set_ylabel('밀도')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. 월별 수익률 히트맵 (일시투자)
        ax2 = axes[0, 1]
        ls_monthly_returns = self._calculate_monthly_returns_matrix(lump_sum_result.returns)
        if not ls_monthly_returns.empty:
            sns.heatmap(ls_monthly_returns, annot=True, fmt='.1f', cmap='RdYlGn', 
                       center=0, ax=ax2, cbar_kws={'label': '수익률 (%)'})
        ax2.set_title('일시투자 - 월별 수익률 히트맵 (%)')
        
        # 3. 월별 수익률 히트맵 (적립식투자)
        ax3 = axes[1, 0]
        dca_monthly_returns = self._calculate_monthly_returns_matrix(dca_result.returns)
        if not dca_monthly_returns.empty:
            sns.heatmap(dca_monthly_returns, annot=True, fmt='.1f', cmap='RdYlGn', 
                       center=0, ax=ax3, cbar_kws={'label': '수익률 (%)'})
        ax3.set_title('적립식투자 - 월별 수익률 히트맵 (%)')
        
        # 4. 롤링 샤프 비율 비교
        ax4 = axes[1, 1]
        ls_rolling_sharpe = self._calculate_rolling_sharpe(lump_sum_result.returns)
        dca_rolling_sharpe = self._calculate_rolling_sharpe(dca_result.returns)
        
        ax4.plot(ls_rolling_sharpe.index, ls_rolling_sharpe.values,
                label='일시투자', linewidth=2, color='#2E86AB')
        ax4.plot(dca_rolling_sharpe.index, dca_rolling_sharpe.values,
                label='적립식투자', linewidth=2, color='#F24236')
        ax4.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
        ax4.set_title('롤링 샤프 비율 (252일)')
        ax4.set_ylabel('샤프 비율')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        self._format_date_axis(ax4)
        
        plt.tight_layout()
        
        # 저장
        if save_path is None:
            save_path = f"results/charts/{index_name}_수익률분석_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
        
        return save_path
    
    def plot_drawdown_analysis(self, lump_sum_result: BacktestResult, 
                             dca_result: BacktestResult, 
                             index_name: str,
                             save_path: Optional[str] = None) -> str:
        """
        드로다운 분석 차트
        
        Args:
            lump_sum_result: 일시투자 결과
            dca_result: 적립식투자 결과
            index_name: 지수명
            save_path: 저장 경로
            
        Returns:
            저장된 파일 경로
        """
        fig, axes = plt.subplots(2, 1, figsize=self.figsize)
        fig.suptitle(f'{index_name} 드로다운 분석', fontsize=16, fontweight='bold')
        
        # 드로다운 계산
        ls_drawdown = self._calculate_drawdown(lump_sum_result.portfolio_value, 
                                             lump_sum_result.total_invested)
        dca_drawdown = self._calculate_drawdown(dca_result.portfolio_value, 
                                              dca_result.total_invested)
        
        # 1. 포트폴리오 가치와 최고점
        ax1 = axes[0]
        
        # 포트폴리오 가치
        ax1.plot(lump_sum_result.portfolio_value.index, 
                lump_sum_result.portfolio_value.values,
                label='일시투자 포트폴리오', linewidth=2, color='#2E86AB')
        ax1.plot(dca_result.portfolio_value.index, 
                dca_result.portfolio_value.values,
                label='적립식투자 포트폴리오', linewidth=2, color='#F24236')
        
        # 최고점 표시
        ls_cummax = lump_sum_result.portfolio_value.expanding().max()
        dca_cummax = dca_result.portfolio_value.expanding().max()
        
        ax1.plot(ls_cummax.index, ls_cummax.values, 
                '--', alpha=0.7, color='#2E86AB', label='일시투자 최고점')
        ax1.plot(dca_cummax.index, dca_cummax.values, 
                '--', alpha=0.7, color='#F24236', label='적립식투자 최고점')
        
        ax1.set_title('포트폴리오 가치와 역사적 최고점')
        ax1.set_ylabel('포트폴리오 가치 ($)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        self._format_date_axis(ax1)
        
        # 2. 드로다운 (%)
        ax2 = axes[1]
        ax2.fill_between(ls_drawdown.index, ls_drawdown.values, 0, 
                        alpha=0.7, color='#2E86AB', label='일시투자 드로다운')
        ax2.fill_between(dca_drawdown.index, dca_drawdown.values, 0, 
                        alpha=0.7, color='#F24236', label='적립식투자 드로다운')
        
        ax2.set_title('시간별 드로다운')
        ax2.set_ylabel('드로다운 (%)')
        ax2.set_xlabel('날짜')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        self._format_date_axis(ax2)
        
        # 최대 드로다운 지점 표시
        ls_max_dd_date = ls_drawdown.idxmin()
        dca_max_dd_date = dca_drawdown.idxmin()
        
        ax2.axvline(x=ls_max_dd_date, color='#2E86AB', linestyle=':', alpha=0.8)
        ax2.axvline(x=dca_max_dd_date, color='#F24236', linestyle=':', alpha=0.8)
        
        plt.tight_layout()
        
        # 저장
        if save_path is None:
            save_path = f"results/charts/{index_name}_드로다운분석_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
        
        return save_path
    
    def plot_metrics_comparison(self, comparison_data: dict, 
                              index_name: str,
                              save_path: Optional[str] = None) -> str:
        """
        성과 지표 비교 차트
        
        Args:
            comparison_data: 비교 분석 데이터
            index_name: 지수명
            save_path: 저장 경로
            
        Returns:
            저장된 파일 경로
        """
        fig, axes = plt.subplots(2, 2, figsize=self.figsize)
        fig.suptitle(f'{index_name} 성과 지표 비교', fontsize=16, fontweight='bold')
        
        ls_data = comparison_data['lump_sum']
        dca_data = comparison_data['dca']
        
        # 1. 기본 성과 지표
        ax1 = axes[0, 0]
        metrics = ['총 수익률 (%)', '연평균 수익률 (%)', '변동성 (%)', '샤프 비율']
        ls_values = [
            ls_data['basic']['total_return_pct'],
            ls_data['time_based']['annualized_return'],
            ls_data['risk']['volatility'],
            ls_data['risk']['sharpe_ratio']
        ]
        dca_values = [
            dca_data['basic']['total_return_pct'],
            dca_data['time_based']['annualized_return'],
            dca_data['risk']['volatility'],
            dca_data['risk']['sharpe_ratio']
        ]
        
        x = np.arange(len(metrics))
        width = 0.35
        
        ax1.bar(x - width/2, ls_values, width, label='일시투자', color='#2E86AB', alpha=0.8)
        ax1.bar(x + width/2, dca_values, width, label='적립식투자', color='#F24236', alpha=0.8)
        
        ax1.set_title('주요 성과 지표')
        ax1.set_xticks(x)
        ax1.set_xticklabels(metrics, rotation=45, ha='right')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. 위험 지표
        ax2 = axes[0, 1]
        risk_metrics = ['최대 손실 (%)', 'VaR 5% (%)', '변동성 (%)']
        ls_risk_values = [
            ls_data['drawdown']['max_drawdown'],
            ls_data['risk']['var_5'],
            ls_data['risk']['volatility']
        ]
        dca_risk_values = [
            dca_data['drawdown']['max_drawdown'],
            dca_data['risk']['var_5'],
            dca_data['risk']['volatility']
        ]
        
        x = np.arange(len(risk_metrics))
        ax2.bar(x - width/2, ls_risk_values, width, label='일시투자', color='#2E86AB', alpha=0.8)
        ax2.bar(x + width/2, dca_risk_values, width, label='적립식투자', color='#F24236', alpha=0.8)
        
        ax2.set_title('위험 지표')
        ax2.set_xticks(x)
        ax2.set_xticklabels(risk_metrics, rotation=45, ha='right')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 3. 승률 비교
        ax3 = axes[1, 0]
        win_rates = ['월별 승률 (%)', '연별 승률 (%)']
        ls_win_values = [
            ls_data['time_based']['monthly_return']['win_rate'],
            ls_data['time_based']['yearly_return']['win_rate']
        ]
        dca_win_values = [
            dca_data['time_based']['monthly_return']['win_rate'],
            dca_data['time_based']['yearly_return']['win_rate']
        ]
        
        x = np.arange(len(win_rates))
        ax3.bar(x - width/2, ls_win_values, width, label='일시투자', color='#2E86AB', alpha=0.8)
        ax3.bar(x + width/2, dca_win_values, width, label='적립식투자', color='#F24236', alpha=0.8)
        
        ax3.set_title('승률')
        ax3.set_xticks(x)
        ax3.set_xticklabels(win_rates)
        ax3.set_ylim(0, 100)
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. 투자 효율성
        ax4 = axes[1, 1]
        efficiency_metrics = ['총 투자금', '최종 가치', '총 수익']
        ls_eff_values = [
            ls_data['basic']['total_invested'],
            ls_data['basic']['final_value'],
            ls_data['basic']['total_profit']
        ]
        dca_eff_values = [
            dca_data['basic']['total_invested'],
            dca_data['basic']['final_value'],
            dca_data['basic']['total_profit']
        ]
        
        x = np.arange(len(efficiency_metrics))
        ax4.bar(x - width/2, ls_eff_values, width, label='일시투자', color='#2E86AB', alpha=0.8)
        ax4.bar(x + width/2, dca_eff_values, width, label='적립식투자', color='#F24236', alpha=0.8)
        
        ax4.set_title('투자 효율성 ($)')
        ax4.set_xticks(x)
        ax4.set_xticklabels(efficiency_metrics)
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # 저장
        if save_path is None:
            save_path = f"results/charts/{index_name}_성과지표비교_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
        
        return save_path
    
    def _format_date_axis(self, ax):
        """날짜 축 포맷팅"""
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax.xaxis.set_major_locator(mdates.YearLocator())
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
    
    def _calculate_monthly_returns_matrix(self, returns: pd.Series) -> pd.DataFrame:
        """월별 수익률 매트릭스 계산"""
        monthly_returns = returns.resample('M').apply(lambda x: (1 + x).prod() - 1) * 100
        
        if len(monthly_returns) == 0:
            return pd.DataFrame()
        
        # 년도별, 월별 매트릭스 생성
        matrix_data = []
        for date, ret in monthly_returns.items():
            matrix_data.append({
                'Year': date.year,
                'Month': date.month,
                'Return': ret
            })
        
        if not matrix_data:
            return pd.DataFrame()
        
        df = pd.DataFrame(matrix_data)
        pivot_table = df.pivot(index='Year', columns='Month', values='Return')
        
        # 월 이름으로 컬럼명 변경
        month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        pivot_table.columns = [month_names[i-1] for i in pivot_table.columns]
        
        return pivot_table.fillna(0)
    
    def _calculate_rolling_sharpe(self, returns: pd.Series, window: int = 252) -> pd.Series:
        """롤링 샤프 비율 계산"""
        rolling_mean = returns.rolling(window).mean() * 252
        rolling_std = returns.rolling(window).std() * np.sqrt(252)
        risk_free_rate = 0.02
        
        rolling_sharpe = (rolling_mean - risk_free_rate) / rolling_std
        return rolling_sharpe.dropna()
    
    def _calculate_drawdown(self, portfolio_value: pd.Series, total_invested: pd.Series) -> pd.Series:
        """드로다운 계산"""
        if len(total_invested.unique()) > 1:  # 적립식투자
            cumulative_returns = portfolio_value / total_invested
        else:  # 일시투자
            cumulative_returns = portfolio_value / portfolio_value.iloc[0]
        
        rolling_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - rolling_max) / rolling_max * 100
        
        return drawdown