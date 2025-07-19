# 일시투자 vs 적립투자 백테스팅

## 개요
일시투자와 적립투자 전략의 성과를 비교 분석하는 독립적인 백테스팅 모듈입니다.

## 디렉토리 구조
```
lump_sum_vs_dca/
├── src/                           # 소스코드
│   ├── config.py                  # 백테스팅 전용 설정
│   ├── lump_sum_vs_dca_backtester.py  # 백테스터
│   ├── excel_exporter.py          # Excel 내보내기
│   ├── strategy_factory.py        # 전략 팩토리
│   ├── main_interactive.py        # 대화형 실행 스크립트 (레거시)
│   └── strategies/                # 투자 전략들
│       ├── lump_sum_strategy.py   # 일시투자 전략
│       └── dca_strategy.py        # 적립투자 전략
├── results/                       # 분석 결과물
│   ├── excel/                     # Excel 파일들
│   ├── charts/                    # 차트 파일들
│   └── reports/                   # 보고서들
├── docs/                          # 백테스팅별 문서
├── run_backtest.py               # 실행 스크립트
└── README.md                     # 이 파일
```

## 실행 방법

### 테스트 코드 방식 (권장)
```bash
# 1. run_backtest.py에서 BACKTEST_CONFIG 변수 수정
# 2. 실행
python run_backtest.py
```

#### 설정 변수 예시
```python
BACKTEST_CONFIG = {
    'symbol': 'NASDAQ',                    # 투자 지수
    'start_year': 2020,                    # 투자 시작 연도
    'start_month': 1,                      # 투자 시작 월 (1-12)
    'investment_period_years': 3,          # 투자 기간 (년)
    'dca_months': 24,                      # 적립 분할 월수
}
```

#### 장점
- 반복 실행 용이
- 설정 관리 간편
- 자동화 가능
- 버전 관리 추적 가능

### 대화형 실행 (레거시)
```bash
cd src
python main_interactive.py
```

## 설정

### 기본 설정
- **투자금**: 10,000,000원 (고정)
- **기본 지수**: NASDAQ
- **기본 투자 기간**: 10년
- **기본 적립 분할**: 60개월

### 설정 관리
백테스트 설정은 Excel 파일의 "백테스트 설정" 시트에 자동으로 저장됩니다.

```python
from src.config import LumpSumVsDcaConfig

# 설정 생성 및 파라미터 설정
config = LumpSumVsDcaConfig()
config.set_analysis_params('NASDAQ', 2020, 1, 3, 24)

# 백테스트 실행 시 Excel 파일에 설정 정보가 자동 저장됨
```

## 분석 결과물

### 1. Excel 파일
- **백테스트 설정**: 실행 설정 정보 (투자 설정, 파일 정보 등)
- **매수 내역**: 거래별 세부 정보
- **일 수익률 변화**: 일별 포트폴리오 변화
- **분석 요약**: 성과 지표 비교

### 2. 성과 지표
- 최종 수익률
- CAGR (연평균성장률)
- MDD (최대손실폭)
- 샤프 지수
- 변동성
- 최종 가치

## 확장 방법

### 새로운 전략 추가
1. `strategies/` 폴더에 새 전략 클래스 생성
2. `BaseStrategy`를 상속받아 `execute()` 메서드 구현
3. `strategy_factory.py`에 전략 등록

### 새로운 지표 추가
1. `analyzer.py`의 `calculate_metrics()` 메서드 확장
2. `excel_exporter.py`의 요약 테이블에 지표 추가

## 의존성
- pandas
- numpy
- openpyxl
- dateutil

## 주의사항
- 이 모듈은 독립적으로 실행되도록 설계됨
- 공통 모듈(`src/`)에 대한 의존성 최소화
- 결과물은 `results/` 하위 디렉토리에 자동 저장
- 백테스트 설정은 Excel 파일에 통합 저장되어 별도 설정 파일 불필요