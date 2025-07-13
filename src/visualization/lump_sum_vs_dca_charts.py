"""
일시투자 vs 적립식투자(DCA) 분석 전용 시각화 모듈
"""
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import pandas as pd
import numpy as np
from typing import List, Dict, Optional
import os
from datetime import datetime


class LumpSumVsDcaVisualizer:
    """일시투자 vs 적립식투자(DCA) 분석 시각화 클래스"""
    
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
    
    def plot_cagr_by_start_date(self, scenarios_data: List[Dict], 
                               save_path: Optional[str] = None) -> str:
        """시작일별 CAGR 막대 차트 (시나리오별 + 연도별)"""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(20, 12))
        
        # === 상단: 시나리오별 CAGR 차트 ===
        df = pd.DataFrame(scenarios_data)
        df['시작일'] = pd.to_datetime(df['시작일'])
        df = df.sort_values('시작일')
        
        # X축: 시작일, Y축: CAGR
        x_pos = np.arange(len(df))
        width = 0.35
        
        # 막대 그래프 생성
        bars1 = ax1.bar(x_pos - width/2, df['일시투자_CAGR'], width, 
                       label='일시투자 CAGR', color='#2E86AB', alpha=0.8)
        bars2 = ax1.bar(x_pos + width/2, df['적립식투자_CAGR'], width, 
                       label='적립식투자 CAGR', color='#F24236', alpha=0.8)
        
        # 축 설정
        ax1.set_xlabel('투자 시작일', fontsize=12)
        ax1.set_ylabel('연평균수익률 (CAGR) %', fontsize=12)
        ax1.set_title('투자 시작일별 연평균수익률(CAGR) - 전체 시나리오', fontsize=14, fontweight='bold', pad=15)
        
        # X축 레이블 설정 (5년 간격으로 표시)
        step = max(1, len(df) // 20)  # 대략 20개 정도의 레이블만 표시
        ax1.set_xticks(x_pos[::step])
        ax1.set_xticklabels([date.strftime('%Y-%m') for date in df['시작일'].iloc[::step]], 
                           rotation=45, ha='right')
        
        # 범례 및 그리드
        ax1.legend(fontsize=11)
        ax1.grid(True, alpha=0.3, axis='y')
        
        # Y축 범위 조정
        y_min = min(df['일시투자_CAGR'].min(), df['적립식투자_CAGR'].min()) - 5
        y_max = max(df['일시투자_CAGR'].max(), df['적립식투자_CAGR'].max()) + 5
        ax1.set_ylim(y_min, y_max)
        
        # 0% 기준선 추가
        ax1.axhline(y=0, color='red', linestyle='--', alpha=0.5, linewidth=1)
        
        # 통계 정보 텍스트 박스
        ls_avg = df['일시투자_CAGR'].mean()
        dca_avg = df['적립식투자_CAGR'].mean()
        ls_max = df['일시투자_CAGR'].max()
        dca_max = df['적립식투자_CAGR'].max()
        ls_min = df['일시투자_CAGR'].min()
        dca_min = df['적립식투자_CAGR'].min()
        
        stats_text = f"""시나리오별 통계
일시투자 CAGR: 평균 {ls_avg:.1f}% (최고 {ls_max:.1f}%, 최저 {ls_min:.1f}%)
적립식투자 CAGR: 평균 {dca_avg:.1f}% (최고 {dca_max:.1f}%, 최저 {dca_min:.1f}%)
총 시나리오: {len(df)}개"""
        
        ax1.text(0.02, 0.98, stats_text, transform=ax1.transAxes, 
                fontsize=10, verticalalignment='top',
                bbox=dict(boxstyle="round,pad=0.5", facecolor="lightgray", alpha=0.8))
        
        # === 하단: 연도별 평균 CAGR 차트 ===
        # 연도별 데이터 생성 (연도별통계 시트와 동일한 로직)
        df_copy = df.copy()
        df_copy['연도'] = pd.to_datetime(df_copy['시작일']).dt.year
        
        yearly_cagr = df_copy.groupby('연도').agg({
            '일시투자_CAGR': 'mean',
            '적립식투자_CAGR': 'mean',
            '시작일': 'count'  # 시나리오 수
        }).round(2)
        
        # 연도별 막대 그래프
        years = yearly_cagr.index
        x_pos_yearly = np.arange(len(years))
        width_yearly = 0.35
        
        bars3 = ax2.bar(x_pos_yearly - width_yearly/2, yearly_cagr['일시투자_CAGR'], width_yearly, 
                       label='일시투자 CAGR (연평균)', color='#2E86AB', alpha=0.8)
        bars4 = ax2.bar(x_pos_yearly + width_yearly/2, yearly_cagr['적립식투자_CAGR'], width_yearly, 
                       label='적립식투자 CAGR (연평균)', color='#F24236', alpha=0.8)
        
        # 축 설정
        ax2.set_xlabel('투자 시작 연도', fontsize=12)
        ax2.set_ylabel('연평균수익률 (CAGR) %', fontsize=12)
        ax2.set_title('연도별 평균 연평균수익률(CAGR)', fontsize=14, fontweight='bold', pad=15)
        
        # X축 레이블 설정 (5년 간격)
        step_yearly = max(1, len(years) // 10)
        ax2.set_xticks(x_pos_yearly[::step_yearly])
        ax2.set_xticklabels([str(year) for year in years[::step_yearly]], rotation=45)
        
        # 범례 및 그리드
        ax2.legend(fontsize=11)
        ax2.grid(True, alpha=0.3, axis='y')
        
        # Y축 범위 조정
        y_min_yearly = min(yearly_cagr['일시투자_CAGR'].min(), yearly_cagr['적립식투자_CAGR'].min()) - 2
        y_max_yearly = max(yearly_cagr['일시투자_CAGR'].max(), yearly_cagr['적립식투자_CAGR'].max()) + 2
        ax2.set_ylim(y_min_yearly, y_max_yearly)
        
        # 0% 기준선 추가
        ax2.axhline(y=0, color='red', linestyle='--', alpha=0.5, linewidth=1)
        
        # 연도별 통계 정보
        yearly_ls_avg = yearly_cagr['일시투자_CAGR'].mean()
        yearly_dca_avg = yearly_cagr['적립식투자_CAGR'].mean()
        yearly_ls_max = yearly_cagr['일시투자_CAGR'].max()
        yearly_dca_max = yearly_cagr['적립식투자_CAGR'].max()
        
        yearly_stats_text = f"""연도별 통계
일시투자 CAGR: 연평균 {yearly_ls_avg:.1f}% (최고연도 {yearly_ls_max:.1f}%)
적립식투자 CAGR: 연평균 {yearly_dca_avg:.1f}% (최고연도 {yearly_dca_max:.1f}%)
분석 연도: {len(years)}년"""
        
        ax2.text(0.02, 0.98, yearly_stats_text, transform=ax2.transAxes, 
                fontsize=10, verticalalignment='top',
                bbox=dict(boxstyle="round,pad=0.5", facecolor="lightblue", alpha=0.8))
        
        plt.tight_layout()
        
        # 저장
        if save_path is None:
            save_path = f"results/charts/시작일별_CAGR_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
        
        return save_path
    
    def plot_returns_by_start_date(self, scenarios_data: List[Dict], 
                                  save_path: Optional[str] = None) -> str:
        """시작일별 수익률 막대 차트 (시나리오별 + 연도별)"""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(20, 12))
        
        # === 상단: 시나리오별 수익률 차트 ===
        df = pd.DataFrame(scenarios_data)
        df['시작일'] = pd.to_datetime(df['시작일'])
        df = df.sort_values('시작일')
        
        # X축: 시작일, Y축: 수익률
        x_pos = np.arange(len(df))
        width = 0.35
        
        # 막대 그래프 생성
        bars1 = ax1.bar(x_pos - width/2, df['일시투자_수익률'], width, 
                       label='일시투자 수익률', color='#2E86AB', alpha=0.8)
        bars2 = ax1.bar(x_pos + width/2, df['적립식투자_수익률'], width, 
                       label='적립식투자 수익률', color='#F24236', alpha=0.8)
        
        # 축 설정
        ax1.set_xlabel('투자 시작일', fontsize=12)
        ax1.set_ylabel('총 수익률 (%)', fontsize=12)
        ax1.set_title('투자 시작일별 총 수익률 - 전체 시나리오', fontsize=14, fontweight='bold', pad=15)
        
        # X축 레이블 설정
        step = max(1, len(df) // 20)
        ax1.set_xticks(x_pos[::step])
        ax1.set_xticklabels([date.strftime('%Y-%m') for date in df['시작일'].iloc[::step]], 
                           rotation=45, ha='right')
        
        # 범례 및 그리드
        ax1.legend(fontsize=11)
        ax1.grid(True, alpha=0.3, axis='y')
        
        # Y축 범위 조정
        y_min = min(df['일시투자_수익률'].min(), df['적립식투자_수익률'].min()) - 50
        y_max = max(df['일시투자_수익률'].max(), df['적립식투자_수익률'].max()) + 50
        ax1.set_ylim(y_min, y_max)
        
        # 0% 기준선 추가
        ax1.axhline(y=0, color='red', linestyle='--', alpha=0.5, linewidth=1)
        
        # 통계 정보 텍스트 박스
        ls_avg = df['일시투자_수익률'].mean()
        dca_avg = df['적립식투자_수익률'].mean()
        ls_max = df['일시투자_수익률'].max()
        dca_max = df['적립식투자_수익률'].max()
        ls_min = df['일시투자_수익률'].min()
        dca_min = df['적립식투자_수익률'].min()
        
        stats_text = f"""시나리오별 통계
일시투자 수익률: 평균 {ls_avg:.1f}% (최고 {ls_max:.1f}%, 최저 {ls_min:.1f}%)
적립식투자 수익률: 평균 {dca_avg:.1f}% (최고 {dca_max:.1f}%, 최저 {dca_min:.1f}%)
총 시나리오: {len(df)}개"""
        
        ax1.text(0.02, 0.98, stats_text, transform=ax1.transAxes, 
                fontsize=10, verticalalignment='top',
                bbox=dict(boxstyle="round,pad=0.5", facecolor="lightgray", alpha=0.8))
        
        # === 하단: 연도별 평균 수익률 차트 ===
        df_copy = df.copy()
        df_copy['연도'] = pd.to_datetime(df_copy['시작일']).dt.year
        
        yearly_returns = df_copy.groupby('연도').agg({
            '일시투자_수익률': 'mean',
            '적립식투자_수익률': 'mean',
            '시작일': 'count'
        }).round(2)
        
        # 연도별 막대 그래프
        years = yearly_returns.index
        x_pos_yearly = np.arange(len(years))
        width_yearly = 0.35
        
        bars3 = ax2.bar(x_pos_yearly - width_yearly/2, yearly_returns['일시투자_수익률'], width_yearly, 
                       label='일시투자 수익률 (연평균)', color='#2E86AB', alpha=0.8)
        bars4 = ax2.bar(x_pos_yearly + width_yearly/2, yearly_returns['적립식투자_수익률'], width_yearly, 
                       label='적립식투자 수익률 (연평균)', color='#F24236', alpha=0.8)
        
        # 축 설정
        ax2.set_xlabel('투자 시작 연도', fontsize=12)
        ax2.set_ylabel('총 수익률 (%)', fontsize=12)
        ax2.set_title('연도별 평균 총 수익률', fontsize=14, fontweight='bold', pad=15)
        
        # X축 레이블 설정
        step_yearly = max(1, len(years) // 10)
        ax2.set_xticks(x_pos_yearly[::step_yearly])
        ax2.set_xticklabels([str(year) for year in years[::step_yearly]], rotation=45)
        
        # 범례 및 그리드
        ax2.legend(fontsize=11)
        ax2.grid(True, alpha=0.3, axis='y')
        
        # Y축 범위 조정
        y_min_yearly = min(yearly_returns['일시투자_수익률'].min(), yearly_returns['적립식투자_수익률'].min()) - 20
        y_max_yearly = max(yearly_returns['일시투자_수익률'].max(), yearly_returns['적립식투자_수익률'].max()) + 20
        ax2.set_ylim(y_min_yearly, y_max_yearly)
        
        # 0% 기준선 추가
        ax2.axhline(y=0, color='red', linestyle='--', alpha=0.5, linewidth=1)
        
        # 연도별 통계 정보
        yearly_ls_avg = yearly_returns['일시투자_수익률'].mean()
        yearly_dca_avg = yearly_returns['적립식투자_수익률'].mean()
        yearly_ls_max = yearly_returns['일시투자_수익률'].max()
        yearly_dca_max = yearly_returns['적립식투자_수익률'].max()
        
        yearly_stats_text = f"""연도별 통계
일시투자 수익률: 연평균 {yearly_ls_avg:.1f}% (최고연도 {yearly_ls_max:.1f}%)
적립식투자 수익률: 연평균 {yearly_dca_avg:.1f}% (최고연도 {yearly_dca_max:.1f}%)
분석 연도: {len(years)}년"""
        
        ax2.text(0.02, 0.98, yearly_stats_text, transform=ax2.transAxes, 
                fontsize=10, verticalalignment='top',
                bbox=dict(boxstyle="round,pad=0.5", facecolor="lightgreen", alpha=0.8))
        
        plt.tight_layout()
        
        # 저장
        if save_path is None:
            save_path = f"results/charts/시작일별_수익률_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
        
        return save_path
    
    def plot_mdd_by_start_date(self, scenarios_data: List[Dict], 
                              save_path: Optional[str] = None) -> str:
        """시작일별 MDD 막대 차트 (시나리오별 + 연도별)"""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(20, 12))
        
        # === 상단: 시나리오별 MDD 차트 ===
        df = pd.DataFrame(scenarios_data)
        df['시작일'] = pd.to_datetime(df['시작일'])
        df = df.sort_values('시작일')
        
        # X축: 시작일, Y축: MDD (음수 값이므로 절댓값으로 표시)
        x_pos = np.arange(len(df))
        width = 0.35
        
        # MDD는 음수이므로 절댓값으로 표시 (하락폭을 양수로)
        ls_mdd_abs = abs(df['일시투자_MDD'])
        dca_mdd_abs = abs(df['적립식투자_MDD'])
        
        # 막대 그래프 생성
        bars1 = ax1.bar(x_pos - width/2, ls_mdd_abs, width, 
                       label='일시투자 MDD', color='#2E86AB', alpha=0.8)
        bars2 = ax1.bar(x_pos + width/2, dca_mdd_abs, width, 
                       label='적립식투자 MDD', color='#F24236', alpha=0.8)
        
        # 축 설정
        ax1.set_xlabel('투자 시작일', fontsize=12)
        ax1.set_ylabel('최대낙폭 (MDD) %', fontsize=12)
        ax1.set_title('투자 시작일별 최대낙폭(MDD) - 전체 시나리오', fontsize=14, fontweight='bold', pad=15)
        
        # X축 레이블 설정
        step = max(1, len(df) // 20)
        ax1.set_xticks(x_pos[::step])
        ax1.set_xticklabels([date.strftime('%Y-%m') for date in df['시작일'].iloc[::step]], 
                           rotation=45, ha='right')
        
        # 범례 및 그리드
        ax1.legend(fontsize=11)
        ax1.grid(True, alpha=0.3, axis='y')
        
        # Y축 범위 조정 (0부터 시작, MDD는 하락폭이므로)
        y_max = max(ls_mdd_abs.max(), dca_mdd_abs.max()) + 5
        ax1.set_ylim(0, y_max)
        
        # 통계 정보 텍스트 박스
        ls_avg = ls_mdd_abs.mean()
        dca_avg = dca_mdd_abs.mean()
        ls_max = ls_mdd_abs.max()
        dca_max = dca_mdd_abs.max()
        ls_min = ls_mdd_abs.min()
        dca_min = dca_mdd_abs.min()
        
        stats_text = f"""시나리오별 통계
일시투자 MDD: 평균 {ls_avg:.1f}% (최대 {ls_max:.1f}%, 최소 {ls_min:.1f}%)
적립식투자 MDD: 평균 {dca_avg:.1f}% (최대 {dca_max:.1f}%, 최소 {dca_min:.1f}%)
총 시나리오: {len(df)}개"""
        
        ax1.text(0.02, 0.98, stats_text, transform=ax1.transAxes, 
                fontsize=10, verticalalignment='top',
                bbox=dict(boxstyle="round,pad=0.5", facecolor="lightgray", alpha=0.8))
        
        # === 하단: 연도별 평균 MDD 차트 ===
        df_copy = df.copy()
        df_copy['연도'] = pd.to_datetime(df_copy['시작일']).dt.year
        
        yearly_mdd = df_copy.groupby('연도').agg({
            '일시투자_MDD': lambda x: abs(x).mean(),  # 절댓값의 평균
            '적립식투자_MDD': lambda x: abs(x).mean(),
            '시작일': 'count'
        }).round(2)
        
        # 연도별 막대 그래프
        years = yearly_mdd.index
        x_pos_yearly = np.arange(len(years))
        width_yearly = 0.35
        
        bars3 = ax2.bar(x_pos_yearly - width_yearly/2, yearly_mdd['일시투자_MDD'], width_yearly, 
                       label='일시투자 MDD (연평균)', color='#2E86AB', alpha=0.8)
        bars4 = ax2.bar(x_pos_yearly + width_yearly/2, yearly_mdd['적립식투자_MDD'], width_yearly, 
                       label='적립식투자 MDD (연평균)', color='#F24236', alpha=0.8)
        
        # 축 설정
        ax2.set_xlabel('투자 시작 연도', fontsize=12)
        ax2.set_ylabel('최대낙폭 (MDD) %', fontsize=12)
        ax2.set_title('연도별 평균 최대낙폭(MDD)', fontsize=14, fontweight='bold', pad=15)
        
        # X축 레이블 설정
        step_yearly = max(1, len(years) // 10)
        ax2.set_xticks(x_pos_yearly[::step_yearly])
        ax2.set_xticklabels([str(year) for year in years[::step_yearly]], rotation=45)
        
        # 범례 및 그리드
        ax2.legend(fontsize=11)
        ax2.grid(True, alpha=0.3, axis='y')
        
        # Y축 범위 조정
        y_max_yearly = max(yearly_mdd['일시투자_MDD'].max(), yearly_mdd['적립식투자_MDD'].max()) + 2
        ax2.set_ylim(0, y_max_yearly)
        
        # 연도별 통계 정보
        yearly_ls_avg = yearly_mdd['일시투자_MDD'].mean()
        yearly_dca_avg = yearly_mdd['적립식투자_MDD'].mean()
        yearly_ls_max = yearly_mdd['일시투자_MDD'].max()
        yearly_dca_max = yearly_mdd['적립식투자_MDD'].max()
        
        yearly_stats_text = f"""연도별 통계
일시투자 MDD: 연평균 {yearly_ls_avg:.1f}% (최악연도 {yearly_ls_max:.1f}%)
적립식투자 MDD: 연평균 {yearly_dca_avg:.1f}% (최악연도 {yearly_dca_max:.1f}%)
분석 연도: {len(years)}년"""
        
        ax2.text(0.02, 0.98, yearly_stats_text, transform=ax2.transAxes, 
                fontsize=10, verticalalignment='top',
                bbox=dict(boxstyle="round,pad=0.5", facecolor="lightcoral", alpha=0.8))
        
        plt.tight_layout()
        
        # 저장
        if save_path is None:
            save_path = f"results/charts/시작일별_MDD_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
        
        return save_path
    
    def plot_sharpe_by_start_date(self, scenarios_data: List[Dict], 
                                 save_path: Optional[str] = None) -> str:
        """시작일별 샤프지수 막대 차트 (시나리오별 + 연도별)"""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(20, 12))
        
        # === 상단: 시나리오별 샤프지수 차트 ===
        df = pd.DataFrame(scenarios_data)
        df['시작일'] = pd.to_datetime(df['시작일'])
        df = df.sort_values('시작일')
        
        # X축: 시작일, Y축: 샤프지수
        x_pos = np.arange(len(df))
        width = 0.35
        
        # 막대 그래프 생성
        bars1 = ax1.bar(x_pos - width/2, df['일시투자_샤프지수'], width, 
                       label='일시투자 샤프지수', color='#2E86AB', alpha=0.8)
        bars2 = ax1.bar(x_pos + width/2, df['적립식투자_샤프지수'], width, 
                       label='적립식투자 샤프지수', color='#F24236', alpha=0.8)
        
        # 축 설정
        ax1.set_xlabel('투자 시작일', fontsize=12)
        ax1.set_ylabel('샤프지수', fontsize=12)
        ax1.set_title('투자 시작일별 샤프지수 - 전체 시나리오', fontsize=14, fontweight='bold', pad=15)
        
        # X축 레이블 설정
        step = max(1, len(df) // 20)
        ax1.set_xticks(x_pos[::step])
        ax1.set_xticklabels([date.strftime('%Y-%m') for date in df['시작일'].iloc[::step]], 
                           rotation=45, ha='right')
        
        # 범례 및 그리드
        ax1.legend(fontsize=11)
        ax1.grid(True, alpha=0.3, axis='y')
        
        # Y축 범위 조정
        y_min = min(df['일시투자_샤프지수'].min(), df['적립식투자_샤프지수'].min()) - 0.2
        y_max = max(df['일시투자_샤프지수'].max(), df['적립식투자_샤프지수'].max()) + 0.2
        ax1.set_ylim(y_min, y_max)
        
        # 0 기준선 추가
        ax1.axhline(y=0, color='red', linestyle='--', alpha=0.5, linewidth=1)
        # 1.0 기준선 추가 (우수한 샤프지수 기준)
        ax1.axhline(y=1.0, color='green', linestyle='--', alpha=0.5, linewidth=1, label='우수 기준(1.0)')
        
        # 통계 정보 텍스트 박스
        ls_avg = df['일시투자_샤프지수'].mean()
        dca_avg = df['적립식투자_샤프지수'].mean()
        ls_max = df['일시투자_샤프지수'].max()
        dca_max = df['적립식투자_샤프지수'].max()
        ls_min = df['일시투자_샤프지수'].min()
        dca_min = df['적립식투자_샤프지수'].min()
        
        stats_text = f"""시나리오별 통계
일시투자 샤프지수: 평균 {ls_avg:.2f} (최고 {ls_max:.2f}, 최저 {ls_min:.2f})
적립식투자 샤프지수: 평균 {dca_avg:.2f} (최고 {dca_max:.2f}, 최저 {dca_min:.2f})
총 시나리오: {len(df)}개"""
        
        ax1.text(0.02, 0.98, stats_text, transform=ax1.transAxes, 
                fontsize=10, verticalalignment='top',
                bbox=dict(boxstyle="round,pad=0.5", facecolor="lightgray", alpha=0.8))
        
        # === 하단: 연도별 평균 샤프지수 차트 ===
        df_copy = df.copy()
        df_copy['연도'] = pd.to_datetime(df_copy['시작일']).dt.year
        
        yearly_sharpe = df_copy.groupby('연도').agg({
            '일시투자_샤프지수': 'mean',
            '적립식투자_샤프지수': 'mean',
            '시작일': 'count'
        }).round(3)
        
        # 연도별 막대 그래프
        years = yearly_sharpe.index
        x_pos_yearly = np.arange(len(years))
        width_yearly = 0.35
        
        bars3 = ax2.bar(x_pos_yearly - width_yearly/2, yearly_sharpe['일시투자_샤프지수'], width_yearly, 
                       label='일시투자 샤프지수 (연평균)', color='#2E86AB', alpha=0.8)
        bars4 = ax2.bar(x_pos_yearly + width_yearly/2, yearly_sharpe['적립식투자_샤프지수'], width_yearly, 
                       label='적립식투자 샤프지수 (연평균)', color='#F24236', alpha=0.8)
        
        # 축 설정
        ax2.set_xlabel('투자 시작 연도', fontsize=12)
        ax2.set_ylabel('샤프지수', fontsize=12)
        ax2.set_title('연도별 평균 샤프지수', fontsize=14, fontweight='bold', pad=15)
        
        # X축 레이블 설정
        step_yearly = max(1, len(years) // 10)
        ax2.set_xticks(x_pos_yearly[::step_yearly])
        ax2.set_xticklabels([str(year) for year in years[::step_yearly]], rotation=45)
        
        # 범례 및 그리드
        ax2.legend(fontsize=11)
        ax2.grid(True, alpha=0.3, axis='y')
        
        # Y축 범위 조정
        y_min_yearly = min(yearly_sharpe['일시투자_샤프지수'].min(), yearly_sharpe['적립식투자_샤프지수'].min()) - 0.1
        y_max_yearly = max(yearly_sharpe['일시투자_샤프지수'].max(), yearly_sharpe['적립식투자_샤프지수'].max()) + 0.1
        ax2.set_ylim(y_min_yearly, y_max_yearly)
        
        # 기준선들
        ax2.axhline(y=0, color='red', linestyle='--', alpha=0.5, linewidth=1)
        ax2.axhline(y=1.0, color='green', linestyle='--', alpha=0.5, linewidth=1)
        
        # 연도별 통계 정보
        yearly_ls_avg = yearly_sharpe['일시투자_샤프지수'].mean()
        yearly_dca_avg = yearly_sharpe['적립식투자_샤프지수'].mean()
        yearly_ls_max = yearly_sharpe['일시투자_샤프지수'].max()
        yearly_dca_max = yearly_sharpe['적립식투자_샤프지수'].max()
        
        yearly_stats_text = f"""연도별 통계
일시투자 샤프지수: 연평균 {yearly_ls_avg:.2f} (최고연도 {yearly_ls_max:.2f})
적립식투자 샤프지수: 연평균 {yearly_dca_avg:.2f} (최고연도 {yearly_dca_max:.2f})
분석 연도: {len(years)}년"""
        
        ax2.text(0.02, 0.98, yearly_stats_text, transform=ax2.transAxes, 
                fontsize=10, verticalalignment='top',
                bbox=dict(boxstyle="round,pad=0.5", facecolor="lightyellow", alpha=0.8))
        
        plt.tight_layout()
        
        # 저장
        if save_path is None:
            save_path = f"results/charts/시작일별_샤프지수_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
        
        return save_path