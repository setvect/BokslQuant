"""
확률 기반 분석 전용 시각화 모듈
"""
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import pandas as pd
import numpy as np
from typing import List, Dict, Optional
import os
from datetime import datetime


class ProbabilisticVisualizer:
    """확률 기반 분석 시각화 클래스"""
    
    def __init__(self, figsize: tuple = (16, 12)):
        self.figsize = figsize
        plt.style.use('default')
        sns.set_palette("husl")
        
        # 한글 폰트 설정
        import matplotlib.font_manager as fm
        
        # 폰트 캐시 클리어
        fm._get_fontconfig_fonts.cache_clear()
        
        # 시스템 폰트 재로드
        fm.fontManager.__init__()
        
        # 사용 가능한 한글 폰트 찾기
        korean_fonts = [f.name for f in fm.fontManager.ttflist if 'CJK' in f.name or 'Nanum' in f.name]
        
        if korean_fonts:
            font_name = korean_fonts[0]
            plt.rcParams['font.family'] = font_name
            # 모든 텍스트 요소에 한글 폰트 적용
            plt.rcParams['font.sans-serif'] = [font_name] + plt.rcParams['font.sans-serif']
            plt.rcParams['font.monospace'] = [font_name] + plt.rcParams['font.monospace']
            plt.rcParams['font.serif'] = [font_name] + plt.rcParams['font.serif']
            print(f"한글 폰트 설정: {font_name}")
        else:
            # 직접 폰트 파일 경로 지정
            font_path = '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
            if os.path.exists(font_path):
                prop = fm.FontProperties(fname=font_path)
                font_name = prop.get_name()
                plt.rcParams['font.family'] = font_name
                plt.rcParams['font.sans-serif'] = [font_name] + plt.rcParams['font.sans-serif']
                plt.rcParams['font.monospace'] = [font_name] + plt.rcParams['font.monospace']
                plt.rcParams['font.serif'] = [font_name] + plt.rcParams['font.serif']
                print(f"폰트 파일 직접 로드: {font_path}")
            else:
                plt.rcParams['font.family'] = 'DejaVu Sans'
                print("한글 폰트 없음, DejaVu Sans 사용")
        
        plt.rcParams['axes.unicode_minus'] = False
    
    def plot_probability_analysis(self, scenarios_data: List[Dict], 
                                stats: Dict,
                                save_path: Optional[str] = None) -> str:
        """확률 분석 종합 차트"""
        fig = plt.figure(figsize=self.figsize)
        
        # 데이터 준비
        df = pd.DataFrame(scenarios_data)
        lump_sum_returns = df['일시투자_수익률'].values
        dca_returns = df['적립식투자_수익률'].values
        return_diff = df['수익률차이'].values
        
        # 서브플롯 생성 (2x3 그리드)
        gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)
        
        # 1. 확률 분포 히스토그램
        ax1 = fig.add_subplot(gs[0, 0])
        ax1.hist(lump_sum_returns, bins=50, alpha=0.7, label='일시투자', 
                color='#2E86AB', density=True)
        ax1.hist(dca_returns, bins=50, alpha=0.7, label='적립식투자', 
                color='#F24236', density=True)
        ax1.set_title('수익률 확률 분포')
        ax1.set_xlabel('수익률 (%)')
        ax1.set_ylabel('밀도')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. 승률 파이 차트
        ax2 = fig.add_subplot(gs[0, 1])
        win_counts = [stats['기본_통계']['일시투자_승리'], stats['기본_통계']['적립식투자_승리']]
        labels = ['일시투자', '적립식투자']
        colors = ['#2E86AB', '#F24236']
        wedges, texts, autotexts = ax2.pie(win_counts, labels=labels, colors=colors, 
                                          autopct='%1.1f%%', startangle=90)
        ax2.set_title(f'승률 비교\n(총 {stats["기본_통계"]["총_시나리오수"]}개 시나리오)')
        
        # 3. 수익률 차이 분포
        ax3 = fig.add_subplot(gs[1, 0])
        ax3.hist(return_diff, bins=50, alpha=0.7, color='purple', edgecolor='black')
        ax3.axvline(x=0, color='red', linestyle='--', linewidth=2, label='동일 수익률')
        ax3.set_title('수익률 차이 분포\n(일시투자 - 적립식투자)')
        ax3.set_xlabel('수익률 차이 (%p)')
        ax3.set_ylabel('빈도')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. 산점도 (일시투자 vs 적립식투자)
        ax4 = fig.add_subplot(gs[1, 1])
        scatter = ax4.scatter(lump_sum_returns, dca_returns, 
                             alpha=0.6, c=return_diff, cmap='RdYlBu', s=30)
        ax4.plot([min(lump_sum_returns), max(lump_sum_returns)], 
                [min(lump_sum_returns), max(lump_sum_returns)], 
                'r--', alpha=0.8, label='동일 수익률선')
        ax4.set_xlabel('일시투자 수익률 (%)')
        ax4.set_ylabel('적립식투자 수익률 (%)')
        ax4.set_title('투자 전략별 수익률 비교')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        # 컬러바 추가
        cbar = plt.colorbar(scatter, ax=ax4)
        cbar.set_label('수익률 차이 (%p)')
        
        # 5. 연도별 승률 추이
        ax5 = fig.add_subplot(gs[2, :])
        df['시작연도'] = pd.to_datetime(df['시작일']).dt.year
        yearly_stats = df.groupby('시작연도').agg({
            '승자': lambda x: (x == '일시투자').mean() * 100
        }).rename(columns={'승자': '일시투자_승률'})
        
        ax5.plot(yearly_stats.index, yearly_stats['일시투자_승률'], 
                marker='o', linewidth=2, markersize=4, color='#2E86AB')
        ax5.axhline(y=50, color='red', linestyle='--', alpha=0.7, label='50% 기준선')
        ax5.set_xlabel('투자 시작 연도')
        ax5.set_ylabel('일시투자 승률 (%)')
        ax5.set_title('연도별 일시투자 승률 추이')
        ax5.legend()
        ax5.grid(True, alpha=0.3)
        ax5.set_ylim(0, 100)
        
        plt.suptitle('나스닥 확률 기반 투자 전략 분석 (1972-2015)', 
                    fontsize=16, fontweight='bold')
        
        # 저장
        if save_path is None:
            save_path = f"results/charts/확률분석_종합_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
        
        return save_path
    
    def plot_time_series_analysis(self, scenarios_data: List[Dict],
                                 save_path: Optional[str] = None) -> str:
        """시계열 분석 차트"""
        fig, axes = plt.subplots(2, 2, figsize=self.figsize)
        fig.suptitle('시계열 기반 투자 성과 분석', fontsize=16, fontweight='bold')
        
        df = pd.DataFrame(scenarios_data)
        df['시작일'] = pd.to_datetime(df['시작일'])
        df['시작연도'] = df['시작일'].dt.year
        df['시작월'] = df['시작일'].dt.month
        
        # 1. 월별 평균 수익률
        ax1 = axes[0, 0]
        monthly_stats = df.groupby('시작월').agg({
            '일시투자_수익률': 'mean',
            '적립식투자_수익률': 'mean'
        })
        
        months = monthly_stats.index
        ax1.plot(months, monthly_stats['일시투자_수익률'], 
                marker='o', label='일시투자', color='#2E86AB', linewidth=2)
        ax1.plot(months, monthly_stats['적립식투자_수익률'], 
                marker='s', label='적립식투자', color='#F24236', linewidth=2)
        ax1.set_xlabel('투자 시작 월')
        ax1.set_ylabel('평균 수익률 (%)')
        ax1.set_title('월별 평균 수익률')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.set_xticks(range(1, 13))
        
        # 2. 연도별 평균 수익률
        ax2 = axes[0, 1]
        yearly_stats = df.groupby('시작연도').agg({
            '일시투자_수익률': 'mean',
            '적립식투자_수익률': 'mean'
        })
        
        years = yearly_stats.index
        ax2.plot(years, yearly_stats['일시투자_수익률'], 
                marker='o', label='일시투자', color='#2E86AB', linewidth=2)
        ax2.plot(years, yearly_stats['적립식투자_수익률'], 
                marker='s', label='적립식투자', color='#F24236', linewidth=2)
        ax2.set_xlabel('투자 시작 연도')
        ax2.set_ylabel('평균 수익률 (%)')
        ax2.set_title('연도별 평균 수익률')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 3. 수익률 차이 시계열
        ax3 = axes[1, 0]
        ax3.plot(df['시작일'], df['수익률차이'], 
                alpha=0.7, linewidth=1, color='purple')
        ax3.axhline(y=0, color='red', linestyle='--', alpha=0.8)
        ax3.set_xlabel('투자 시작일')
        ax3.set_ylabel('수익률 차이 (%p)')
        ax3.set_title('시간별 수익률 차이 추이')
        ax3.grid(True, alpha=0.3)
        
        # x축 날짜 포맷팅
        ax3.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
        ax3.xaxis.set_major_locator(mdates.YearLocator(5))
        plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45)
        
        # 4. 연도별 승률 막대 그래프
        ax4 = axes[1, 1]
        decade_stats = df.groupby(df['시작연도'] // 10 * 10).agg({
            '승자': lambda x: (x == '일시투자').mean() * 100
        }).rename(columns={'승자': '일시투자_승률'})
        
        decades = [f"{int(d)}년대" for d in decade_stats.index]
        ax4.bar(decades, decade_stats['일시투자_승률'], 
               color='#2E86AB', alpha=0.7)
        ax4.axhline(y=50, color='red', linestyle='--', alpha=0.8)
        ax4.set_xlabel('연대')
        ax4.set_ylabel('일시투자 승률 (%)')
        ax4.set_title('연대별 일시투자 승률')
        ax4.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        
        # 저장
        if save_path is None:
            save_path = f"results/charts/시계열분석_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
        
        return save_path
    
    def plot_risk_return_analysis(self, scenarios_data: List[Dict],
                                 save_path: Optional[str] = None) -> str:
        """위험-수익률 분석 차트"""
        fig, axes = plt.subplots(2, 2, figsize=self.figsize)
        fig.suptitle('위험-수익률 분석', fontsize=16, fontweight='bold')
        
        df = pd.DataFrame(scenarios_data)
        lump_sum_returns = df['일시투자_수익률'].values
        dca_returns = df['적립식투자_수익률'].values
        
        # 1. 박스플롯 비교
        ax1 = axes[0, 0]
        data_to_plot = [lump_sum_returns, dca_returns]
        labels = ['일시투자', '적립식투자']
        colors = ['#2E86AB', '#F24236']
        
        bp = ax1.boxplot(data_to_plot, labels=labels, patch_artist=True)
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
        
        ax1.set_ylabel('수익률 (%)')
        ax1.set_title('수익률 분포 비교')
        ax1.grid(True, alpha=0.3)
        
        # 2. 누적 분포 함수 (CDF)
        ax2 = axes[0, 1]
        
        # 정렬된 데이터와 누적 확률 계산
        ls_sorted = np.sort(lump_sum_returns)
        dca_sorted = np.sort(dca_returns)
        ls_p = np.arange(1, len(ls_sorted) + 1) / len(ls_sorted)
        dca_p = np.arange(1, len(dca_sorted) + 1) / len(dca_sorted)
        
        ax2.plot(ls_sorted, ls_p * 100, label='일시투자', 
                color='#2E86AB', linewidth=2)
        ax2.plot(dca_sorted, dca_p * 100, label='적립식투자', 
                color='#F24236', linewidth=2)
        ax2.set_xlabel('수익률 (%)')
        ax2.set_ylabel('누적 확률 (%)')
        ax2.set_title('누적 분포 함수')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 3. 분위수 비교
        ax3 = axes[1, 0]
        percentiles = [5, 10, 25, 50, 75, 90, 95]
        ls_percentiles = np.percentile(lump_sum_returns, percentiles)
        dca_percentiles = np.percentile(dca_returns, percentiles)
        
        x = np.arange(len(percentiles))
        width = 0.35
        
        ax3.bar(x - width/2, ls_percentiles, width, 
               label='일시투자', color='#2E86AB', alpha=0.7)
        ax3.bar(x + width/2, dca_percentiles, width, 
               label='적립식투자', color='#F24236', alpha=0.7)
        
        ax3.set_xlabel('분위수')
        ax3.set_ylabel('수익률 (%)')
        ax3.set_title('분위수별 수익률 비교')
        ax3.set_xticks(x)
        ax3.set_xticklabels([f'{p}%' for p in percentiles])
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. 위험-수익률 산점도 (연도별 색상)
        ax4 = axes[1, 1]
        df['시작연도'] = pd.to_datetime(df['시작일']).dt.year
        
        # 연도별 평균과 표준편차 계산
        yearly_stats = df.groupby('시작연도').agg({
            '일시투자_수익률': ['mean', 'std'],
            '적립식투자_수익률': ['mean', 'std']
        })
        
        ls_mean = yearly_stats[('일시투자_수익률', 'mean')]
        ls_std = yearly_stats[('일시투자_수익률', 'std')]
        dca_mean = yearly_stats[('적립식투자_수익률', 'mean')]
        dca_std = yearly_stats[('적립식투자_수익률', 'std')]
        
        ax4.scatter(ls_std, ls_mean, alpha=0.7, s=50, 
                   color='#2E86AB', label='일시투자')
        ax4.scatter(dca_std, dca_mean, alpha=0.7, s=50, 
                   color='#F24236', label='적립식투자')
        
        ax4.set_xlabel('위험 (표준편차, %)')
        ax4.set_ylabel('수익률 (평균, %)')
        ax4.set_title('위험-수익률 관계 (연도별)')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # 저장
        if save_path is None:
            save_path = f"results/charts/위험수익률분석_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
        
        return save_path
    
    def plot_summary_report(self, stats: Dict,
                           save_path: Optional[str] = None) -> str:
        """요약 리포트 차트"""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('확률 분석 요약 리포트', fontsize=16, fontweight='bold')
        
        # 1. 기본 통계 막대 차트
        ax1 = axes[0, 0]
        categories = ['승리 횟수', '승률 (%)']
        lump_sum_values = [stats['기본_통계']['일시투자_승리'], 
                          stats['기본_통계']['일시투자_승률']]
        dca_values = [stats['기본_통계']['적립식투자_승리'], 
                     stats['기본_통계']['적립식투자_승률']]
        
        x = np.arange(len(categories))
        width = 0.35
        
        ax1.bar(x - width/2, lump_sum_values, width, 
               label='일시투자', color='#2E86AB', alpha=0.8)
        ax1.bar(x + width/2, dca_values, width, 
               label='적립식투자', color='#F24236', alpha=0.8)
        
        ax1.set_xlabel('지표')
        ax1.set_ylabel('값')
        ax1.set_title('기본 성과 비교')
        ax1.set_xticks(x)
        ax1.set_xticklabels(categories)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 값 표시
        for i, (ls_val, dca_val) in enumerate(zip(lump_sum_values, dca_values)):
            ax1.text(i - width/2, ls_val + max(lump_sum_values) * 0.01, 
                    f'{ls_val:.1f}', ha='center', va='bottom')
            ax1.text(i + width/2, dca_val + max(dca_values) * 0.01, 
                    f'{dca_val:.1f}', ha='center', va='bottom')
        
        # 2. 수익률 통계
        ax2 = axes[0, 1]
        return_categories = ['평균 수익률', '표준편차']
        ls_return_values = [stats['수익률_통계']['일시투자_평균수익률'],
                           stats['수익률_통계']['일시투자_표준편차']]
        dca_return_values = [stats['수익률_통계']['적립식투자_평균수익률'],
                            stats['수익률_통계']['적립식투자_표준편차']]
        
        x = np.arange(len(return_categories))
        ax2.bar(x - width/2, ls_return_values, width, 
               label='일시투자', color='#2E86AB', alpha=0.8)
        ax2.bar(x + width/2, dca_return_values, width, 
               label='적립식투자', color='#F24236', alpha=0.8)
        
        ax2.set_xlabel('지표')
        ax2.set_ylabel('수익률 (%)')
        ax2.set_title('수익률 통계')
        ax2.set_xticks(x)
        ax2.set_xticklabels(return_categories)
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 3. 극값 분석
        ax3 = axes[1, 0]
        extreme_categories = ['최고 수익률', '최저 수익률']
        ls_extreme_values = [stats['극값_분석']['일시투자_최고수익률'],
                            stats['극값_분석']['일시투자_최저수익률']]
        dca_extreme_values = [stats['극값_분석']['적립식투자_최고수익률'],
                             stats['극값_분석']['적립식투자_최저수익률']]
        
        x = np.arange(len(extreme_categories))
        ax3.bar(x - width/2, ls_extreme_values, width, 
               label='일시투자', color='#2E86AB', alpha=0.8)
        ax3.bar(x + width/2, dca_extreme_values, width, 
               label='적립식투자', color='#F24236', alpha=0.8)
        
        ax3.set_xlabel('지표')
        ax3.set_ylabel('수익률 (%)')
        ax3.set_title('극값 분석')
        ax3.set_xticks(x)
        ax3.set_xticklabels(extreme_categories)
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. 텍스트 요약
        ax4 = axes[1, 1]
        ax4.axis('off')
        
        summary_text = f"""
📊 분석 요약

총 시나리오 수: {stats['기본_통계']['총_시나리오수']:,}개
분석 기간: 1972년 ~ 2015년 (43년)

🏆 승률
일시투자: {stats['기본_통계']['일시투자_승률']:.1f}%
적립식투자: {stats['기본_통계']['적립식투자_승률']:.1f}%

📈 평균 수익률
일시투자: {stats['수익률_통계']['일시투자_평균수익률']:.2f}%
적립식투자: {stats['수익률_통계']['적립식투자_평균수익률']:.2f}%
평균 차이: {stats['수익률_통계']['평균_수익률차이']:.2f}%p

📊 위험 (표준편차)
일시투자: {stats['수익률_통계']['일시투자_표준편차']:.2f}%
적립식투자: {stats['수익률_통계']['적립식투자_표준편차']:.2f}%

🎯 최고 성과 시나리오
일시투자: {stats['극값_시나리오']['일시투자_최고']['수익률']:.2f}%
({stats['극값_시나리오']['일시투자_최고']['시작일']})

적립식투자: {stats['극값_시나리오']['적립식투자_최고']['수익률']:.2f}%
({stats['극값_시나리오']['적립식투자_최고']['시작일']})
        """
        
        ax4.text(0.05, 0.95, summary_text, transform=ax4.transAxes, 
                fontsize=10, verticalalignment='top',
                bbox=dict(boxstyle="round,pad=0.5", facecolor="lightgray", alpha=0.8))
        
        plt.tight_layout()
        
        # 저장
        if save_path is None:
            save_path = f"results/charts/요약리포트_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
        
        return save_path