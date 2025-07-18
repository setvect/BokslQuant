"""
설정 관리 모듈
"""
import os
from datetime import datetime
from typing import Dict, Any


class Config:
    """퀀트 투자 분석 설정 클래스"""
    
    def __init__(self, backtest_type: str = "lump_sum_vs_dca"):
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        self.base_results_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'results')
        self.backtest_type = backtest_type
        self.results_dir = os.path.join(self.base_results_dir, backtest_type)
        self.initial_capital = 10_000_000  # 고정 투자금 1천만원
        
        # 기본 설정값
        self.symbol = "NASDAQ"
        self.start_year = 2000
        self.start_month = 1
        self.investment_period_years = 10
        self.dca_months = 60
        
        # 결과 디렉토리 생성 (백테스팅 타입별)
        self._create_results_directories()
    
    def _create_results_directories(self):
        """결과 디렉토리들 생성"""
        # 기본 results 디렉토리
        if not os.path.exists(self.base_results_dir):
            os.makedirs(self.base_results_dir)
        
        # 백테스팅 타입별 디렉토리
        if not os.path.exists(self.results_dir):
            os.makedirs(self.results_dir)
    
    def get_symbol_file_path(self, symbol: str) -> str:
        """지수 데이터 파일 경로 반환"""
        return os.path.join(self.data_dir, f"{symbol}_data.csv")
    
    def get_available_symbols(self) -> list:
        """사용 가능한 지수 목록 반환"""
        symbols = []
        for file in os.listdir(self.data_dir):
            if file.endswith('_data.csv'):
                symbol = file.replace('_data.csv', '')
                symbols.append(symbol)
        return sorted(symbols)
    
    def set_analysis_params(self, symbol: str, start_year: int, start_month: int, 
                           investment_period_years: int, dca_months: int):
        """분석 파라미터 설정"""
        self.symbol = symbol
        self.start_year = start_year
        self.start_month = start_month
        self.investment_period_years = investment_period_years
        self.dca_months = dca_months
    
    def get_dca_monthly_amount(self) -> float:
        """적립투자 월별 투자금액 계산"""
        return self.initial_capital / self.dca_months
    
    def get_results_filename(self) -> str:
        """결과 파일명 생성"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"lump_sum_vs_dca_{self.symbol}_{self.start_year}{self.start_month:02d}_{timestamp}.xlsx"
    
    def to_dict(self) -> Dict[str, Any]:
        """설정을 딕셔너리로 반환"""
        return {
            'backtest_type': self.backtest_type,
            'symbol': self.symbol,
            'start_year': self.start_year,
            'start_month': self.start_month,
            'investment_period_years': self.investment_period_years,
            'dca_months': self.dca_months,
            'initial_capital': self.initial_capital,
            'dca_monthly_amount': self.get_dca_monthly_amount(),
            'results_dir': self.results_dir
        }