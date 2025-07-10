#!/usr/bin/env python3
"""
퀀트 투자 성과 분석 시스템
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.config import Config
from src.data_collector import DataCollector
from src.strategies import LumpSumStrategy, DollarCostAverageStrategy
from src.backtester import Backtester
from src.analyzer import PerformanceAnalyzer
from src.visualizer import Visualizer

def main():
    """메인 실행 함수"""
    
    # 설정 로드
    config = Config()
    
    print("=== 퀀트 투자 성과 분석 시스템 ===")
    print(f"분석 대상: {config.symbol}")
    print(f"분석 기간: {config.start_date} ~ {config.end_date}")
    print(f"초기 자본: ${config.initial_capital:,}")
    
    # 데이터 수집
    print("\n[1] 데이터 수집 중...")
    data_collector = DataCollector()
    data = data_collector.get_data(config.symbol, config.start_date, config.end_date)
    
    if data is None or data.empty:
        print("데이터 수집 실패")
        return
    
    print(f"데이터 수집 완료: {len(data)}개 레코드")
    
    # 백테스팅 실행
    print("\n[2] 백테스팅 실행 중...")
    backtester = Backtester(config)
    
    # 일시투자 전략
    lump_sum_strategy = LumpSumStrategy(config)
    lump_sum_result = backtester.run_strategy(data, lump_sum_strategy, "일시투자")
    
    # 적립식 투자 전략
    dca_strategy = DollarCostAverageStrategy(config)
    dca_result = backtester.run_strategy(data, dca_strategy, "적립식투자")
    
    # 성과 분석
    print("\n[3] 성과 분석 중...")
    analyzer = PerformanceAnalyzer()
    
    lump_sum_metrics = analyzer.calculate_metrics(lump_sum_result)
    dca_metrics = analyzer.calculate_metrics(dca_result)
    
    # 결과 출력
    print("\n" + "="*50)
    print("분석 결과")
    print("="*50)
    
    analyzer.print_comparison(lump_sum_metrics, dca_metrics)
    
    # 시각화
    print("\n[4] 차트 생성 중...")
    visualizer = Visualizer()
    visualizer.plot_comparison(lump_sum_result, dca_result, config.symbol)
    
    print("\n분석 완료!")

if __name__ == "__main__":
    main()