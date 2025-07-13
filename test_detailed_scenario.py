"""
특정 시나리오 상세 분석 테스트
1973-08-01 시작 시나리오의 월별 세부 진행 상황 분석
"""
import sys
sys.path.append('.')

from src.strategies.lump_sum_vs_dca_analysis import LumpSumVsDcaAnalyzer, ScenarioConfig
from src.backtesting.engine import InvestmentBacktester


def main():
    """1973-08-01 시나리오 상세 분석 실행"""
    print("🔍 특정 시나리오 상세 분석 테스트")
    print("=" * 60)
    
    # 분석할 시나리오
    target_scenario = "1973-08-01"
    
    print(f"📅 분석 대상: {target_scenario} 시작 시나리오")
    print(f"💰 총 투자금액: $60,000")
    print(f"📈 적립식 기간: 60개월 (5년)")
    print(f"📊 성과 측정 기간: 10년")
    print()
    
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
    
    # 2. 상세 분석기 생성
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
    
    # 3. 시나리오 분석 실행
    print(f"\\n🎯 {target_scenario} 시나리오 월별 분석 시작...")
    try:
        records = analyzer.analyze_detailed_scenario(target_scenario, nasdaq_data)
        print(f"✅ 분석 완료: {len(records)}개월 데이터")
        
        # 분석 기간 정보
        start_record = records[0]
        end_record = records[-1]
        print(f"   분석 기간: {start_record.date} ~ {end_record.date}")
        print(f"   시작가격: ${start_record.index_price:.2f}")
        print(f"   종료가격: ${end_record.index_price:.2f}")
        
    except Exception as e:
        print(f"❌ 시나리오 분석 실패: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 4. 주요 결과 출력
    print(f"\\n📈 최종 결과 요약:")
    print(f"   일시금투자 최종가치: ${end_record.lump_sum_value:,.0f}")
    print(f"   일시금투자 총수익률: {end_record.lump_sum_cumulative_return:.2f}%")
    print(f"   일시금투자 최대낙폭: {end_record.lump_sum_mdd:.2f}%")
    
    # MDD 디버깅: 최악의 월을 찾기
    worst_lump_sum_mdd = min(record.lump_sum_mdd for record in records)
    worst_dca_mdd = min(record.dca_mdd for record in records)
    print(f"   [디버그] 일시금 최악 MDD: {worst_lump_sum_mdd:.2f}%")
    print(f"   [디버그] 적립식 최악 MDD: {worst_dca_mdd:.2f}%")
    print()
    print(f"   적립식투자 최종가치: ${end_record.dca_value:,.0f}")
    print(f"   적립식투자 총수익률: {end_record.dca_cumulative_return:.2f}%") 
    print(f"   적립식투자 최대낙폭: {end_record.dca_mdd:.2f}%")
    print(f"   적립식투자 평균단가: ${end_record.dca_average_price:.2f}")
    print(f"   적립식투자 총구매수량: {end_record.dca_total_shares:.4f}")
    
    # 승자 판정
    if end_record.lump_sum_cumulative_return > end_record.dca_cumulative_return:
        winner = "일시금투자"
        difference = end_record.lump_sum_cumulative_return - end_record.dca_cumulative_return
    else:
        winner = "적립식투자"
        difference = end_record.dca_cumulative_return - end_record.lump_sum_cumulative_return
    
    print(f"\\n🏆 승자: {winner} (차이: {difference:.2f}%p)")
    
    # 5. Excel 출력
    print(f"\\n💾 상세 분석 결과 저장 중...")
    try:
        excel_path = analyzer.export_detailed_analysis_to_excel(records, target_scenario)
        print(f"✅ Excel 저장 완료: {excel_path}")
    except Exception as e:
        print(f"❌ Excel 저장 실패: {e}")
        import traceback
        traceback.print_exc()
    
    # 6. 차트 생성
    print(f"\\n📊 차트 생성 중...")
    try:
        returns_chart, mdd_chart = analyzer.create_detailed_charts(records, target_scenario, nasdaq_data)
        print(f"✅ 수익률 변화 차트: {returns_chart}")
        print(f"✅ MDD 변화 차트: {mdd_chart}")
    except Exception as e:
        print(f"❌ 차트 생성 실패: {e}")
        import traceback
        traceback.print_exc()
    
    # 7. 월별 진행 상황 샘플 출력 (처음 12개월)
    print(f"\\n📅 월별 진행 상황 (첫 12개월 샘플):")
    print("-" * 100)
    print(f"{'월':<3} {'날짜':<12} {'지수가격':<10} {'일시금가치':<12} {'일시금수익률':<12} {'적립투자액':<10} {'적립식가치':<12} {'적립수익률':<12}")
    print("-" * 100)
    
    for record in records[:12]:
        print(f"{record.month_num:<3} {record.date:<12} ${record.index_price:<9.2f} "
              f"${record.lump_sum_value:<11,.0f} {record.lump_sum_cumulative_return:<11.2f}% "
              f"${record.dca_monthly_investment:<9,.0f} ${record.dca_value:<11,.0f} {record.dca_cumulative_return:<11.2f}%")
    
    print("\\n" + "=" * 60)
    print("🎉 상세 분석 완료!")
    print(f"📁 생성된 파일들:")
    print(f"   - 상세 데이터: {excel_path}")
    print(f"   - 수익률 차트: {returns_chart}")
    print(f"   - MDD 차트: {mdd_chart}")
    print("=" * 60)


if __name__ == "__main__":
    main()