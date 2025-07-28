"""
일시투자 vs 적립투자 백테스팅 전용 설정 모듈
"""
import os
from datetime import datetime
from typing import Dict, Any
import sys

# 공통 모듈 경로 추가
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'src'))


class LumpSumVsDcaConfig:
    """일시투자 vs 적립투자 백테스팅 전용 설정 클래스"""
    
    def __init__(self):
        # 현재 파일의 디렉토리 (/src/lump_sum_vs_dca)
        current_dir = os.path.dirname(__file__)
        
        # src 디렉토리 (/src)
        src_dir = os.path.dirname(current_dir)
        
        # 프로젝트 루트 디렉토리 (/mnt/d/intellij-project/boksl_quant)
        self.project_root = os.path.dirname(src_dir)
        
        # 백테스팅 루트 디렉토리 (현재는 src/lump_sum_vs_dca)
        self.backtest_root = current_dir
        
        # 디렉토리 경로 설정
        self.data_dir = os.path.join(self.project_root, 'data')
        self.results_base_dir = os.path.join(self.project_root, 'results', 'lump_sum_vs_dca')
        self.docs_dir = os.path.join(self.project_root, 'docs')
        
        # 고정 투자금 설정
        self.initial_capital = 10_000_000  # 1천만원
        
        # 기본 분석 파라미터
        self.symbol = "NASDAQ"
        self.start_year = 2000
        self.start_month = 1
        self.investment_period_years = 10
        self.dca_months = 60
        
        # 백테스트 타입 (detail 또는 rolling)
        self.backtest_type = "detail"  # 기본값은 개별 백테스트
        
        # 동적 디렉토리 경로 (백테스트 실행 시 설정됨)
        self.result_session_dir = None
        self.excel_dir = None  
        self.charts_dir = None
        
        # 기본 디렉토리 생성
        self._create_base_directories()
    
    def _create_base_directories(self):
        """기본 디렉토리들 생성"""
        directories = [
            self.results_base_dir,
            os.path.join(self.results_base_dir, 'detail'),
            os.path.join(self.results_base_dir, 'rolling'),
            self.docs_dir
        ]
        
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory)
    
    def set_backtest_type(self, backtest_type: str):
        """백테스트 타입 설정 (detail 또는 rolling)"""
        if backtest_type not in ['detail', 'rolling']:
            raise ValueError("backtest_type은 'detail' 또는 'rolling'이어야 합니다.")
        self.backtest_type = backtest_type
    
    def create_session_directory(self):
        """백테스트 세션별 디렉토리 생성 (중복 시 번호 추가)"""
        base_session_name = f"{self.symbol}_{self.start_year}_{self.start_month:02d}"
        session_name = self._get_unique_directory_name(base_session_name)
        
        # 세션 디렉토리 경로 설정
        self.result_session_dir = os.path.join(
            self.results_base_dir, 
            self.backtest_type, 
            session_name
        )
        
        # Excel과 차트 디렉토리는 세션 디렉토리 내부에
        self.excel_dir = self.result_session_dir
        self.charts_dir = self.result_session_dir
        
        # 디렉토리 생성
        if not os.path.exists(self.result_session_dir):
            os.makedirs(self.result_session_dir)
        
        return self.result_session_dir
    
    def get_symbol_file_path(self, symbol: str) -> str:
        """지수 데이터 파일 경로 반환"""
        return os.path.join(self.data_dir, f"{symbol}_data.csv")
    
    def get_available_symbols(self) -> list:
        """사용 가능한 지수 목록 반환"""
        symbols = []
        if os.path.exists(self.data_dir):
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
    
    def get_excel_filename(self) -> str:
        """Excel 결과 파일명 생성"""
        return f"lump_sum_vs_dca_{self.symbol}_{self.start_year}{self.start_month:02d}.xlsx"
    
    def get_excel_filepath(self) -> str:
        """Excel 결과 파일 전체 경로 반환"""
        return os.path.join(self.excel_dir, self.get_excel_filename())
    
    
    def _get_unique_directory_name(self, base_name: str) -> str:
        """중복 디렉토리명 처리 - 번호 추가"""
        base_path = os.path.join(self.results_base_dir, self.backtest_type, base_name)
        
        if not os.path.exists(base_path):
            return base_name
        
        counter = 1
        while True:
            new_name = f"{base_name}({counter})"
            new_path = os.path.join(self.results_base_dir, self.backtest_type, new_name)
            if not os.path.exists(new_path):
                return new_name
            counter += 1
    
    
    def __str__(self):
        """설정 정보를 문자열로 반환"""
        return f"""
=== 일시투자 vs 적립투자 백테스팅 설정 ===
지수: {self.symbol}
투자 시작: {self.start_year}년 {self.start_month}월
투자 기간: {self.investment_period_years}년
적립 분할: {self.dca_months}개월
총 투자금: {self.initial_capital:,}원
월 적립금: {self.get_dca_monthly_amount():,.0f}원
백테스트 타입: {self.backtest_type}

결과 저장 경로:
- 세션 디렉토리: {self.result_session_dir or '미설정'}
- Excel: {self.excel_dir or '미설정'}
- 차트: {self.charts_dir or '미설정'}
"""