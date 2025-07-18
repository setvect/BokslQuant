# 새로운 백테스팅 구조 가이드

## 업데이트된 프로젝트 구조

기존의 `src/analysis_types/` 구조에서 독립적인 `backtests/` 구조로 변경되었습니다.

### 새로운 구조
```
boksl_quant/
├── src/                           # 공통 모듈
│   ├── config.py                  # 기본 설정
│   ├── backtester.py             # 베이스 백테스터
│   ├── analyzer.py               # 성과 분석기
│   └── strategies/               # 공통 전략들
│       └── base_strategy.py      # 전략 베이스 클래스
├── backtests/                    # 백테스팅별 독립 모듈
│   └── lump_sum_vs_dca/         # 일시투자 vs 적립투자
│       ├── src/                 # 전용 소스코드
│       │   ├── config.py        # 백테스팅 전용 설정
│       │   ├── lump_sum_vs_dca_backtester.py
│       │   ├── excel_exporter.py
│       │   ├── strategy_factory.py
│       │   ├── main.py          # 백테스팅 메인
│       │   └── strategies/      # 전용 전략들
│       ├── results/             # 결과물 저장
│       │   ├── excel/          # Excel 파일들
│       │   ├── charts/         # 차트 파일들
│       │   └── reports/        # 보고서들
│       ├── configs/            # 설정 파일들
│       ├── docs/               # 백테스팅 문서
│       ├── run_backtest.py     # 실행 스크립트
│       └── README.md           # 백테스팅 가이드
└── data/                       # 공통 데이터
```

## 변경 사항

### 1. 디렉토리 구조 변경
- **이전**: `src/analysis_types/lump_sum_vs_dca/`
- **이후**: `backtests/lump_sum_vs_dca/`

### 2. 독립적인 실행 환경
각 백테스팅은 완전히 독립적으로 실행됩니다:
```bash
# 일시투자 vs 적립투자 백테스팅 실행
cd backtests/lump_sum_vs_dca
python run_backtest.py
```

### 3. 결과물 분리
각 백테스팅의 결과물이 독립적으로 관리됩니다:
- Excel 파일: `backtests/lump_sum_vs_dca/results/excel/`
- 차트: `backtests/lump_sum_vs_dca/results/charts/`
- 보고서: `backtests/lump_sum_vs_dca/results/reports/`

### 4. 설정 시스템 개선
백테스팅별 전용 설정 클래스:
```python
from config import LumpSumVsDcaConfig

config = LumpSumVsDcaConfig()
config.set_analysis_params('NASDAQ', 2020, 1, 3, 24)
config.save_config()  # configs/ 디렉토리에 저장
```

## 장점

### 1. 모듈화
- 각 백테스팅이 완전히 독립적
- 코드 충돌 없음
- 개별 유지보수 가능

### 2. 확장성
새로운 백테스팅 추가가 용이:
```bash
mkdir backtests/new_strategy
cp -r backtests/lump_sum_vs_dca/* backtests/new_strategy/
# 필요한 부분만 수정
```

### 3. 결과물 관리
- 백테스팅별 결과물 분리
- 각 백테스팅의 설정 파일 저장
- 독립적인 문서화

### 4. 재사용성
공통 모듈(`src/`)은 여러 백테스팅에서 재사용:
- `backtester.py`: 베이스 백테스터
- `analyzer.py`: 성과 분석기
- `strategies/base_strategy.py`: 전략 베이스 클래스

## 향후 계획

### 예정된 백테스팅들
```
backtests/
├── lump_sum_vs_dca/        # ✅ 완료
├── momentum_strategy/       # 📋 계획됨
├── volatility_breakout/     # 📋 계획됨
├── sector_rotation/         # 📋 계획됨
└── pairs_trading/          # 📋 계획됨
```

각 백테스팅은 동일한 구조를 가지며 독립적으로 개발/관리됩니다.