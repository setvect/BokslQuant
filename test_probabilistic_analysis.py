"""
확률 기반 백테스팅 분석 테스트 실행 코드
1972년~2015년 나스닥 데이터로 일시투자 vs 적립식투자 516개 시나리오 분석
"""
import sys
import os
sys.path.append('.')

from src.strategies.probabilistic_analysis import ProbabilisticBacktester, ScenarioConfig
from src.backtesting.engine import InvestmentBacktester
from src.visualization.probabilistic_charts import ProbabilisticVisualizer
import pandas as pd


def main():
    """확률 기반 분석 메인 실행 함수"""
    print("🎲 확률 기반 투자 전략 분석 시작")
    print("=" * 70)
    
    # 1. 나스닥 데이터 로드
    print("📊 나스닥 데이터 로드 중...")
    try:
        backtester = InvestmentBacktester()
        nasdaq_data = backtester.load_data("NASDAQ")
        print(f"✅ 데이터 로드 완료: {len(nasdaq_data)}일 데이터")
        print(f"   기간: {nasdaq_data.index[0].strftime('%Y-%m-%d')} ~ {nasdaq_data.index[-1].strftime('%Y-%m-%d')}")
    except Exception as e:
        print(f"❌ 데이터 로드 실패: {e}")
        return
    
    # 2. 분석 설정
    config = ScenarioConfig(
        total_amount=60000,  # 총 6만달러
        investment_period_months=60,  # 5년간 적립
        analysis_period_years=10,  # 10년 후 성과 측정
        start_year=1972,
        start_month=1,
        end_year=2015,
        end_month=1
    )
    
    print(f"\n⚙️ 분석 설정:")
    print(f"   총 투자금액: ${config.total_amount:,}")
    print(f"   적립식 기간: {config.investment_period_months}개월 ({config.investment_period_months//12}년)")
    print(f"   성과 측정 기간: {config.analysis_period_years}년")
    print(f"   시나리오 기간: {config.start_year}년 {config.start_month}월 ~ {config.end_year}년 {config.end_month}월")
    
    # 월별 적립금액 계산
    monthly_amount = config.total_amount / config.investment_period_months
    print(f"   월 적립금액: ${monthly_amount:,.0f}")
    
    # 3. 확률 분석 실행
    print(f"\n🎯 확률 분석 시작...")
    analyzer = ProbabilisticBacktester(config)
    
    try:
        # 시나리오 개수 미리 확인
        scenarios = analyzer.generate_scenarios()
        print(f"   예상 시나리오 수: {len(scenarios)}개")
        
        # 데이터 범위 확인
        data_start = nasdaq_data.index[0]
        data_end = nasdaq_data.index[-1]
        scenario_start = scenarios[0][0]
        scenario_end = scenarios[-1][1]
        
        print(f"   데이터 범위: {data_start.strftime('%Y-%m')} ~ {data_end.strftime('%Y-%m')}")
        print(f"   분석 범위: {scenario_start.strftime('%Y-%m')} ~ {scenario_end.strftime('%Y-%m')}")
        
        if scenario_end > data_end:
            print(f"⚠️ 경고: 일부 시나리오는 데이터 부족으로 제외될 수 있습니다.")
        
        # 분석 실행
        analyzer.run_all_scenarios(nasdaq_data)
        
        if not analyzer.scenarios:
            print("❌ 분석 가능한 시나리오가 없습니다.")
            return
            
    except Exception as e:
        print(f"❌ 분석 실행 중 오류: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 4. 결과 집계 및 통계
    print(f"\n📈 결과 분석 중...")
    try:
        stats = analyzer.get_summary_statistics()
        scenarios_data = analyzer.get_scenarios_data()
        
        # 기본 통계 출력
        print_summary_statistics(stats)
        
    except Exception as e:
        print(f"❌ 통계 분석 중 오류: {e}")
        return
    
    # 5. 결과 저장
    print(f"\n💾 결과 저장 중...")
    try:
        # Excel 저장
        excel_path = analyzer.export_to_excel()
        print(f"✅ Excel 저장: {excel_path}")
        
    except Exception as e:
        print(f"❌ 결과 저장 중 오류: {e}")
    
    # 6. 시각화 생성
    print(f"\n📊 차트 생성 중...")
    try:
        visualizer = ProbabilisticVisualizer()
        
        # 시작일별 CAGR 막대 차트
        chart1_path = visualizer.plot_cagr_by_start_date(scenarios_data)
        print(f"✅ 시작일별 CAGR 차트: {chart1_path}")
        
        # 시작일별 수익률 막대 차트
        chart2_path = visualizer.plot_returns_by_start_date(scenarios_data)
        print(f"✅ 시작일별 수익률 차트: {chart2_path}")
        
        # 시작일별 MDD 막대 차트
        chart3_path = visualizer.plot_mdd_by_start_date(scenarios_data)
        print(f"✅ 시작일별 MDD 차트: {chart3_path}")
        
        # 시작일별 샤프지수 막대 차트
        chart4_path = visualizer.plot_sharpe_by_start_date(scenarios_data)
        print(f"✅ 시작일별 샤프지수 차트: {chart4_path}")
        
    except Exception as e:
        print(f"❌ 시각화 생성 중 오류: {e}")
        import traceback
        traceback.print_exc()
    
    # 7. 최종 요약
    print(f"\n" + "="*70)
    print(f"🎉 확률 기반 분석 완료!")
    print(f"📁 생성된 파일들:")
    print(f"   - 상세 데이터 (Excel): {excel_path}")
    print(f"   - 시작일별 CAGR 차트: {chart1_path}")
    print(f"   - 시작일별 수익률 차트: {chart2_path}")
    print(f"   - 시작일별 MDD 차트: {chart3_path}")
    print(f"   - 시작일별 샤프지수 차트: {chart4_path}")
    print(f"="*70)


def print_summary_statistics(stats: dict):
    """요약 통계 출력"""
    basic = stats['기본_통계']
    returns = stats['수익률_통계']
    extremes = stats['극값_분석']
    scenarios = stats['극값_시나리오']
    
    print(f"\n📊 분석 결과 요약")
    print(f"-" * 50)
    
    print(f"\n🎯 기본 통계:")
    print(f"   총 시나리오: {basic['총_시나리오수']:,}개")
    print(f"   일시투자 승리: {basic['일시투자_승리']:,}개 ({basic['일시투자_승률']:.1f}%)")
    print(f"   적립식투자 승리: {basic['적립식투자_승리']:,}개 ({basic['적립식투자_승률']:.1f}%)")
    
    print(f"\n📈 수익률 통계:")
    print(f"   일시투자 평균: {returns['일시투자_평균수익률']:.2f}% (±{returns['일시투자_표준편차']:.2f}%)")
    print(f"   적립식투자 평균: {returns['적립식투자_평균수익률']:.2f}% (±{returns['적립식투자_표준편차']:.2f}%)")
    print(f"   평균 차이: {returns['평균_수익률차이']:.2f}%p")
    
    print(f"\n🏆 극값 분석:")
    print(f"   일시투자 최고/최저: {extremes['일시투자_최고수익률']:.2f}% / {extremes['일시투자_최저수익률']:.2f}%")
    print(f"   적립식투자 최고/최저: {extremes['적립식투자_최고수익률']:.2f}% / {extremes['적립식투자_최저수익률']:.2f}%")
    print(f"   최대 수익률 차이: {extremes['최대_수익률차이']:.2f}%p")
    
    print(f"\n🎪 최고 성과 시나리오:")
    print(f"   일시투자: {scenarios['일시투자_최고']['수익률']:.2f}% ({scenarios['일시투자_최고']['시작일']})")
    print(f"   적립식투자: {scenarios['적립식투자_최고']['수익률']:.2f}% ({scenarios['적립식투자_최고']['시작일']})")
    
    # 승률 기반 결론
    if basic['일시투자_승률'] > 50:
        print(f"\n🏁 결론: 일시투자가 {basic['일시투자_승률']:.1f}%의 확률로 더 우수한 성과를 보임")
    else:
        print(f"\n🏁 결론: 적립식투자가 {basic['적립식투자_승률']:.1f}%의 확률로 더 우수한 성과를 보임")



def quick_analysis():
    """빠른 분석 (테스트용 - 일부 시나리오만)"""
    print("🔬 빠른 분석 모드 (테스트용)")
    print("=" * 50)
    
    # 데이터 로드
    backtester = InvestmentBacktester()
    nasdaq_data = backtester.load_data("NASDAQ")
    
    # 설정 (테스트용 - 더 짧은 기간)
    config = ScenarioConfig(
        total_amount=60000,
        investment_period_months=60,
        analysis_period_years=10,
        start_year=2000,  # 2000년부터만
        start_month=1,
        end_year=2005,    # 2005년까지만 (5년)
        end_month=1
    )
    
    analyzer = ProbabilisticBacktester(config)
    analyzer.run_all_scenarios(nasdaq_data)
    
    if analyzer.scenarios:
        stats = analyzer.get_summary_statistics()
        print_summary_statistics(stats)
        
        # 간단한 차트만 생성
        visualizer = ProbabilisticVisualizer()
        scenarios_data = analyzer.get_scenarios_data()
        chart_path = visualizer.plot_cagr_by_start_date(scenarios_data)
        print(f"✅ 차트 저장: {chart_path}")
    else:
        print("❌ 분석 가능한 시나리오가 없습니다.")


if __name__ == "__main__":
    import sys
    
    # 명령행 인수 확인
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        quick_analysis()
    else:
        main()