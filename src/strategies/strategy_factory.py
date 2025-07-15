"""
전략 팩토리
"""


class StrategyFactory:
    """전략 팩토리 - 기본 클래스"""
    
    @staticmethod
    def create_strategy(strategy_type: str, config):
        """전략 생성 - 하위 클래스에서 구현"""
        raise NotImplementedError("하위 클래스에서 구현해야 합니다")