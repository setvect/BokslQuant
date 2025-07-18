# Config 클래스 사용 예시

## 개선된 Config 클래스의 백테스팅 타입별 디렉토리 관리

### 1. 일시투자 vs 적립투자
```python
from src.config import Config

# 기본값 (lump_sum_vs_dca)
config = Config()
# 또는 명시적으로
config = Config(backtest_type="lump_sum_vs_dca")

# 결과 저장 경로: results/lump_sum_vs_dca/
```

### 2. 모멘텀 전략 (향후)
```python
from src.config import Config

config = Config(backtest_type="momentum_strategy")
# 결과 저장 경로: results/momentum_strategy/
```

### 3. 변동성 돌파 전략 (향후)
```python
from src.config import Config

config = Config(backtest_type="volatility_breakout")
# 결과 저장 경로: results/volatility_breakout/
```

### 4. 섹터 로테이션 전략 (향후)
```python
from src.config import Config

config = Config(backtest_type="sector_rotation")
# 결과 저장 경로: results/sector_rotation/
```

## 디렉토리 구조

```
results/
├── lump_sum_vs_dca/              # 일시투자 vs 적립투자 결과
│   ├── lump_sum_vs_dca_NASDAQ_200001_20250719_083137.xlsx
│   └── lump_sum_vs_dca_SP500_202001_20250719_084512.xlsx
├── momentum_strategy/            # 모멘텀 전략 결과 (향후)
│   ├── momentum_NASDAQ_20200101_20250719_090000.xlsx
│   └── momentum_SP500_20210101_20250719_091234.xlsx
├── volatility_breakout/          # 변동성 돌파 전략 결과 (향후)
└── sector_rotation/              # 섹터 로테이션 전략 결과 (향후)
```

## 장점

### 1. 결과물 분리
- 각 백테스팅 타입별로 결과가 명확히 구분됨
- 파일 이름 충돌 방지
- 체계적인 관리 가능

### 2. 확장성
- 새로운 백테스팅 타입 추가 시 자동으로 디렉토리 생성
- 기존 결과물에 영향 없음

### 3. 유지보수성
- 특정 백테스팅의 결과만 삭제/정리 가능
- 백테스팅별 독립적인 관리

## 사용 방법

### Config 인스턴스 생성
```python
# 기본 방식
config = Config("my_backtest_type")

# 설정 확인
print(f"백테스팅 타입: {config.backtest_type}")
print(f"결과 저장 경로: {config.results_dir}")

# 설정 딕셔너리 출력
print(config.to_dict())
```

### 자동 디렉토리 생성
Config 인스턴스를 생성하면 자동으로:
1. `results/` 디렉토리 생성 (없는 경우)
2. `results/{backtest_type}/` 디렉토리 생성 (없는 경우)