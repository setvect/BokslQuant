#!/usr/bin/env python3
"""
일시투자 vs 적립투자 백테스팅 실행 스크립트 (테스트 코드 방식)

사용법:
1. 아래 변수들을 원하는 값으로 수정
2. python run_backtest.py 실행
"""
import sys
import os

# 백테스팅 모듈과 공통 모듈 경로 설정
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
project_src_dir = os.path.join(os.path.dirname(os.path.dirname(current_dir)), 'src')
sys.path.insert(0, src_dir)
sys.path.insert(0, project_src_dir)

# 백테스팅 설정 변수들 (여기를 수정하세요)
BACKTEST_CONFIG = {
    'symbol': 'NASDAQ',                    # 투자 지수: NASDAQ, SP500, KOSPI 등
    'start_year': 2000,                    # 투자 시작 연도
    'start_month': 1,                      # 투자 시작 월 (1-12)
    'investment_period_years': 10,         # 투자 기간 (년)
    'dca_months': 60,                      # 적립 분할 월수
}

def run_backtest():
    """백테스팅 실행"""
    try:
        # 모듈 import
        from src.config import LumpSumVsDcaConfig
        from src.lump_sum_vs_dca_backtester import LumpSumVsDcaBacktester
        from src.excel_exporter import ExcelExporter
        from analyzer import PerformanceAnalyzer
        
        # 설정 생성
        config = LumpSumVsDcaConfig()
        config.set_analysis_params(
            symbol=BACKTEST_CONFIG['symbol'],
            start_year=BACKTEST_CONFIG['start_year'],
            start_month=BACKTEST_CONFIG['start_month'],
            investment_period_years=BACKTEST_CONFIG['investment_period_years'],
            dca_months=BACKTEST_CONFIG['dca_months']
        )
        
        print("=== 일시투자 vs 적립투자 백테스팅 ===")
        print(f"지수: {config.symbol}")
        print(f"투자 시작: {config.start_year}년 {config.start_month}월")
        print(f"투자 기간: {config.investment_period_years}년")
        print(f"적립 분할: {config.dca_months}개월")
        print(f"총 투자금: {config.initial_capital:,}원")
        print(f"월 적립금: {config.get_dca_monthly_amount():,.0f}원")
        print(f"결과 저장: {config.excel_dir}")
        
        # 백테스팅 실행
        print("\n[1] 백테스팅 실행 중...")
        backtester = LumpSumVsDcaBacktester(config)
        comparison_result = backtester.run_comparison(config.symbol)
        
        print("[2] 성과 분석 중...")
        analyzer = PerformanceAnalyzer()
        
        # 결과 요약 출력
        print("\n[3] 결과 요약:")
        summary = analyzer.generate_summary(comparison_result)
        print(summary)
        
        # Excel 출력
        print("[4] Excel 파일 생성 중...")
        exporter = ExcelExporter(config)
        excel_file = exporter.export_analysis(comparison_result, analyzer)
        
        print("\n🎉 분석 완료!")
        print(f"📊 Excel 파일: {excel_file}")
        print(f"📋 백테스트 설정이 Excel 파일의 '백테스트 설정' 시트에 저장되었습니다.")
        
        return 0
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(run_backtest())