"""
롤링 백테스트 인사이트 차트 생성 모듈
"""
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
import seaborn as sns
import os
from typing import List, Dict, Any
from datetime import datetime
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# 스타일 설정
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")


class RollingChartGenerator:
    """롤링 백테스트 인사이트 차트 생성기"""
    
    def __init__(self, symbol: str, start_year: int, end_year: int, 
                 investment_period_years: int, dca_months: int, chart_dir=None):
        self.symbol = symbol
        self.start_year = start_year
        self.end_year = end_year
        self.investment_period_years = investment_period_years
        self.dca_months = dca_months
        self._setup_korean_fonts()
        
        # 차트 저장 디렉토리 설정 (외부에서 지정 가능)
        if chart_dir:
            self.chart_dir = Path(chart_dir)
        else:
            # 기본 경로 (하위호환성)
            current_dir = Path(__file__).parent
            project_root = current_dir.parent.parent
            self.chart_dir = project_root / "results" / "lump_sum_vs_dca" / "charts"
        
        self.chart_dir.mkdir(parents=True, exist_ok=True)
    
    def _setup_korean_fonts(self):
        """한글 폰트 설정"""
        # 폰트 캐시 클리어 및 시스템 폰트 재로드
        fm._get_fontconfig_fonts.cache_clear()
        fm.fontManager.__init__()
        
        # 한글 폰트 찾기 및 설정
        korean_fonts = [f.name for f in fm.fontManager.ttflist if 'CJK' in f.name or 'Nanum' in f.name]
        if korean_fonts:
            font_name = korean_fonts[0]
            plt.rcParams['font.family'] = font_name
            plt.rcParams['font.sans-serif'] = [font_name] + plt.rcParams['font.sans-serif']
            plt.rcParams['font.monospace'] = [font_name] + plt.rcParams['font.monospace']
            plt.rcParams['font.serif'] = [font_name] + plt.rcParams['font.serif']
        else:
            # 대체 폰트 설정
            font_path = '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
            if os.path.exists(font_path):
                prop = fm.FontProperties(fname=font_path)
                font_name = prop.get_name()
                plt.rcParams['font.family'] = font_name
                plt.rcParams['font.sans-serif'] = [font_name] + plt.rcParams['font.sans-serif']
        
        plt.rcParams['axes.unicode_minus'] = False
        
        # 차트 품질 설정
        plt.rcParams['figure.dpi'] = 300
        plt.rcParams['savefig.dpi'] = 300
        plt.rcParams['savefig.bbox'] = 'tight'
    
    def generate_all_charts(self, results: List[Dict[str, Any]]) -> Dict[str, str]:
        """핵심 인사이트 차트 3개 생성 (선별)"""
        chart_files = {}
        
        print("📊 핵심 인사이트 차트 생성 중...")
        
        # 데이터프레임 변환
        df = pd.DataFrame(results)
        df['date'] = pd.to_datetime(df['period'])
        df['win'] = (df['return_difference'] > 0).astype(int)
        
        # 🎯 가장 인사이트가 있는 핵심 차트 3개 생성
        print("  [1/3] 수익률 시계열 비교 (투자 시점별 수익률 추이)...")
        chart_files['return_timeline'] = self.create_return_timeline_chart(df)
        
        print("  [2/3] 성과 차이 히트맵 (시기별 패턴 분석)...")
        chart_files['performance_heatmap'] = self.create_performance_heatmap_chart(df)
        
        print("  [3/3] 통계 요약 대시보드 (종합 분석)...")
        chart_files['summary_dashboard'] = self.create_summary_dashboard_chart(df)
        
        print("📊 핵심 인사이트 차트 생성 완료!")
        return chart_files
    
    def create_return_timeline_chart(self, df: pd.DataFrame) -> str:
        """수익률 시계열 비교 차트"""
        fig, ax = plt.subplots(figsize=(15, 9))
        
        # 시간순 정렬
        df_sorted = df.sort_values('date')
        
        # 수익률을 퍼센트로 변환
        lump_sum_returns = df_sorted['lump_sum_return'] * 100
        dca_returns = df_sorted['dca_return'] * 100
        
        # 라인 차트 그리기
        ax.plot(df_sorted['date'], lump_sum_returns, 
               linewidth=3, color='#1f77b4', marker='o', markersize=4,
               label=f'일시투자 (평균: {lump_sum_returns.mean():.1f}%)', alpha=0.8)
        ax.plot(df_sorted['date'], dca_returns, 
               linewidth=3, color='#ff7f0e', marker='s', markersize=4,
               label=f'적립투자 (평균: {dca_returns.mean():.1f}%)', alpha=0.8)
        
        # 0% 기준선
        ax.axhline(y=0, color='gray', linestyle='--', alpha=0.7, linewidth=2, label='손익분기점 (0%)')
        
        # 우위 영역 표시
        ax.fill_between(df_sorted['date'], lump_sum_returns, dca_returns,
                       where=(lump_sum_returns > dca_returns),
                       color='blue', alpha=0.1, interpolate=True, label='일시투자 우위 구간')
        ax.fill_between(df_sorted['date'], lump_sum_returns, dca_returns,
                       where=(lump_sum_returns <= dca_returns),
                       color='orange', alpha=0.1, interpolate=True, label='적립투자 우위 구간')
        
        # 차트 설정
        ax.set_title(f'{self.symbol} 투자 시점별 최종 수익률 비교\n({self.start_year}~{self.end_year}, {self.investment_period_years}년 투자)', 
                    fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('투자 시작 시점', fontsize=12)
        ax.set_ylabel('최종 수익률 (%)', fontsize=12)
        ax.legend(fontsize=11, frameon=True, fancybox=True, shadow=True, loc='best')
        ax.grid(True, alpha=0.3)
        
        # X축 날짜 포맷
        import matplotlib.dates as mdates
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax.xaxis.set_major_locator(mdates.YearLocator(2))  # 2년 간격
        plt.xticks(rotation=45)
        
        # Y축 포맷 (% 표시)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:.0f}%'))
        
        # 승률 정보 텍스트 박스
        win_rate = (df['return_difference'] > 0).mean()
        avg_diff = df['return_difference'].mean() * 100
        
        stats_text = f'전략 비교 요약\n일시투자 승률: {win_rate:.1%}\n평균 수익률 차이: {avg_diff:.1f}%p\n(일시투자 - 적립투자)'
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, fontsize=10,
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))
        
        plt.tight_layout()
        
        filename = f'롤링_수익률시계열_{self.symbol}_{self.start_year}_{self.end_year}.png'
        filepath = self.chart_dir / filename
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        return str(filepath)
    
    def create_win_rate_trend_chart(self, df: pd.DataFrame) -> str:
        """1. 승률 트렌드 차트"""
        fig, ax = plt.subplots(figsize=(15, 9))
        
        # 연도별 승률 계산
        df['year'] = df['date'].dt.year
        yearly_stats = df.groupby('year').agg({
            'win': ['mean', 'count'],
            'return_difference': 'mean'
        }).round(4)
        
        years = yearly_stats.index
        win_rates = yearly_stats[('win', 'mean')] * 100
        sample_counts = yearly_stats[('win', 'count')]
        
        # 승률 트렌드 라인
        ax.plot(years, win_rates, marker='o', linewidth=3, markersize=8, 
                color='#2E86AB', label='일시투자 승률')
        
        # 50% 기준선
        ax.axhline(y=50, color='red', linestyle='--', alpha=0.7, linewidth=2, label='균형점 (50%)')
        
        # 데이터 포인트에 값 표시
        for year, win_rate, count in zip(years, win_rates, sample_counts):
            ax.annotate(f'{win_rate:.1f}%\n(n={count})', 
                       (year, win_rate), textcoords="offset points", 
                       xytext=(0,10), ha='center', fontsize=9)
        
        ax.set_title(f'{self.symbol} 연도별 일시투자 승률 트렌드\n({self.start_year}~{self.end_year}, {self.investment_period_years}년 투자)', 
                    fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('투자 시작 연도', fontsize=12)
        ax.set_ylabel('일시투자 승률 (%)', fontsize=12)
        ax.legend(fontsize=11, frameon=True, fancybox=True, shadow=True)
        ax.grid(True, alpha=0.3)
        ax.set_ylim(0, 100)
        
        plt.tight_layout()
        
        filename = f'롤링_승률트렌드_{self.symbol}_{self.start_year}_{self.end_year}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
        filepath = self.chart_dir / filename
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        return str(filepath)
    
    def create_return_distribution_chart(self, df: pd.DataFrame) -> str:
        """2. 수익률 분포 히스토그램"""
        fig, ax = plt.subplots(figsize=(15, 9))
        
        # 수익률을 퍼센트로 변환
        lump_sum_returns = df['lump_sum_return'] * 100
        dca_returns = df['dca_return'] * 100
        
        # 히스토그램 생성
        ax.hist(lump_sum_returns, bins=30, alpha=0.7, color='#1f77b4', 
                label=f'일시투자 (평균: {lump_sum_returns.mean():.1f}%)', density=True)
        ax.hist(dca_returns, bins=30, alpha=0.7, color='#ff7f0e', 
                label=f'적립투자 (평균: {dca_returns.mean():.1f}%)', density=True)
        
        # 평균선 표시
        ax.axvline(lump_sum_returns.mean(), color='#1f77b4', linestyle='--', linewidth=2, alpha=0.8)
        ax.axvline(dca_returns.mean(), color='#ff7f0e', linestyle='--', linewidth=2, alpha=0.8)
        
        ax.set_title(f'{self.symbol} 투자전략별 수익률 분포 비교\n({len(df)}개 롤링 윈도우 분석)', 
                    fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('최종 수익률 (%)', fontsize=12)
        ax.set_ylabel('확률 밀도', fontsize=12)
        ax.legend(fontsize=11, frameon=True, fancybox=True, shadow=True)
        ax.grid(True, alpha=0.3)
        
        # 통계 정보 텍스트
        stats_text = f'통계 요약\n일시투자: 평균 {lump_sum_returns.mean():.1f}%, 표준편차 {lump_sum_returns.std():.1f}%\n적립투자: 평균 {dca_returns.mean():.1f}%, 표준편차 {dca_returns.std():.1f}%'
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, fontsize=10,
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))
        
        plt.tight_layout()
        
        filename = f'롤링_수익률분포_{self.symbol}_{self.start_year}_{self.end_year}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
        filepath = self.chart_dir / filename
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        return str(filepath)
    
    def create_risk_return_scatter_chart(self, df: pd.DataFrame) -> str:
        """3. 위험-수익 산점도"""
        fig, ax = plt.subplots(figsize=(15, 9))
        
        # 데이터 준비 (퍼센트 변환)
        lump_sum_vol = df['lump_sum_volatility'] * 100
        lump_sum_cagr = df['lump_sum_cagr'] * 100
        lump_sum_sharpe = df['lump_sum_sharpe']
        
        dca_vol = df['dca_volatility'] * 100
        dca_cagr = df['dca_cagr'] * 100
        dca_sharpe = df['dca_sharpe']
        
        # 산점도 그리기 (샤프지수에 따른 점 크기)
        scatter1 = ax.scatter(lump_sum_vol, lump_sum_cagr, 
                             s=lump_sum_sharpe*50+50, alpha=0.6, color='#1f77b4', 
                             label='일시투자', edgecolors='navy', linewidth=0.5)
        scatter2 = ax.scatter(dca_vol, dca_cagr, 
                             s=dca_sharpe*50+50, alpha=0.6, color='#ff7f0e', 
                             label='적립투자', edgecolors='darkorange', linewidth=0.5)
        
        # 효율적 프론티어 근사선 (상위 25% 포인트들)
        combined_data = pd.DataFrame({
            'vol': np.concatenate([lump_sum_vol, dca_vol]),
            'cagr': np.concatenate([lump_sum_cagr, dca_cagr]),
            'sharpe': np.concatenate([lump_sum_sharpe, dca_sharpe])
        })
        
        # 변동성 구간별 최고 CAGR 포인트들로 효율적 프론티어 그리기
        vol_bins = np.linspace(combined_data['vol'].min(), combined_data['vol'].max(), 10)
        frontier_vol = []
        frontier_cagr = []
        
        for i in range(len(vol_bins)-1):
            mask = (combined_data['vol'] >= vol_bins[i]) & (combined_data['vol'] < vol_bins[i+1])
            if mask.sum() > 0:
                max_cagr_idx = combined_data.loc[mask, 'cagr'].idxmax()
                frontier_vol.append(combined_data.loc[max_cagr_idx, 'vol'])
                frontier_cagr.append(combined_data.loc[max_cagr_idx, 'cagr'])
        
        if len(frontier_vol) > 2:
            ax.plot(frontier_vol, frontier_cagr, '--', color='gray', alpha=0.8, linewidth=2, label='효율적 프론티어')
        
        ax.set_title(f'{self.symbol} 위험-수익 분석 (샤프지수 반영)\n점 크기 = 샤프지수 × 50 + 50', 
                    fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('변동성 (%)', fontsize=12)
        ax.set_ylabel('CAGR (%)', fontsize=12)
        ax.legend(fontsize=11, frameon=True, fancybox=True, shadow=True)
        ax.grid(True, alpha=0.3)
        
        # 범례 설명 추가
        legend_text = '샤프지수 범례\n작은 점: 낮은 샤프지수\n큰 점: 높은 샤프지수'
        ax.text(0.98, 0.02, legend_text, transform=ax.transAxes, fontsize=9,
                verticalalignment='bottom', horizontalalignment='right',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        
        plt.tight_layout()
        
        filename = f'롤링_위험수익분석_{self.symbol}_{self.start_year}_{self.end_year}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
        filepath = self.chart_dir / filename
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        return str(filepath)
    
    def create_performance_heatmap_chart(self, df: pd.DataFrame) -> str:
        """4. 성과 차이 히트맵"""
        fig, ax = plt.subplots(figsize=(15, 9))
        
        # 연도-월별 데이터 준비
        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.month
        df['return_diff_pct'] = df['return_difference'] * 100
        
        # 피벗 테이블 생성
        heatmap_data = df.pivot_table(values='return_diff_pct', 
                                     index='year', columns='month', 
                                     aggfunc='mean')
        
        # 히트맵 그리기
        sns.heatmap(heatmap_data, annot=True, fmt='.1f', cmap='RdYlBu_r', 
                   center=0, ax=ax, cbar_kws={'label': '수익률 차이 (%)'})
        
        ax.set_title(f'{self.symbol} 투자시점별 성과차이 히트맵\n(일시투자 - 적립투자, %)', 
                    fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('투자 시작 월', fontsize=12)
        ax.set_ylabel('투자 시작 연도', fontsize=12)
        
        # 월 라벨 설정
        ax.set_xticklabels(['1월', '2월', '3월', '4월', '5월', '6월', 
                           '7월', '8월', '9월', '10월', '11월', '12월'])
        
        plt.tight_layout()
        
        filename = f'롤링_성과히트맵_{self.symbol}_{self.start_year}_{self.end_year}.png'
        filepath = self.chart_dir / filename
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        return str(filepath)
    
    def create_mdd_win_rate_chart(self, df: pd.DataFrame) -> str:
        """5. MDD 구간별 승률 분석"""
        fig, ax = plt.subplots(figsize=(15, 9))
        
        # MDD 구간 정의 (더 정밀한 구간)
        df['lump_sum_mdd_pct'] = df['lump_sum_mdd'] * 100
        df['dca_mdd_pct'] = df['dca_mdd'] * 100
        
        # 평균 MDD로 구간 나누기
        df['avg_mdd'] = (df['lump_sum_mdd_pct'] + df['dca_mdd_pct']) / 2
        
        # MDD 구간별 승률 계산
        mdd_bins = [0, 10, 20, 30, 40, 50, 100]
        mdd_labels = ['0-10%', '10-20%', '20-30%', '30-40%', '40-50%', '50%+']
        
        df['mdd_range'] = pd.cut(df['avg_mdd'], bins=mdd_bins, labels=mdd_labels, include_lowest=True)
        
        mdd_stats = df.groupby('mdd_range').agg({
            'win': ['mean', 'count'],
            'return_difference': 'mean',
            'lump_sum_mdd_pct': 'mean',
            'dca_mdd_pct': 'mean'
        }).round(4)
        
        # 구간별 승률 막대 그래프
        win_rates = mdd_stats[('win', 'mean')] * 100
        sample_counts = mdd_stats[('win', 'count')]
        
        # 막대 그래프 생성
        bars = ax.bar(range(len(win_rates)), win_rates, 
                     alpha=0.7, edgecolor='black', linewidth=1)
        
        # 막대별로 색상 설정 (50% 이상은 녹색, 미만은 빨간색)
        for bar, win_rate in zip(bars, win_rates):
            if win_rate > 50:
                bar.set_facecolor('green')
            else:
                bar.set_facecolor('red')
        
        # 50% 기준선
        ax.axhline(y=50, color='blue', linestyle='--', linewidth=2, alpha=0.8, label='균형점 (50%)')
        
        # 막대 위에 값 표시
        for i, (win_rate, count) in enumerate(zip(win_rates, sample_counts)):
            ax.text(i, win_rate + 2, f'{win_rate:.1f}%\n(n={count})', 
                   ha='center', va='bottom', fontweight='bold')
        
        ax.set_title(f'{self.symbol} MDD 구간별 일시투자 승률\n(시장 변동성에 따른 전략 효과성)', 
                    fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('평균 MDD 구간', fontsize=12)
        ax.set_ylabel('일시투자 승률 (%)', fontsize=12)
        ax.set_xticks(range(len(mdd_labels)))
        ax.set_xticklabels(mdd_labels)
        ax.legend(fontsize=11, frameon=True, fancybox=True, shadow=True)
        ax.grid(True, alpha=0.3, axis='y')
        ax.set_ylim(0, 100)
        
        plt.tight_layout()
        
        filename = f'롤링_MDD승률분석_{self.symbol}_{self.start_year}_{self.end_year}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
        filepath = self.chart_dir / filename
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        return str(filepath)
    
    def create_cumulative_performance_chart(self, df: pd.DataFrame) -> str:
        """6. 시간 순서별 누적 성과"""
        fig, ax = plt.subplots(figsize=(15, 9))
        
        # 시간순 정렬
        df_sorted = df.sort_values('date').reset_index(drop=True)
        
        # 누적 평균 계산
        df_sorted['cumulative_lump_sum'] = df_sorted['lump_sum_return'].expanding().mean() * 100
        df_sorted['cumulative_dca'] = df_sorted['dca_return'].expanding().mean() * 100
        df_sorted['cumulative_win_rate'] = df_sorted['win'].expanding().mean() * 100
        
        # 이중 Y축 설정
        ax2 = ax.twinx()
        
        # 누적 평균 수익률
        line1 = ax.plot(df_sorted.index, df_sorted['cumulative_lump_sum'], 
                       color='#1f77b4', linewidth=3, label='일시투자 누적평균수익률')
        line2 = ax.plot(df_sorted.index, df_sorted['cumulative_dca'], 
                       color='#ff7f0e', linewidth=3, label='적립투자 누적평균수익률')
        
        # 누적 승률 (오른쪽 축)
        line3 = ax2.plot(df_sorted.index, df_sorted['cumulative_win_rate'], 
                        color='green', linewidth=2, linestyle='--', label='일시투자 누적승률')
        
        # 50% 승률 기준선
        ax2.axhline(y=50, color='red', linestyle=':', alpha=0.7, linewidth=1)
        
        ax.set_title(f'{self.symbol} 시간순서별 누적 성과 안정성\n({self.start_year}~{self.end_year} 롤링 윈도우)', 
                    fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('롤링 윈도우 순서 (시간순)', fontsize=12)
        ax.set_ylabel('누적 평균 수익률 (%)', fontsize=12)
        ax2.set_ylabel('누적 승률 (%)', fontsize=12)
        
        # 범례 통합
        lines = line1 + line2 + line3
        labels = [l.get_label() for l in lines]
        ax.legend(lines, labels, loc='upper left', fontsize=10, frameon=True, fancybox=True, shadow=True)
        
        ax.grid(True, alpha=0.3)
        ax2.set_ylim(0, 100)
        
        plt.tight_layout()
        
        filename = f'롤링_누적성과_{self.symbol}_{self.start_year}_{self.end_year}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
        filepath = self.chart_dir / filename
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        return str(filepath)
    
    def create_sharpe_comparison_chart(self, df: pd.DataFrame) -> str:
        """7. 샤프지수 비교"""
        fig, ax = plt.subplots(figsize=(15, 9))
        
        # 샤프지수 차이 계산
        df['sharpe_difference'] = df['lump_sum_sharpe'] - df['dca_sharpe']
        
        # 시간순 정렬
        df_sorted = df.sort_values('date')
        
        # 샤프지수 시계열
        ax.plot(df_sorted['date'], df_sorted['lump_sum_sharpe'], 
               linewidth=2, color='#1f77b4', label='일시투자 샤프지수', alpha=0.8)
        ax.plot(df_sorted['date'], df_sorted['dca_sharpe'], 
               linewidth=2, color='#ff7f0e', label='적립투자 샤프지수', alpha=0.8)
        
        # 차이 영역 표시
        ax.fill_between(df_sorted['date'], df_sorted['lump_sum_sharpe'], df_sorted['dca_sharpe'],
                       where=(df_sorted['lump_sum_sharpe'] > df_sorted['dca_sharpe']),
                       color='blue', alpha=0.2, interpolate=True, label='일시투자 우위')
        ax.fill_between(df_sorted['date'], df_sorted['lump_sum_sharpe'], df_sorted['dca_sharpe'],
                       where=(df_sorted['lump_sum_sharpe'] <= df_sorted['dca_sharpe']),
                       color='orange', alpha=0.2, interpolate=True, label='적립투자 우위')
        
        ax.set_title(f'{self.symbol} 샤프지수 시계열 비교\n(위험조정수익률 분석)', 
                    fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('투자 시작 시점', fontsize=12)
        ax.set_ylabel('샤프지수', fontsize=12)
        ax.legend(fontsize=11, frameon=True, fancybox=True, shadow=True)
        ax.grid(True, alpha=0.3)
        
        # X축 날짜 포맷
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax.xaxis.set_major_locator(mdates.YearLocator())
        plt.xticks(rotation=45)
        
        # 통계 정보
        lump_avg_sharpe = df['lump_sum_sharpe'].mean()
        dca_avg_sharpe = df['dca_sharpe'].mean()
        sharpe_win_rate = (df['sharpe_difference'] > 0).mean() * 100
        
        stats_text = f'평균 샤프지수\n일시투자: {lump_avg_sharpe:.3f}\n적립투자: {dca_avg_sharpe:.3f}\n일시투자 우위: {sharpe_win_rate:.1f}%'
        ax.text(0.98, 0.98, stats_text, transform=ax.transAxes, fontsize=10,
                verticalalignment='top', horizontalalignment='right',
                bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))
        
        plt.tight_layout()
        
        filename = f'롤링_샤프지수비교_{self.symbol}_{self.start_year}_{self.end_year}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
        filepath = self.chart_dir / filename
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        return str(filepath)
    
    def create_volatility_analysis_chart(self, df: pd.DataFrame) -> str:
        """8. 변동성 분석"""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 12))
        
        # 변동성 데이터 준비 (퍼센트 변환)
        df['lump_sum_vol_pct'] = df['lump_sum_volatility'] * 100
        df['dca_vol_pct'] = df['dca_volatility'] * 100
        df['vol_difference'] = df['lump_sum_vol_pct'] - df['dca_vol_pct']
        
        # 상단: 변동성 시계열
        df_sorted = df.sort_values('date')
        ax1.plot(df_sorted['date'], df_sorted['lump_sum_vol_pct'], 
                linewidth=2, color='#1f77b4', label='일시투자 변동성', alpha=0.8)
        ax1.plot(df_sorted['date'], df_sorted['dca_vol_pct'], 
                linewidth=2, color='#ff7f0e', label='적립투자 변동성', alpha=0.8)
        
        ax1.set_title(f'{self.symbol} 변동성 시계열 분석', fontsize=14, fontweight='bold')
        ax1.set_ylabel('연환산 변동성 (%)', fontsize=12)
        ax1.legend(fontsize=11)
        ax1.grid(True, alpha=0.3)
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax1.xaxis.set_major_locator(mdates.YearLocator())
        
        # 하단: 변동성 차이 분포
        ax2.hist(df['vol_difference'], bins=20, alpha=0.7, color='purple', 
                edgecolor='black', linewidth=1)
        ax2.axvline(df['vol_difference'].mean(), color='red', linestyle='--', 
                   linewidth=2, label=f'평균: {df["vol_difference"].mean():.2f}%')
        ax2.axvline(0, color='black', linestyle='-', linewidth=1, alpha=0.5)
        
        ax2.set_title('변동성 차이 분포 (일시투자 - 적립투자)', fontsize=14, fontweight='bold')
        ax2.set_xlabel('변동성 차이 (%)', fontsize=12)
        ax2.set_ylabel('빈도', fontsize=12)
        ax2.legend(fontsize=11)
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        filename = f'롤링_변동성분석_{self.symbol}_{self.start_year}_{self.end_year}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
        filepath = self.chart_dir / filename
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        return str(filepath)
    
    def create_final_value_distribution_chart(self, df: pd.DataFrame) -> str:
        """9. 최종가치 분포"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8))
        
        # 최종가치를 천만원 단위로 변환
        df['lump_sum_value_10m'] = df['lump_sum_final_value'] / 1e7
        df['dca_value_10m'] = df['dca_final_value'] / 1e7
        df['value_diff_10m'] = (df['lump_sum_final_value'] - df['dca_final_value']) / 1e7
        
        # 좌측: 최종가치 분포 비교
        ax1.hist(df['lump_sum_value_10m'], bins=25, alpha=0.7, color='#1f77b4', 
                label=f'일시투자 (평균: {df["lump_sum_value_10m"].mean():.1f}천만)', density=True)
        ax1.hist(df['dca_value_10m'], bins=25, alpha=0.7, color='#ff7f0e', 
                label=f'적립투자 (평균: {df["dca_value_10m"].mean():.1f}천만)', density=True)
        
        ax1.axvline(df['lump_sum_value_10m'].mean(), color='#1f77b4', linestyle='--', linewidth=2)
        ax1.axvline(df['dca_value_10m'].mean(), color='#ff7f0e', linestyle='--', linewidth=2)
        
        ax1.set_title('최종 포트폴리오 가치 분포', fontsize=14, fontweight='bold')
        ax1.set_xlabel('최종 가치 (천만원)', fontsize=12)
        ax1.set_ylabel('확률 밀도', fontsize=12)
        ax1.legend(fontsize=11)
        ax1.grid(True, alpha=0.3)
        
        # 우측: 가치 차이 분포
        n, bins, patches = ax2.hist(df['value_diff_10m'], bins=20, alpha=0.7, 
                                   edgecolor='black', linewidth=1)
        
        # 막대별로 색상 설정 (양수는 녹색, 음수는 빨간색)
        for i, (patch, bin_center) in enumerate(zip(patches, (bins[:-1] + bins[1:]) / 2)):
            if bin_center > 0:
                patch.set_facecolor('green')
            else:
                patch.set_facecolor('red')
        ax2.axvline(df['value_diff_10m'].mean(), color='blue', linestyle='--', linewidth=2,
                   label=f'평균 차이: {df["value_diff_10m"].mean():.1f}천만')
        ax2.axvline(0, color='black', linestyle='-', linewidth=1, alpha=0.5)
        
        ax2.set_title('최종 가치 차이 분포\n(일시투자 - 적립투자)', fontsize=14, fontweight='bold')
        ax2.set_xlabel('가치 차이 (천만원)', fontsize=12)
        ax2.set_ylabel('빈도', fontsize=12)
        ax2.legend(fontsize=11)
        ax2.grid(True, alpha=0.3)
        
        # 전체 제목
        fig.suptitle(f'{self.symbol} 최종 포트폴리오 가치 분석 ({len(df)}개 시나리오)', 
                    fontsize=16, fontweight='bold')
        
        plt.tight_layout()
        
        filename = f'롤링_최종가치분포_{self.symbol}_{self.start_year}_{self.end_year}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
        filepath = self.chart_dir / filename
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        return str(filepath)
    
    def create_summary_dashboard_chart(self, df: pd.DataFrame) -> str:
        """10. 통계 요약 대시보드"""
        fig = plt.figure(figsize=(20, 12))
        
        # 2x3 그리드 레이아웃
        gs = fig.add_gridspec(3, 3, height_ratios=[1, 1, 1], width_ratios=[1, 1, 1])
        
        # 1. 기본 통계
        ax1 = fig.add_subplot(gs[0, 0])
        metrics = ['수익률', 'CAGR', 'MDD', '샤프지수', '변동성']
        lump_sum_values = [df['lump_sum_return'].mean(), df['lump_sum_cagr'].mean(), 
                          df['lump_sum_mdd'].mean(), df['lump_sum_sharpe'].mean(), 
                          df['lump_sum_volatility'].mean()]
        dca_values = [df['dca_return'].mean(), df['dca_cagr'].mean(), 
                     df['dca_mdd'].mean(), df['dca_sharpe'].mean(), 
                     df['dca_volatility'].mean()]
        
        x = np.arange(len(metrics))
        width = 0.35
        
        bars1 = ax1.bar(x - width/2, [v*100 if i < 3 or i == 4 else v for i, v in enumerate(lump_sum_values)], 
                       width, label='일시투자', color='#1f77b4', alpha=0.8)
        bars2 = ax1.bar(x + width/2, [v*100 if i < 3 or i == 4 else v for i, v in enumerate(dca_values)], 
                       width, label='적립투자', color='#ff7f0e', alpha=0.8)
        
        ax1.set_title('평균 성과 지표 비교', fontweight='bold')
        ax1.set_xticks(x)
        ax1.set_xticklabels(metrics, rotation=45)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. 승률 파이차트
        ax2 = fig.add_subplot(gs[0, 1])
        win_rate = df['win'].mean()
        sizes = [win_rate, 1-win_rate]
        colors = ['lightblue', 'lightcoral']
        labels = [f'일시투자 승\n{win_rate:.1%}', f'적립투자 승\n{1-win_rate:.1%}']
        
        ax2.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        ax2.set_title('전체 승률 분포', fontweight='bold')
        
        # 3. CAGR 분포 박스플롯
        ax3 = fig.add_subplot(gs[0, 2])
        box_data = [df['lump_sum_cagr']*100, df['dca_cagr']*100]
        ax3.boxplot(box_data, labels=['일시투자', '적립투자'])
        ax3.set_title('CAGR 분포 (박스플롯)', fontweight='bold')
        ax3.set_ylabel('CAGR (%)')
        ax3.grid(True, alpha=0.3)
        
        # 4. 연도별 승률
        ax4 = fig.add_subplot(gs[1, :])
        df['year'] = df['date'].dt.year
        yearly_win_rate = df.groupby('year')['win'].mean() * 100
        
        # 막대 그래프 생성
        bars = ax4.bar(yearly_win_rate.index, yearly_win_rate.values, 
                      alpha=0.7, edgecolor='black', linewidth=1)
        
        # 막대별로 색상 설정 (50% 이상은 녹색, 미만은 빨간색)
        for bar, win_rate in zip(bars, yearly_win_rate.values):
            if win_rate > 50:
                bar.set_facecolor('green')
            else:
                bar.set_facecolor('red')
        ax4.axhline(y=50, color='blue', linestyle='--', linewidth=2, alpha=0.8)
        ax4.set_title('연도별 일시투자 승률 추이', fontweight='bold', pad=15)
        ax4.set_xlabel('연도')
        ax4.set_ylabel('승률 (%)')
        ax4.set_ylim(0, 110)  # 상단 여백 추가 (100 -> 110)
        ax4.grid(True, alpha=0.3)
        
        # 막대 위에 값 표시
        for bar, value in zip(bars, yearly_win_rate.values):
            ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2, 
                    f'{value:.1f}%', ha='center', va='bottom', fontsize=9)
        
        # 5. 주요 통계 테이블
        ax5 = fig.add_subplot(gs[2, :])
        ax5.axis('off')
        
        # 통계 테이블 생성
        stats_data = [
            ['지표', '일시투자', '적립투자', '차이', '일시투자 우위율'],
            ['평균 수익률', f'{df["lump_sum_return"].mean():.1%}', f'{df["dca_return"].mean():.1%}', 
             f'{df["return_difference"].mean():.1%}', f'{(df["return_difference"] > 0).mean():.1%}'],
            ['평균 CAGR', f'{df["lump_sum_cagr"].mean():.1%}', f'{df["dca_cagr"].mean():.1%}', 
             f'{(df["lump_sum_cagr"] - df["dca_cagr"]).mean():.1%}', f'{(df["lump_sum_cagr"] > df["dca_cagr"]).mean():.1%}'],
            ['평균 MDD', f'{df["lump_sum_mdd"].mean():.1%}', f'{df["dca_mdd"].mean():.1%}', 
             f'{(df["lump_sum_mdd"] - df["dca_mdd"]).mean():.1%}', f'{(df["lump_sum_mdd"] < df["dca_mdd"]).mean():.1%}'],
            ['평균 샤프지수', f'{df["lump_sum_sharpe"].mean():.3f}', f'{df["dca_sharpe"].mean():.3f}', 
             f'{(df["lump_sum_sharpe"] - df["dca_sharpe"]).mean():.3f}', f'{(df["lump_sum_sharpe"] > df["dca_sharpe"]).mean():.1%}'],
            ['평균 변동성', f'{df["lump_sum_volatility"].mean():.1%}', f'{df["dca_volatility"].mean():.1%}', 
             f'{(df["lump_sum_volatility"] - df["dca_volatility"]).mean():.1%}', f'{(df["lump_sum_volatility"] < df["dca_volatility"]).mean():.1%}']
        ]
        
        table = ax5.table(cellText=stats_data[1:], colLabels=stats_data[0], 
                         cellLoc='center', loc='center', bbox=[0, 0, 1, 1])
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 2)
        
        # 헤더 스타일링
        for i in range(len(stats_data[0])):
            table[(0, i)].set_facecolor('#4CAF50')
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        # 전체 제목
        fig.suptitle(f'{self.symbol} 롤링 백테스트 종합 분석 대시보드\n'
                    f'({self.start_year}~{self.end_year}, {len(df)}개 시나리오, {self.investment_period_years}년 투자)', 
                    fontsize=18, fontweight='bold')
        
        plt.tight_layout()
        
        filename = f'롤링_종합대시보드_{self.symbol}_{self.start_year}_{self.end_year}.png'
        filepath = self.chart_dir / filename
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        return str(filepath)