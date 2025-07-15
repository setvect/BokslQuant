"""
일시투자 vs 적립투자 분석 메인 모듈
"""
import os
import sys
from datetime import datetime

# 프로젝트 루트 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from src.config import Config
from src.analyzer import PerformanceAnalyzer
from src.analysis_types.lump_sum_vs_dca.backtester import LumpSumVsDcaBacktester
from src.analysis_types.lump_sum_vs_dca.excel_exporter import ExcelExporter


def get_user_input():
    """사용자 입력 받기"""
    config = Config()
    
    print("=== 일시투자 vs 적립투자 분석 프로그램 ===\n")
    
    # 사용 가능한 지수 목록 표시
    available_symbols = config.get_available_symbols()
    print("사용 가능한 지수:")
    for i, symbol in enumerate(available_symbols, 1):
        print(f"{i}. {symbol}")
    
    # 지수 선택
    while True:
        try:
            symbol_choice = int(input(f"\n지수를 선택하세요 (1-{len(available_symbols)}): "))
            if 1 <= symbol_choice <= len(available_symbols):
                symbol = available_symbols[symbol_choice - 1]
                break
            else:
                print("올바른 번호를 입력하세요.")
        except ValueError:
            print("숫자를 입력하세요.")
    
    # 투자 시작 날짜 입력
    while True:
        try:
            start_year = int(input("투자 시작 연도를 입력하세요 (예: 2000): "))
            if 1970 <= start_year <= datetime.now().year:
                break
            else:
                print("올바른 연도를 입력하세요.")
        except ValueError:
            print("숫자를 입력하세요.")
    
    while True:
        try:
            start_month = int(input("투자 시작 월을 입력하세요 (1-12): "))
            if 1 <= start_month <= 12:
                break
            else:
                print("1-12 사이의 월을 입력하세요.")
        except ValueError:
            print("숫자를 입력하세요.")
    
    # 투자 기간 입력
    while True:
        try:
            investment_period_years = int(input("투자 기간(년)을 입력하세요 (예: 10): "))
            if 1 <= investment_period_years <= 50:
                break
            else:
                print("1-50년 사이의 기간을 입력하세요.")
        except ValueError:
            print("숫자를 입력하세요.")
    
    # 적립 분할 월수 입력
    while True:
        try:
            dca_months = int(input("적립 분할 월수를 입력하세요 (예: 60): "))
            if 1 <= dca_months <= investment_period_years * 12:
                break
            else:
                print(f"1-{investment_period_years * 12}개월 사이의 기간을 입력하세요.")
        except ValueError:
            print("숫자를 입력하세요.")
    
    # 설정 적용
    config.set_analysis_params(symbol, start_year, start_month, investment_period_years, dca_months)
    
    return config


def main():
    """메인 함수"""
    try:
        # 사용자 입력 받기
        config = get_user_input()
        
        print(f"\n=== 분석 설정 ===")
        print(f"지수: {config.symbol}")
        print(f"투자 시작: {config.start_year}년 {config.start_month}월")
        print(f"투자 기간: {config.investment_period_years}년")
        print(f"적립 분할 월수: {config.dca_months}개월")
        print(f"총 투자금: {config.initial_capital:,}원")
        print(f"월 적립금: {config.get_dca_monthly_amount():,.0f}원")
        
        # 분석 실행
        print(f"\n[1] 백테스팅 실행 중...")
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
        
    except Exception as e:
        print(f"오류 발생: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())