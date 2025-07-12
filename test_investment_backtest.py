"""
일시투자 vs 적립식투자 백테스팅 테스트 실행 코드
"""
import sys
import os
sys.path.append('.')

from src.strategies.investment_types import InvestmentConfig
from src.backtesting.engine import InvestmentBacktester
from src.analysis.metrics import PerformanceAnalyzer, ComparisonAnalyzer
from src.visualization.charts import InvestmentVisualizer


def main():
    """메인 실행 함수"""
    print("🚀 일시투자 vs 적립식투자 백테스팅 시작")
    print("=" * 60)
    
    # 백테스터 초기화
    backtester = InvestmentBacktester()
    
    # 사용 가능한 지수 출력
    available_indices = backtester.get_available_indices()
    print(f"📊 사용 가능한 지수: {', '.join(available_indices)}")
    
    if not available_indices:
        print("❌ 사용 가능한 데이터가 없습니다. data/ 폴더에 CSV 파일을 확인해주세요.")
        return
    
    # 투자 설정
    config = InvestmentConfig(
        initial_capital=100000,    # 일시투자 10만달러
        monthly_amount=1000,       # 월 적립 1천달러
        start_date="2020-01-01",   # 투자 시작일
        end_date="2023-12-31",     # 투자 종료일
        commission_rate=0.001,     # 수수료 0.1%
        frequency="monthly"        # 월단위 적립
    )
    
    print(f"\n⚙️ 투자 설정:")
    print(f"   일시투자 금액: ${config.initial_capital:,}")
    print(f"   월 적립금액: ${config.monthly_amount:,}")
    print(f"   투자 기간: {config.start_date} ~ {config.end_date}")
    print(f"   수수료율: {config.commission_rate * 100}%")
    print(f"   적립 주기: {config.frequency}")
    
    # 분석할 지수 선택 (나스닥 고정)
    index_name = "NASDAQ"
    if index_name not in available_indices:
        print(f"❌ {index_name} 데이터를 찾을 수 없습니다.")
        print(f"사용 가능한 지수: {', '.join(available_indices)}")
        return
    print(f"\n📈 분석 대상: {index_name} (나스닥)")
    
    try:
        # 백테스팅 실행
        lump_sum_result, dca_result = backtester.run_comparison(index_name, config)
        
        # 기본 결과 출력
        backtester.print_comparison_summary(lump_sum_result, dca_result, index_name)
        
        # 상세 분석
        print(f"\n🔍 상세 분석 중...")
        comparison_data = ComparisonAnalyzer.compare_strategies(lump_sum_result, dca_result)
        
        # 상세 리포트 생성
        detailed_report = ComparisonAnalyzer.generate_summary_report(comparison_data)
        print(f"\n{detailed_report}")
        
        # 시각화 생성
        print(f"\n📊 차트 생성 중...")
        visualizer = InvestmentVisualizer()
        
        # 포트폴리오 비교 차트
        chart1_path = visualizer.plot_portfolio_comparison(
            lump_sum_result, dca_result, index_name
        )
        print(f"✅ 포트폴리오 비교 차트 저장: {chart1_path}")
        
        # 수익률 분석 차트
        chart2_path = visualizer.plot_returns_analysis(
            lump_sum_result, dca_result, index_name
        )
        print(f"✅ 수익률 분석 차트 저장: {chart2_path}")
        
        # 드로다운 분석 차트
        chart3_path = visualizer.plot_drawdown_analysis(
            lump_sum_result, dca_result, index_name
        )
        print(f"✅ 드로다운 분석 차트 저장: {chart3_path}")
        
        # 성과 지표 비교 차트
        chart4_path = visualizer.plot_metrics_comparison(
            comparison_data, index_name
        )
        print(f"✅ 성과 지표 비교 차트 저장: {chart4_path}")
        
        # 결과 데이터 내보내기
        csv_path = backtester.export_results(
            lump_sum_result, dca_result, index_name
        )
        
        print(f"\n🎉 분석 완료!")
        print(f"📁 생성된 파일들:")
        print(f"   - 포트폴리오 비교: {chart1_path}")
        print(f"   - 수익률 분석: {chart2_path}")
        print(f"   - 드로다운 분석: {chart3_path}")
        print(f"   - 성과 지표 비교: {chart4_path}")
        print(f"   - 결과 데이터: {csv_path}")
        
    except Exception as e:
        print(f"❌ 오류가 발생했습니다: {str(e)}")
        import traceback
        traceback.print_exc()


def test_multiple_indices():
    """여러 지수에 대한 테스트"""
    print("\n🔄 여러 지수 비교 분석")
    print("=" * 60)
    
    backtester = InvestmentBacktester()
    available_indices = backtester.get_available_indices()
    
    if len(available_indices) < 2:
        print("❌ 비교할 지수가 부족합니다.")
        return
    
    # 투자 설정
    config = InvestmentConfig(
        initial_capital=100000,
        monthly_amount=1000,
        start_date="2020-01-01",
        end_date="2023-12-31",
        commission_rate=0.001,
        frequency="monthly"
    )
    
    results_summary = []
    
    # 상위 3개 지수만 분석 (시간 단축)
    for index_name in available_indices[:3]:
        try:
            print(f"\n📈 {index_name} 분석 중...")
            lump_sum_result, dca_result = backtester.run_comparison(index_name, config)
            
            # 요약 데이터 수집
            ls_metrics = lump_sum_result.metrics
            dca_metrics = dca_result.metrics
            
            results_summary.append({
                'Index': index_name,
                'LS_Return': ls_metrics['total_return'],
                'DCA_Return': dca_metrics['total_return'],
                'LS_Sharpe': ls_metrics['sharpe_ratio'],
                'DCA_Sharpe': dca_metrics['sharpe_ratio'],
                'LS_MDD': ls_metrics['max_drawdown'],
                'DCA_MDD': dca_metrics['max_drawdown']
            })
            
        except Exception as e:
            print(f"❌ {index_name} 분석 실패: {str(e)}")
    
    # 결과 요약 출력
    if results_summary:
        print(f"\n📊 지수별 성과 요약:")
        print("-" * 80)
        print(f"{'Index':<10} {'LS Return':<10} {'DCA Return':<11} {'LS Sharpe':<10} {'DCA Sharpe':<11} {'LS MDD':<8} {'DCA MDD':<8}")
        print("-" * 80)
        
        for result in results_summary:
            print(f"{result['Index']:<10} "
                  f"{result['LS_Return']:>9.2f}% "
                  f"{result['DCA_Return']:>10.2f}% "
                  f"{result['LS_Sharpe']:>9.3f} "
                  f"{result['DCA_Sharpe']:>10.3f} "
                  f"{result['LS_MDD']:>7.2f}% "
                  f"{result['DCA_MDD']:>7.2f}%")


if __name__ == "__main__":
    # 나스닥 전용 테스트 실행
    print("🎯 나스닥 전용 백테스팅 시작")
    main()
    print(f"\n✅ 나스닥 분석 완료!")