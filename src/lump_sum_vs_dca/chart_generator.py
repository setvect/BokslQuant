"""
일시투자 vs 적립투자 차트 생성 모듈
"""
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import pandas as pd
import os
from typing import Dict, Any
from datetime import datetime
import seaborn as sns

# 스타일 설정
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")


class ChartGenerator:
    """일시투자 vs 적립투자 차트 생성기"""
    
    def __init__(self, config):
        self.config = config
        self.chart_dir = os.path.join(config.charts_dir)
        self._setup_korean_fonts()
        self._create_chart_directory()
    
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
    
    def _create_chart_directory(self):
        """차트 디렉토리 생성"""
        if not os.path.exists(self.chart_dir):
            os.makedirs(self.chart_dir)
    
    def generate_all_charts(self, comparison_result: Dict[str, Any]) -> Dict[str, str]:
        """모든 차트 생성"""
        chart_files = {}
        
        print("📊 차트 생성 중...")
        
        # 1. 누적 수익률 비교 차트
        print("  [1/4] 누적 수익률 비교 차트...")
        chart_files['cumulative_returns'] = self.create_cumulative_returns_chart(comparison_result)
        
        # 2. 포트폴리오 가치 변화 차트
        print("  [2/4] 포트폴리오 가치 변화 차트...")
        chart_files['portfolio_value'] = self.create_portfolio_value_chart(comparison_result)
        
        # 3. MDD 비교 차트
        print("  [3/4] MDD 비교 차트...")
        chart_files['mdd_comparison'] = self.create_mdd_comparison_chart(comparison_result)
        
        # 4. 투자 타이밍 효과 차트
        print("  [4/4] 투자 타이밍 효과 차트...")
        chart_files['timing_effect'] = self.create_timing_effect_chart(comparison_result)
        
        print("📊 모든 차트 생성 완료!")
        return chart_files
    
    def create_cumulative_returns_chart(self, comparison_result: Dict[str, Any]) -> str:
        """누적 수익률 비교 차트"""
        fig, ax = plt.subplots(figsize=(15, 9))
        
        # 데이터 준비
        lump_sum_data = comparison_result['lump_sum']['daily_returns']
        dca_data = comparison_result['dca']['daily_returns']
        
        # 날짜 변환
        lump_sum_data['date'] = pd.to_datetime(lump_sum_data['date'])
        dca_data['date'] = pd.to_datetime(dca_data['date'])
        
        # 누적 수익률 계산 (%)
        lump_sum_data['cumulative_return_pct'] = lump_sum_data['total_return'] * 100
        dca_data['cumulative_return_pct'] = dca_data['total_return'] * 100
        
        # 차트 그리기
        ax.plot(lump_sum_data['date'], lump_sum_data['cumulative_return_pct'], 
                label='일시투자', linewidth=2.5, color='#1f77b4')
        ax.plot(dca_data['date'], dca_data['cumulative_return_pct'], 
                label='적립투자', linewidth=2.5, color='#ff7f0e')
        
        # 0% 기준선
        ax.axhline(y=0, color='gray', linestyle='--', alpha=0.7, linewidth=1)
        
        # 차트 설정
        ax.set_title(f'{self.config.symbol} 누적 수익률 비교\n({self.config.start_year}년 {self.config.start_month}월 ~ {self.config.investment_period_years}년간)', 
                    fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('날짜', fontsize=12)
        ax.set_ylabel('누적 수익률 (%)', fontsize=12)
        ax.legend(fontsize=12, loc='best', frameon=True, fancybox=True, shadow=True)
        ax.grid(True, alpha=0.3)
        
        # Y축 포맷 (% 표시)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:.1f}%'))
        
        # 최종 수익률 표시
        final_lump_sum = lump_sum_data['cumulative_return_pct'].iloc[-1]
        final_dca = dca_data['cumulative_return_pct'].iloc[-1]
        
        # 텍스트 박스 (왼쪽 하단에 배치)
        textstr = f'최종 수익률\n일시투자: {final_lump_sum:.2f}%\n적립투자: {final_dca:.2f}%\n차이: {final_lump_sum - final_dca:.2f}%p'
        props = dict(boxstyle='round', facecolor='lightgray', alpha=0.8)
        ax.text(0.02, 0.35, textstr, transform=ax.transAxes, fontsize=10,
                verticalalignment='top', bbox=props)
        
        plt.tight_layout()
        
        # 파일 저장
        filename = f'누적수익률비교_{self.config.symbol}_{self.config.start_year}{self.config.start_month:02d}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
        filepath = os.path.join(self.chart_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        return filepath
    
    def create_portfolio_value_chart(self, comparison_result: Dict[str, Any]) -> str:
        """포트폴리오 가치 변화 차트"""
        fig, ax = plt.subplots(figsize=(15, 9))
        
        # 데이터 준비
        lump_sum_data = comparison_result['lump_sum']['daily_returns']
        dca_data = comparison_result['dca']['daily_returns']
        
        # 날짜 변환
        lump_sum_data['date'] = pd.to_datetime(lump_sum_data['date'])
        dca_data['date'] = pd.to_datetime(dca_data['date'])
        
        # 차트 그리기
        ax.plot(lump_sum_data['date'], lump_sum_data['current_value'], 
                label='일시투자 포트폴리오', linewidth=2.5, color='#1f77b4')
        ax.plot(dca_data['date'], dca_data['current_value'], 
                label='적립투자 포트폴리오', linewidth=2.5, color='#ff7f0e')
        
        # 투자원금 라인 (적립투자는 계단식 증가)
        ax.plot(lump_sum_data['date'], lump_sum_data['invested_amount'], 
                label='일시투자 원금', linewidth=2, linestyle='--', color='#1f77b4', alpha=0.7)
        ax.plot(dca_data['date'], dca_data['invested_amount'], 
                label='적립투자 원금', linewidth=2, linestyle='--', color='#ff7f0e', alpha=0.7)
        
        # 차트 설정
        ax.set_title(f'{self.config.symbol} 포트폴리오 가치 변화\n({self.config.start_year}년 {self.config.start_month}월 ~ {self.config.investment_period_years}년간)', 
                    fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('날짜', fontsize=12)
        ax.set_ylabel('포트폴리오 가치', fontsize=12)
        ax.legend(fontsize=10, loc='upper left', frameon=True, fancybox=True, shadow=True, 
                 bbox_to_anchor=(0.02, 0.98))
        ax.grid(True, alpha=0.3)
        
        # Y축 포맷 (천만 단위)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x/1e7:.1f}천만'))
        
        # 최종 가치 표시
        final_lump_sum_value = lump_sum_data['current_value'].iloc[-1]
        final_dca_value = dca_data['current_value'].iloc[-1]
        
        # 텍스트 박스 (왼쪽 하단에 배치)
        textstr = f'최종 포트폴리오 가치\n일시투자: {final_lump_sum_value:,.0f}\n적립투자: {final_dca_value:,.0f}\n차이: {final_lump_sum_value - final_dca_value:,.0f}'
        props = dict(boxstyle='round', facecolor='lightgray', alpha=0.8)
        ax.text(0.02, 0.35, textstr, transform=ax.transAxes, fontsize=10,
                verticalalignment='top', bbox=props)
        
        plt.tight_layout()
        
        # 파일 저장
        filename = f'포트폴리오가치_{self.config.symbol}_{self.config.start_year}{self.config.start_month:02d}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
        filepath = os.path.join(self.chart_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        return filepath
    
    def create_mdd_comparison_chart(self, comparison_result: Dict[str, Any]) -> str:
        """MDD 비교 차트"""
        fig, ax = plt.subplots(figsize=(15, 9))
        
        # 데이터 준비
        lump_sum_data = comparison_result['lump_sum']['daily_returns']
        dca_data = comparison_result['dca']['daily_returns']
        
        # 날짜 변환
        lump_sum_data['date'] = pd.to_datetime(lump_sum_data['date'])
        dca_data['date'] = pd.to_datetime(dca_data['date'])
        
        # Drawdown을 백분율로 변환
        lump_sum_data['drawdown_pct'] = lump_sum_data['drawdown'] * 100
        dca_data['drawdown_pct'] = dca_data['drawdown'] * 100
        
        # Drawdown 시계열 차트
        ax.plot(lump_sum_data['date'], lump_sum_data['drawdown_pct'], 
                linewidth=2.5, color='#1f77b4', label='일시투자')
        ax.plot(dca_data['date'], dca_data['drawdown_pct'], 
                linewidth=2.5, color='#ff7f0e', label='적립투자')
        
        # 차트 설정
        ax.set_title(f'{self.config.symbol} 손실폭(Drawdown) 비교\n({self.config.start_year}년 {self.config.start_month}월 ~ {self.config.investment_period_years}년간)', 
                    fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('날짜', fontsize=12)
        ax.set_ylabel('손실폭 (%)', fontsize=12)
        ax.legend(fontsize=11, frameon=True, fancybox=True, shadow=True, loc='best')
        ax.grid(True, alpha=0.3)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:.1f}%'))
        
        # MDD 정보 텍스트 박스
        lump_sum_mdd = lump_sum_data['drawdown_pct'].min()
        dca_mdd = dca_data['drawdown_pct'].min()
        
        info_text = f'최대 손실폭(MDD)\n일시투자: {lump_sum_mdd:.2f}%\n적립투자: {dca_mdd:.2f}%'
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
        ax.text(0.02, 0.25, info_text, transform=ax.transAxes, fontsize=11,
                verticalalignment='top', bbox=props)
        
        plt.tight_layout()
        
        # 파일 저장
        filename = f'MDD비교_{self.config.symbol}_{self.config.start_year}{self.config.start_month:02d}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
        filepath = os.path.join(self.chart_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        return filepath
    
    def create_timing_effect_chart(self, comparison_result: Dict[str, Any]) -> str:
        """투자 타이밍 효과 차트"""
        fig, ax = plt.subplots(figsize=(15, 9))
        
        # 적립투자 거래 데이터 분석
        dca_trades = comparison_result['dca']['trades']
        dca_daily_returns = comparison_result['dca']['daily_returns']
        
        # 각 거래의 최종 기여도 계산
        trade_contributions = []
        final_price = dca_daily_returns['price'].iloc[-1]
        
        for trade in dca_trades:
            trade_date = pd.to_datetime(trade['date'])
            shares_bought = trade['shares']
            price_paid = trade['price']
            
            # 해당 투자의 최종 수익률
            final_return = (final_price - price_paid) / price_paid * 100
            # 해당 투자가 최종 포트폴리오에 기여한 금액
            contribution = shares_bought * (final_price - price_paid)
            
            trade_contributions.append({
                'date': trade_date,
                'month_year': trade_date.strftime('%Y-%m'),
                'price_paid': price_paid,
                'final_return': final_return,
                'contribution': contribution,
                'investment_amount': trade['amount']
            })
        
        # 데이터프레임 생성
        df = pd.DataFrame(trade_contributions)
        
        # 월별로 그룹화
        df['year_month'] = df['date'].dt.to_period('M')
        
        # 차트 그리기 - 이중 Y축
        ax2 = ax.twinx()
        
        # 막대 차트: 각 월의 투자 기여도
        bars = ax.bar(range(len(df)), df['contribution'], 
                     color=['green' if x > 0 else 'red' for x in df['contribution']], 
                     alpha=0.7, label='투자 기여도')
        
        # 라인 차트: 해당 월의 매수 가격
        ax2.plot(range(len(df)), df['price_paid'], 
                color='blue', marker='o', linewidth=2, markersize=4, 
                label='매수 가격')
        
        # X축 라벨 설정
        ax.set_xticks(range(0, len(df), max(1, len(df)//12)))  # 최대 12개 라벨
        ax.set_xticklabels([df.iloc[i]['month_year'] for i in range(0, len(df), max(1, len(df)//12))], 
                          rotation=45)
        
        # 차트 설정
        ax.set_title(f'{self.config.symbol} 적립투자 타이밍 효과 분석\n(각 월별 투자의 최종 기여도)', 
                    fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('투자 시기', fontsize=12)
        ax.set_ylabel('투자 기여도', fontsize=12)
        ax2.set_ylabel('매수 가격', fontsize=12)
        
        # Y축 포맷 (3자리 단위 구분)
        def format_value(x, _):
            if abs(x) >= 1e8:  # 억 이상
                return f'{x/1e8:.0f}억'
            elif abs(x) >= 1e4:  # 만 이상
                return f'{x/1e4:.0f}만'
            elif abs(x) >= 1e3:  # 천 이상
                return f'{x/1e3:.0f}천'
            else:  # 천 미만
                return f'{x:.0f}'
        
        ax.yaxis.set_major_formatter(plt.FuncFormatter(format_value))
        
        # 범례
        lines1, labels1 = ax.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax.legend(lines1 + lines2, labels1 + labels2, loc='upper right', fontsize=10, 
                 frameon=True, fancybox=True, shadow=True, bbox_to_anchor=(0.98, 0.98))
        
        ax.grid(True, alpha=0.3)
        
        # 통계 정보 텍스트
        positive_months = sum(1 for x in df['contribution'] if x > 0)
        total_months = len(df)
        avg_contribution = df['contribution'].mean()
        
        textstr = f'투자 성과 요약\n성공적인 타이밍: {positive_months}/{total_months}회\n평균 기여도: {avg_contribution:,.0f}'
        props = dict(boxstyle='round', facecolor='lightgray', alpha=0.8)
        ax.text(0.02, 0.35, textstr, transform=ax.transAxes, fontsize=10,
                verticalalignment='top', bbox=props)
        
        plt.tight_layout()
        
        # 파일 저장
        filename = f'투자타이밍효과_{self.config.symbol}_{self.config.start_year}{self.config.start_month:02d}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
        filepath = os.path.join(self.chart_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        return filepath