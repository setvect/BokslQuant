"""
일시투자 vs 적립투자 전략 팩토리
"""
from .strategies.lump_sum_strategy import LumpSumStrategy
from .strategies.dca_strategy import DollarCostAverageStrategy


class LumpSumVsDcaStrategyFactory:
    """일시투자 vs 적립투자 전략 팩토리"""
    
    @staticmethod
    def create_strategy(strategy_type: str, config):
        """전략 생성"""
        if strategy_type == 'lump_sum':
            return LumpSumStrategy(config)
        elif strategy_type == 'dca':
            return DollarCostAverageStrategy(config)
        else:
            raise ValueError(f"지원하지 않는 전략 타입: {strategy_type}")