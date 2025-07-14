"""
Excel 파일의 MDD 값을 확인하는 스크립트
"""
import pandas as pd
import sys
sys.path.append('.')

from src.strategies.lump_sum_vs_dca_analysis import LumpSumVsDcaAnalyzer, ScenarioConfig
from src.backtesting.engine import InvestmentBacktester

def check_mdd_values():
    """Excel 파일의 MDD 값과 차트 MDD 값 비교"""
    
    # 1. 나스닥 데이터 로드
    backtester = InvestmentBacktester()
    nasdaq_data = backtester.load_data("NASDAQ")
    
    # 2. 분석기 설정
    config = ScenarioConfig(
        total_amount=60000,
        investment_period_months=60,
        analysis_period_years=10,
        start_year=1972,
        start_month=1,
        end_year=2015,
        end_month=1
    )
    analyzer = LumpSumVsDcaAnalyzer(config)
    
    # 3. 일별 MDD 계산 (차트용)
    from datetime import datetime
    import pytz
    start_date = "1973-08-01"
    start_dt = datetime.strptime(start_date, '%Y-%m-%d').replace(tzinfo=pytz.UTC)
    end_dt = start_dt + pd.DateOffset(years=config.analysis_period_years)
    
    daily_dates, daily_lump_sum_mdds, daily_dca_mdds = analyzer.calculate_daily_mdd(
        nasdaq_data, start_dt, end_dt
    )
    
    # 4. 결과 출력
    print("📊 MDD 값 비교")
    print("=" * 50)
    print(f"차트 (일별 Low 가격 기반):")
    print(f"  일시금투자 최악 MDD: {min(daily_lump_sum_mdds):.2f}%")
    print(f"  적립식투자 최악 MDD: {min(daily_dca_mdds):.2f}%")
    print()
    
    # 5. 월별 MDD 계산 (기존 방식)
    records = analyzer.analyze_detailed_scenario(start_date, nasdaq_data)
    monthly_worst_lump_sum_mdd = min(record.lump_sum_mdd for record in records)
    monthly_worst_dca_mdd = min(record.dca_mdd for record in records)
    
    print(f"Excel 월별 (기존 방식):")
    print(f"  일시금투자 최악 MDD: {monthly_worst_lump_sum_mdd:.2f}%")
    print(f"  적립식투자 최악 MDD: {monthly_worst_dca_mdd:.2f}%")
    print()
    
    print("🔍 결과 분석:")
    print(f"일시금투자 MDD 차이: {min(daily_lump_sum_mdds) - monthly_worst_lump_sum_mdd:.2f}%p")
    print(f"적립식투자 MDD 차이: {min(daily_dca_mdds) - monthly_worst_dca_mdd:.2f}%p")
    print()
    
    # 6. 최근 Excel 파일 확인
    import os
    import glob
    
    excel_files = glob.glob("results/lump_sum_vs_dca/상세분석_19730801_*.xlsx")
    if excel_files:
        latest_file = max(excel_files, key=os.path.getctime)
        print(f"📄 최근 Excel 파일: {latest_file}")
        
        # 요약통계 시트 읽기
        try:
            summary_df = pd.read_excel(latest_file, sheet_name="요약통계", header=None)
            print(f"📋 Excel 요약통계 내용:")
            print(summary_df.to_string(index=False, header=False))
        except Exception as e:
            print(f"❌ Excel 파일 읽기 실패: {e}")

if __name__ == "__main__":
    check_mdd_values()