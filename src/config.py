"""
설정 관리 모듈
"""

from datetime import datetime, timedelta

class Config:
    """퀀트 투자 분석 설정"""
    
    def __init__(self):
        # 기본 설정값들 (여기서 변경 가능)
        
        # 분석 대상 심볼
        self.symbol = "^GSPC"  # S&P 500 지수
        # 다른 옵션들:
        # "^IXIC" - 나스닥 지수
        # "QQQ" - 나스닥 ETF
        # "SPY" - S&P 500 ETF
        # "AAPL" - 개별 주식
        
        # 분석 기간
        self.end_date = datetime.now()
        self.start_date = self.end_date - timedelta(days=365 * 10)  # 10년
        
        # 투자 설정
        self.initial_capital = 100000  # 초기 자본 ($100,000)
        self.monthly_investment = 1000  # 월 적립금 ($1,000)
        
        # 수수료 설정
        self.commission_rate = 0.001  # 0.1% 수수료
        
        # 리밸런싱 설정
        self.rebalance_frequency = "monthly"  # monthly, quarterly, yearly
        
        # 차트 설정
        self.show_charts = True
        self.save_charts = True
        self.chart_directory = "results/charts"
        
        # 결과 저장 설정
        self.save_results = True
        self.results_directory = "results"
    
    def get_date_range_str(self):
        """날짜 범위를 문자열로 반환"""
        start_str = self.start_date.strftime("%Y-%m-%d")
        end_str = self.end_date.strftime("%Y-%m-%d")
        return f"{start_str} ~ {end_str}"
    
    def update_symbol(self, symbol):
        """심볼 업데이트"""
        self.symbol = symbol
    
    def update_date_range(self, start_date, end_date):
        """날짜 범위 업데이트"""
        self.start_date = start_date
        self.end_date = end_date
    
    def update_capital(self, initial_capital, monthly_investment=None):
        """자본 설정 업데이트"""
        self.initial_capital = initial_capital
        if monthly_investment is not None:
            self.monthly_investment = monthly_investment