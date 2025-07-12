"""
확률 기반 백테스팅 분석 모듈
1972년~2015년 매월 시작점에서 일시투자 vs 적립식투자 성과 비교
"""
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import pandas as pd
import numpy as np
from dateutil.relativedelta import relativedelta


@dataclass
class ScenarioConfig:
    """시나리오별 투자 설정"""
    total_amount: float = 60000  # 총 투자금액
    investment_period_months: int = 60  # 적립식 투자 기간 (5년)
    analysis_period_years: int = 10  # 성과 분석 기간
    start_year: int = 1972
    start_month: int = 1
    end_year: int = 2015
    end_month: int = 1


@dataclass
class ScenarioResult:
    """개별 시나리오 결과"""
    start_date: str
    end_date: str
    lump_sum_return: float  # 일시투자 수익률 (%)
    dca_return: float  # 적립식투자 수익률 (%)
    lump_sum_final_value: float  # 일시투자 최종 가치
    dca_final_value: float  # 적립식투자 최종 가치
    winner: str  # "일시투자" or "적립식투자"
    return_difference: float  # 수익률 차이 (%p)
    # 새로 추가된 지표들
    lump_sum_cagr: float  # 일시투자 연평균수익률 (%)
    dca_cagr: float  # 적립식투자 연평균수익률 (%)
    lump_sum_mdd: float  # 일시투자 최대낙폭 (%)
    dca_mdd: float  # 적립식투자 최대낙폭 (%)
    lump_sum_sharpe: float  # 일시투자 샤프지수
    dca_sharpe: float  # 적립식투자 샤프지수
    dca_avg_price: float  # 적립식투자 평균단가
    dca_total_shares: float  # 적립식투자 총 구매 수량
    start_price: float  # 투자 시작일 지수 가격
    end_price: float  # 투자 종료일 지수 가격
    
    def to_dict(self) -> Dict:
        """딕셔너리로 변환"""
        return {
            "시작일": self.start_date,
            "측정일": self.end_date,
            "일시투자_수익률": round(self.lump_sum_return, 2),
            "적립식투자_수익률": round(self.dca_return, 2),
            "일시투자_최종가치": round(self.lump_sum_final_value, 0),
            "적립식투자_최종가치": round(self.dca_final_value, 0),
            "승자": self.winner,
            "수익률차이": round(self.return_difference, 2),
            "일시투자_CAGR": round(self.lump_sum_cagr, 2),
            "적립식투자_CAGR": round(self.dca_cagr, 2),
            "일시투자_MDD": round(self.lump_sum_mdd, 2),
            "적립식투자_MDD": round(self.dca_mdd, 2),
            "일시투자_샤프지수": round(self.lump_sum_sharpe, 3),
            "적립식투자_샤프지수": round(self.dca_sharpe, 3),
            "적립식_평단가": round(self.dca_avg_price, 2),
            "적립식_총구매수량": round(self.dca_total_shares, 2),
            "시작일_지수가격": round(self.start_price, 2),
            "측정일_지수가격": round(self.end_price, 2)
        }


class ProbabilisticBacktester:
    """확률 기반 백테스팅 엔진"""
    
    def __init__(self, config: ScenarioConfig):
        self.config = config
        self.scenarios: List[ScenarioResult] = []
        
    def generate_scenarios(self) -> List[Tuple[datetime, datetime]]:
        """시나리오 시작/종료 날짜 생성"""
        import pytz
        scenarios = []
        
        current_date = datetime(self.config.start_year, self.config.start_month, 1)
        end_limit = datetime(self.config.end_year, self.config.end_month, 1)
        
        while current_date < end_limit:
            start_date = current_date
            end_date = start_date + relativedelta(years=self.config.analysis_period_years)
            
            # UTC timezone 추가
            start_date_utc = start_date.replace(tzinfo=pytz.UTC)
            end_date_utc = end_date.replace(tzinfo=pytz.UTC)
            
            scenarios.append((start_date_utc, end_date_utc))
            
            # 다음 달로 이동
            current_date = current_date + relativedelta(months=1)
            
        return scenarios
    
    def run_single_scenario(self, price_data: pd.DataFrame, 
                           start_date: datetime, 
                           end_date: datetime) -> ScenarioResult:
        """단일 시나리오 백테스팅 실행"""
        
        # 날짜 범위 필터링
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')
        
        # 시나리오 날짜는 이미 UTC timezone이 있으므로 직접 비교
        mask = (price_data.index >= start_date) & (price_data.index <= end_date)
        
        scenario_data = price_data[mask].copy()
        
        if len(scenario_data) < 120:  # 최소 10년 데이터 필요
            raise ValueError(f"데이터 부족: {start_date_str} ~ {end_date_str}")
        
        # 일시투자 백테스팅
        lump_sum_result = self._run_lump_sum(scenario_data)
        
        # 적립식투자 백테스팅
        dca_result = self._run_dca(scenario_data)
        
        # 결과 비교
        winner = "일시투자" if lump_sum_result['return'] > dca_result['return'] else "적립식투자"
        return_diff = lump_sum_result['return'] - dca_result['return']
        
        # 시작가격과 종료가격 추출
        start_price = scenario_data['Open'].iloc[0]
        end_price = scenario_data['Close'].iloc[-1]
        
        return ScenarioResult(
            start_date=start_date_str,
            end_date=end_date_str,
            lump_sum_return=lump_sum_result['return'],
            dca_return=dca_result['return'],
            lump_sum_final_value=lump_sum_result['final_value'],
            dca_final_value=dca_result['final_value'],
            winner=winner,
            return_difference=return_diff,
            lump_sum_cagr=lump_sum_result['cagr'],
            dca_cagr=dca_result['cagr'],
            lump_sum_mdd=lump_sum_result['mdd'],
            dca_mdd=dca_result['mdd'],
            lump_sum_sharpe=lump_sum_result['sharpe'],
            dca_sharpe=dca_result['sharpe'],
            dca_avg_price=dca_result['avg_price'],
            dca_total_shares=dca_result['shares'],
            start_price=start_price,
            end_price=end_price
        )
    
    def _run_lump_sum(self, data: pd.DataFrame) -> Dict:
        """일시투자 백테스팅"""
        initial_price = data['Open'].iloc[0]
        final_price = data['Close'].iloc[-1]
        
        shares = self.config.total_amount / initial_price
        final_value = shares * final_price
        total_return = (final_value / self.config.total_amount - 1) * 100
        
        # CAGR 계산 (연평균 수익률)
        years = self.config.analysis_period_years
        cagr = ((final_value / self.config.total_amount) ** (1/years) - 1) * 100 if years > 0 else 0
        
        # MDD 및 샤프지수 계산을 위한 가격 시계열 생성
        portfolio_values = data['Close'] * shares
        daily_returns = portfolio_values.pct_change().dropna()
        
        # MDD 계산
        cumulative_returns = portfolio_values / portfolio_values.iloc[0]
        rolling_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - rolling_max) / rolling_max * 100
        mdd = drawdown.min()
        
        # 샤프지수 계산
        if len(daily_returns) > 0 and daily_returns.std() > 0:
            excess_return = cagr - 2.0  # 무위험 수익률 2% 가정
            volatility = daily_returns.std() * np.sqrt(252) * 100  # 연환산 변동성
            sharpe_ratio = excess_return / volatility if volatility > 0 else 0
        else:
            sharpe_ratio = 0
        
        return {
            'final_value': final_value,
            'return': total_return,
            'shares': shares,
            'cagr': cagr,
            'mdd': mdd,
            'sharpe': sharpe_ratio
        }
    
    def _run_dca(self, data: pd.DataFrame) -> Dict:
        """적립식투자 백테스팅 (5년간 매월 투자)"""
        monthly_amount = self.config.total_amount / self.config.investment_period_months
        total_shares = 0
        total_invested = 0
        investment_records = []  # 투자 기록 저장
        
        # 매월 투자 (60개월)
        for month in range(min(self.config.investment_period_months, len(data))):
            if month < len(data):
                monthly_price = data['Open'].iloc[month]
                shares_bought = monthly_amount / monthly_price
                total_shares += shares_bought
                total_invested += monthly_amount
                investment_records.append({
                    'month': month,
                    'price': monthly_price,
                    'amount': monthly_amount,
                    'shares': shares_bought
                })
        
        # 평단가 계산
        avg_price = total_invested / total_shares if total_shares > 0 else 0
        
        # 최종 가치 계산 (10년 후)
        final_price = data['Close'].iloc[-1]
        final_value = total_shares * final_price
        total_return = (final_value / total_invested - 1) * 100
        
        # CAGR 계산
        years = self.config.analysis_period_years
        cagr = ((final_value / total_invested) ** (1/years) - 1) * 100 if years > 0 and total_invested > 0 else 0
        
        # MDD 및 샤프지수 계산을 위한 포트폴리오 가치 시계열 생성
        portfolio_values = pd.Series(index=data.index, dtype=float)
        current_shares = 0
        current_invested = 0
        investment_month = 0
        
        for i, date in enumerate(data.index):
            # 투자 기간 중이면 매월 투자 진행
            if investment_month < self.config.investment_period_months and i % 21 == 0:  # 대략 월별 (21 영업일)
                if investment_month < len(investment_records):
                    current_shares += investment_records[investment_month]['shares']
                    current_invested += investment_records[investment_month]['amount']
                    investment_month += 1
            
            # 포트폴리오 가치 계산
            portfolio_values.iloc[i] = current_shares * data['Close'].iloc[i]
        
        # 실제 투자한 부분만 사용하여 수익률 계산
        portfolio_values = portfolio_values.dropna()
        if len(portfolio_values) > 1:
            # 포트폴리오 가치 기준 수익률 계산 (원금 대비)
            invested_series = pd.Series(index=portfolio_values.index)
            month_tracker = 0
            invested_amount = 0
            
            for i, date in enumerate(portfolio_values.index):
                if month_tracker < self.config.investment_period_months and i % 21 == 0:
                    if month_tracker < len(investment_records):
                        invested_amount += investment_records[month_tracker]['amount']
                        month_tracker += 1
                invested_series.iloc[i] = invested_amount if invested_amount > 0 else investment_records[0]['amount']
            
            # MDD 계산 (투자원금 대비)
            returns_ratio = portfolio_values / invested_series
            rolling_max = returns_ratio.expanding().max()
            drawdown = (returns_ratio - rolling_max) / rolling_max * 100
            mdd = drawdown.min()
            
            # 일별 수익률 계산
            daily_returns = portfolio_values.pct_change().dropna()
            
            # 샤프지수 계산
            if len(daily_returns) > 0 and daily_returns.std() > 0:
                excess_return = cagr - 2.0  # 무위험 수익률 2% 가정
                volatility = daily_returns.std() * np.sqrt(252) * 100  # 연환산 변동성
                sharpe_ratio = excess_return / volatility if volatility > 0 else 0
            else:
                sharpe_ratio = 0
        else:
            mdd = 0
            sharpe_ratio = 0
        
        return {
            'final_value': final_value,
            'return': total_return,
            'total_invested': total_invested,
            'shares': total_shares,
            'avg_price': avg_price,
            'cagr': cagr,
            'mdd': mdd,
            'sharpe': sharpe_ratio
        }
    
    def run_all_scenarios(self, price_data: pd.DataFrame) -> None:
        """모든 시나리오 실행"""
        scenarios = self.generate_scenarios()
        self.scenarios = []
        
        print(f"📊 총 {len(scenarios)}개 시나리오 분석 시작...")
        
        successful_scenarios = 0
        failed_scenarios = 0
        
        for i, (start_date, end_date) in enumerate(scenarios):
            try:
                result = self.run_single_scenario(price_data, start_date, end_date)
                self.scenarios.append(result)
                successful_scenarios += 1
                
                # 진행상황 출력 (매 50개마다)
                if (i + 1) % 50 == 0:
                    print(f"  📈 진행상황: {i + 1}/{len(scenarios)} ({(i+1)/len(scenarios)*100:.1f}%)")
                    
            except Exception as e:
                failed_scenarios += 1
                if failed_scenarios <= 5:  # 처음 5개 오류만 출력
                    print(f"  ⚠️ 시나리오 실패: {start_date.strftime('%Y-%m')} - {str(e)}")
        
        print(f"✅ 분석 완료: 성공 {successful_scenarios}개, 실패 {failed_scenarios}개")
    
    def get_summary_statistics(self) -> Dict:
        """요약 통계 생성"""
        if not self.scenarios:
            return {}
        
        # 기본 통계
        total_scenarios = len(self.scenarios)
        lump_sum_wins = sum(1 for s in self.scenarios if s.winner == "일시투자")
        dca_wins = total_scenarios - lump_sum_wins
        
        # 수익률 데이터
        lump_sum_returns = [s.lump_sum_return for s in self.scenarios]
        dca_returns = [s.dca_return for s in self.scenarios]
        return_differences = [s.return_difference for s in self.scenarios]
        
        # 통계 계산
        stats = {
            "기본_통계": {
                "총_시나리오수": total_scenarios,
                "일시투자_승리": lump_sum_wins,
                "적립식투자_승리": dca_wins,
                "일시투자_승률": round(lump_sum_wins / total_scenarios * 100, 1),
                "적립식투자_승률": round(dca_wins / total_scenarios * 100, 1)
            },
            "수익률_통계": {
                "일시투자_평균수익률": round(np.mean(lump_sum_returns), 2),
                "적립식투자_평균수익률": round(np.mean(dca_returns), 2),
                "평균_수익률차이": round(np.mean(return_differences), 2),
                "일시투자_표준편차": round(np.std(lump_sum_returns), 2),
                "적립식투자_표준편차": round(np.std(dca_returns), 2)
            },
            "극값_분석": {
                "일시투자_최고수익률": round(max(lump_sum_returns), 2),
                "일시투자_최저수익률": round(min(lump_sum_returns), 2),
                "적립식투자_최고수익률": round(max(dca_returns), 2),
                "적립식투자_최저수익률": round(min(dca_returns), 2),
                "최대_수익률차이": round(max(return_differences), 2),
                "최소_수익률차이": round(min(return_differences), 2)
            }
        }
        
        # 최고/최악 시나리오 찾기
        best_lump_sum = max(self.scenarios, key=lambda x: x.lump_sum_return)
        worst_lump_sum = min(self.scenarios, key=lambda x: x.lump_sum_return)
        best_dca = max(self.scenarios, key=lambda x: x.dca_return)
        worst_dca = min(self.scenarios, key=lambda x: x.dca_return)
        
        stats["극값_시나리오"] = {
            "일시투자_최고": {
                "시작일": best_lump_sum.start_date,
                "수익률": best_lump_sum.lump_sum_return
            },
            "일시투자_최악": {
                "시작일": worst_lump_sum.start_date,
                "수익률": worst_lump_sum.lump_sum_return
            },
            "적립식투자_최고": {
                "시작일": best_dca.start_date,
                "수익률": best_dca.dca_return
            },
            "적립식투자_최악": {
                "시작일": worst_dca.start_date,
                "수익률": worst_dca.dca_return
            }
        }
        
        return stats
    
    def export_results(self, output_path: str = "results/") -> str:
        """결과를 CSV로 내보내기"""
        import os
        from datetime import datetime
        
        if not self.scenarios:
            raise ValueError("분석된 시나리오가 없습니다.")
        
        # 결과 디렉토리 생성
        os.makedirs(output_path, exist_ok=True)
        
        # 데이터프레임 생성
        df = pd.DataFrame([scenario.to_dict() for scenario in self.scenarios])
        
        # 파일명 생성
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"확률분석_나스닥_{timestamp}.csv"
        filepath = os.path.join(output_path, filename)
        
        # CSV 저장
        df.to_csv(filepath, index=False, encoding='utf-8-sig')
        
        return filepath
    
    def get_scenarios_data(self) -> List[Dict]:
        """시나리오 데이터 리스트 반환"""
        return [scenario.to_dict() for scenario in self.scenarios]