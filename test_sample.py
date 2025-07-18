"""
테스트 샘플 실행
"""
import os
import sys

# 프로젝트 루트 경로 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.config import Config
from src.analyzer import PerformanceAnalyzer
from src.analysis_types.lump_sum_vs_dca.backtester import LumpSumVsDcaBacktester
from src.analysis_types.lump_sum_vs_dca.excel_exporter import ExcelExporter


def test_sample():
    """샘플 테스트"""
    # 설정 생성 (백테스팅 타입 지정)
    config = Config(backtest_type="lump_sum_vs_dca")
    config.set_analysis_params(
        symbol="NASDAQ",
        start_year=2000,
        start_month=1,
        investment_period_years=10,
        dca_months=60
    )
    
    print("=== 설정 정보 ===")
    print(f"백테스팅 타입: {config.backtest_type}")
    print(f"지수: {config.symbol}")
    print(f"투자 시작: {config.start_year}년 {config.start_month}월")
    print(f"투자 기간: {config.investment_period_years}년")
    print(f"적립 분할 월수: {config.dca_months}개월")
    print(f"총 투자금: {config.initial_capital:,}원")
    print(f"월 적립금: {config.get_dca_monthly_amount():,.0f}원")
    print(f"결과 저장 경로: {config.results_dir}")
    
    # 백테스팅 실행
    print("\n[1] 백테스팅 실행 중...")
    backtester = LumpSumVsDcaBacktester(config)
    comparison_result = backtester.run_comparison(config.symbol)
    
    print(f"[2] 성과 분석 중...")
    analyzer = PerformanceAnalyzer()
    
    # 결과 요약 출력
    print(f"\n[3] 결과 요약:")
    summary = analyzer.generate_summary(comparison_result)
    print(summary)
    
    # Excel 출력
    print(f"[4] Excel 파일 생성 중...")
    exporter = ExcelExporter(config)
    excel_file = exporter.export_analysis(comparison_result, analyzer)
    
    print(f"\n분석 완료!")
    print(f"결과 파일: {excel_file}")


if __name__ == "__main__":
    test_sample()