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
        # 백테스팅 루트 디렉토리
        self.backtest_root = os.path.dirname(os.path.dirname(__file__))
        
        # 프로젝트 루트 디렉토리  
        self.project_root = os.path.dirname(os.path.dirname(os.path.dirname(self.backtest_root)))
        
        # 디렉토리 경로 설정
        self.data_dir = os.path.join(self.project_root, 'data')
        self.results_dir = os.path.join(self.backtest_root, 'results')
        self.excel_dir = os.path.join(self.results_dir, 'excel')
        self.charts_dir = os.path.join(self.results_dir, 'charts')
        self.reports_dir = os.path.join(self.results_dir, 'reports')
        self.configs_dir = os.path.join(self.backtest_root, 'configs')
        self.docs_dir = os.path.join(self.backtest_root, 'docs')
        
        # 고정 투자금 설정
        self.initial_capital = 10_000_000  # 1천만원
        
        # 기본 분석 파라미터
        self.symbol = "NASDAQ"
        self.start_year = 2000
        self.start_month = 1
        self.investment_period_years = 10
        self.dca_months = 60
        
        # 필요한 디렉토리 생성
        self._create_directories()
    
    def _create_directories(self):
        """필요한 디렉토리들 생성"""
        directories = [
            self.results_dir,
            self.excel_dir,
            self.charts_dir,
            self.reports_dir,
            self.configs_dir,
            self.docs_dir
        ]
        
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory)
    
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
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"lump_sum_vs_dca_{self.symbol}_{self.start_year}{self.start_month:02d}_{timestamp}.xlsx"
    
    def get_excel_filepath(self) -> str:
        """Excel 결과 파일 전체 경로 반환"""
        return os.path.join(self.excel_dir, self.get_excel_filename())
    
    def save_config(self, filename: str = None) -> str:
        """현재 설정을 파일로 저장"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"config_{self.symbol}_{self.start_year}{self.start_month:02d}_{timestamp}.json"
        
        config_path = os.path.join(self.configs_dir, filename)
        
        import json
        config_data = self.to_dict()
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
        
        return config_path
    
    def load_config(self, filename: str):
        """설정 파일에서 불러오기"""
        config_path = os.path.join(self.configs_dir, filename)
        
        import json
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        self.symbol = config_data['symbol']
        self.start_year = config_data['start_year']
        self.start_month = config_data['start_month']
        self.investment_period_years = config_data['investment_period_years']
        self.dca_months = config_data['dca_months']
        self.initial_capital = config_data['initial_capital']
    
    def to_dict(self) -> Dict[str, Any]:
        """설정을 딕셔너리로 반환"""
        return {
            'symbol': self.symbol,
            'start_year': self.start_year,
            'start_month': self.start_month,
            'investment_period_years': self.investment_period_years,
            'dca_months': self.dca_months,
            'initial_capital': self.initial_capital,
            'dca_monthly_amount': self.get_dca_monthly_amount(),
            'backtest_type': 'lump_sum_vs_dca',
            'created_at': datetime.now().isoformat()
        }
    
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

결과 저장 경로:
- Excel: {self.excel_dir}
- 차트: {self.charts_dir}
- 보고서: {self.reports_dir}
"""