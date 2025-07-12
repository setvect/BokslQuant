"""
백테스팅 엔진 모듈
일시투자 vs 적립식투자 비교 분석을 위한 메인 엔진
"""
import pandas as pd
import numpy as np
from typing import Dict, Tuple
import os
from ..strategies.investment_types import (
    InvestmentConfig, BacktestResult, 
    LumpSumStrategy, DollarCostAveraging
)


class InvestmentBacktester:
    """투자 전략 백테스팅 엔진"""
    
    def __init__(self, data_path: str = "data/"):
        """
        백테스터 초기화
        
        Args:
            data_path: 데이터 파일 경로
        """
        self.data_path = data_path
        self.available_indices = self._scan_available_data()
    
    def _scan_available_data(self) -> Dict[str, str]:
        """사용 가능한 데이터 파일 스캔"""
        available_data = {}
        
        if not os.path.exists(self.data_path):
            return available_data
        
        # CSV 파일들을 스캔하여 지수명 추출
        for filename in os.listdir(self.data_path):
            if filename.endswith('.csv'):
                index_name = filename.replace('_data.csv', '').replace('.csv', '')
                available_data[index_name.upper()] = os.path.join(self.data_path, filename)
        
        return available_data
    
    def load_data(self, index_name: str) -> pd.DataFrame:
        """
        지정된 지수 데이터 로드
        
        Args:
            index_name: 지수명 (예: 'SP500', 'KOSPI')
        
        Returns:
            가격 데이터 DataFrame
        """
        index_name = index_name.upper()
        
        if index_name not in self.available_indices:
            raise ValueError(f"'{index_name}' 데이터를 찾을 수 없습니다. "
                           f"사용 가능한 지수: {list(self.available_indices.keys())}")
        
        file_path = self.available_indices[index_name]
        
        try:
            df = pd.read_csv(file_path)
            
            # 날짜 컬럼을 인덱스로 설정
            if 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date'], utc=True)
                df.set_index('Date', inplace=True)
            
            # 필요한 컬럼들이 있는지 확인
            required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                raise ValueError(f"필수 컬럼이 누락되었습니다: {missing_columns}")
            
            # 결측치 처리
            df = df.dropna()
            
            # 날짜순 정렬
            df = df.sort_index()
            
            return df
        
        except Exception as e:
            raise ValueError(f"데이터 로드 중 오류가 발생했습니다: {str(e)}")
    
    def run_comparison(self, index_name: str, config: InvestmentConfig) -> Tuple[BacktestResult, BacktestResult]:
        """
        일시투자 vs 적립식투자 비교 실행
        
        Args:
            index_name: 분석할 지수명
            config: 투자 설정
        
        Returns:
            (일시투자 결과, 적립식투자 결과) 튜플
        """
        print(f"📊 {index_name} 데이터를 이용한 백테스팅을 시작합니다...")
        
        # 데이터 로드
        price_data = self.load_data(index_name)
        print(f"✅ 데이터 로드 완료: {len(price_data)} 일의 데이터")
        
        # 일시투자 백테스팅
        print("💰 일시투자 백테스팅 실행 중...")
        lump_sum = LumpSumStrategy(config)
        lump_sum_result = lump_sum.backtest(price_data)
        
        # 적립식투자 백테스팅
        print("📅 적립식투자 백테스팅 실행 중...")
        dca = DollarCostAveraging(config)
        dca_result = dca.backtest(price_data)
        
        print("✅ 백테스팅 완료!")
        
        return lump_sum_result, dca_result
    
    def print_comparison_summary(self, lump_sum_result: BacktestResult, 
                               dca_result: BacktestResult, index_name: str):
        """
        비교 결과 요약 출력
        
        Args:
            lump_sum_result: 일시투자 결과
            dca_result: 적립식투자 결과
            index_name: 지수명
        """
        print(f"\n{'='*60}")
        print(f"📈 {index_name} 투자 전략 비교 결과")
        print(f"{'='*60}")
        
        # 기본 정보
        print(f"\n📋 투자 기간: {lump_sum_result.portfolio_value.index[0].strftime('%Y-%m-%d')} ~ "
              f"{lump_sum_result.portfolio_value.index[-1].strftime('%Y-%m-%d')}")
        
        # 일시투자 결과
        ls_metrics = lump_sum_result.metrics
        print(f"\n💰 일시투자 결과:")
        print(f"   초기 투자금: {ls_metrics['total_invested']:,.0f}원")
        print(f"   최종 자산: {ls_metrics['final_value']:,.0f}원")
        print(f"   총 수익률: {ls_metrics['total_return']:.2f}%")
        print(f"   연평균 수익률: {ls_metrics['annualized_return']:.2f}%")
        print(f"   변동성: {ls_metrics['volatility']:.2f}%")
        print(f"   샤프 비율: {ls_metrics['sharpe_ratio']:.3f}")
        print(f"   최대 손실: {ls_metrics['max_drawdown']:.2f}%")
        
        # 적립식투자 결과
        dca_metrics = dca_result.metrics
        print(f"\n📅 적립식투자 결과:")
        print(f"   총 투자금: {dca_metrics['total_invested']:,.0f}원")
        print(f"   최종 자산: {dca_metrics['final_value']:,.0f}원")
        print(f"   총 수익률: {dca_metrics['total_return']:.2f}%")
        print(f"   연평균 수익률: {dca_metrics['annualized_return']:.2f}%")
        print(f"   변동성: {dca_metrics['volatility']:.2f}%")
        print(f"   샤프 비율: {dca_metrics['sharpe_ratio']:.3f}")
        print(f"   최대 손실: {dca_metrics['max_drawdown']:.2f}%")
        
        # 비교 분석
        print(f"\n🔍 비교 분석:")
        
        # 수익률 비교
        return_diff = ls_metrics['total_return'] - dca_metrics['total_return']
        if return_diff > 0:
            print(f"   📈 일시투자가 {return_diff:.2f}%p 더 높은 수익률")
        else:
            print(f"   📈 적립식투자가 {abs(return_diff):.2f}%p 더 높은 수익률")
        
        # 수익금액 비교
        ls_profit = ls_metrics['final_value'] - ls_metrics['total_invested']
        dca_profit = dca_metrics['final_value'] - dca_metrics['total_invested']
        profit_diff = ls_profit - dca_profit
        
        if profit_diff > 0:
            print(f"   💵 일시투자가 {profit_diff:,.0f}원 더 많은 수익")
        else:
            print(f"   💵 적립식투자가 {abs(profit_diff):,.0f}원 더 많은 수익")
        
        # 위험 비교
        volatility_diff = ls_metrics['volatility'] - dca_metrics['volatility']
        if volatility_diff > 0:
            print(f"   📊 일시투자가 {volatility_diff:.2f}%p 더 높은 변동성")
        else:
            print(f"   📊 적립식투자가 {abs(volatility_diff):.2f}%p 더 높은 변동성")
        
        # 샤프 비율 비교
        sharpe_diff = ls_metrics['sharpe_ratio'] - dca_metrics['sharpe_ratio']
        if sharpe_diff > 0:
            print(f"   ⚖️ 일시투자가 {sharpe_diff:.3f} 더 높은 샤프 비율 (위험대비 수익률)")
        else:
            print(f"   ⚖️ 적립식투자가 {abs(sharpe_diff):.3f} 더 높은 샤프 비율 (위험대비 수익률)")
        
        print(f"\n{'='*60}")
    
    def get_available_indices(self) -> list:
        """사용 가능한 지수 목록 반환"""
        return list(self.available_indices.keys())
    
    def export_results(self, lump_sum_result: BacktestResult, 
                      dca_result: BacktestResult, 
                      index_name: str, 
                      output_path: str = "results/"):
        """
        결과를 CSV 파일로 내보내기
        
        Args:
            lump_sum_result: 일시투자 결과
            dca_result: 적립식투자 결과
            index_name: 지수명
            output_path: 출력 경로
        """
        import os
        from datetime import datetime
        
        # 결과 디렉토리 생성
        os.makedirs(output_path, exist_ok=True)
        
        # 타임스탬프 추가
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 포트폴리오 가치 비교 데이터
        comparison_df = pd.DataFrame({
            '날짜': lump_sum_result.portfolio_value.index,
            '일시투자_포트폴리오가치': lump_sum_result.portfolio_value.values,
            '일시투자_투자원금': lump_sum_result.total_invested.values,
            '적립식투자_포트폴리오가치': dca_result.portfolio_value.values,
            '적립식투자_투자원금': dca_result.total_invested.values,
            '일시투자_보유주식수': lump_sum_result.shares_held.values,
            '적립식투자_보유주식수': dca_result.shares_held.values
        })
        
        # CSV 저장
        filename = f"{index_name}_투자전략비교_{timestamp}.csv"
        filepath = os.path.join(output_path, filename)
        comparison_df.to_csv(filepath, index=False, encoding='utf-8-sig')
        
        print(f"📁 결과가 저장되었습니다: {filepath}")
        
        return filepath