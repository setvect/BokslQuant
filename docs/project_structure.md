# 복슬퀀트 프로젝트 구조

## 1. 개발 환경

### 1.1 기술 스택
- **언어**: Python 3.8+
- **패키지 관리**: pip, requirements.txt
- **버전 관리**: Git
- **개발 도구**: IDE (PyCharm, VSCode)

### 1.2 핵심 라이브러리
```python
# 데이터 처리
pandas>=1.5.0          # 데이터 조작 및 분석
numpy>=1.24.0           # 수치 계산
yfinance>=0.2.0         # 주식 데이터 수집
pandas-datareader>=0.10.0  # 추가 데이터 소스

# 기술적 분석
ta-lib>=0.4.25          # 기술적 지표
pandas-ta>=0.3.14b      # 판다스 기반 기술적 분석

# 백테스팅
backtrader>=1.9.76      # 이벤트 기반 백테스팅
vectorbt>=0.25.0        # 벡터화 백테스팅

# 성과 분석
quantstats>=0.0.59      # 포트폴리오 분석
pyfolio>=0.9.2          # 성과 분석 및 리포팅

# 시각화
matplotlib>=3.6.0       # 기본 차트
plotly>=5.11.0          # 인터랙티브 차트
seaborn>=0.12.0         # 통계 시각화

# 테스트 및 품질
pytest>=7.0.0           # 단위 테스트
black>=22.0.0           # 코드 포매팅
flake8>=5.0.0           # 코드 스타일 검사
```

## 2. 디렉토리 구조

```
boksl_quant/
├── main.py                 # 메인 실행 파일
├── requirements.txt        # 의존성 라이브러리
├── README.md              # 프로젝트 설명서
├── CLAUDE.md              # AI 개발 가이드
├── src/
│   ├── __init__.py
│   ├── config.py          # 설정 관리
│   ├── data/
│   │   ├── __init__.py
│   │   ├── collector.py   # 데이터 수집
│   │   ├── processor.py   # 데이터 전처리
│   │   └── storage.py     # 데이터 저장
│   ├── strategies/
│   │   ├── __init__.py
│   │   ├── base.py        # 전략 기본 클래스
│   │   ├── momentum.py    # 모멘텀 전략
│   │   ├── volatility.py  # 변동성 전략
│   │   └── reversion.py   # 평균회귀 전략
│   ├── backtesting/
│   │   ├── __init__.py
│   │   ├── engine.py      # 백테스팅 엔진
│   │   ├── portfolio.py   # 포트폴리오 관리
│   │   └── execution.py   # 주문 실행
│   ├── analysis/
│   │   ├── __init__.py
│   │   ├── metrics.py     # 성과 지표
│   │   ├── risk.py        # 위험 분석
│   │   └── comparison.py  # 비교 분석
│   └── visualization/
│       ├── __init__.py
│       ├── charts.py      # 차트 생성
│       ├── reports.py     # 리포트 생성
│       └── utils.py       # 시각화 유틸
├── tests/
│   ├── __init__.py
│   ├── test_data/
│   ├── test_strategies/
│   ├── test_backtesting/
│   └── test_analysis/
├── data/                  # 데이터 저장소
│   ├── cache/            # 캐시된 데이터
│   └── external/         # 외부 데이터
├── results/              # 분석 결과
│   ├── reports/          # 분석 리포트
│   └── charts/           # 생성된 차트
└── docs/                 # 문서
    ├── PRD.md            # 제품 요구사항
    ├── API.md            # API 문서
    └── examples/         # 사용 예제
```

## 3. 모듈별 역할

### 3.1 src/data/
- **collector.py**: 외부 데이터 소스에서 주식, ETF, 암호화폐 데이터 수집
- **processor.py**: 수집된 원시 데이터의 전처리 및 정제
- **storage.py**: 데이터 저장 및 캐싱 관리

### 3.2 src/strategies/
- **base.py**: 모든 투자 전략의 기본 클래스 및 인터페이스
- **momentum.py**: 모멘텀 기반 투자 전략 구현
- **volatility.py**: 변동성 돌파 전략 구현
- **reversion.py**: 평균회귀 전략 구현

### 3.3 src/backtesting/
- **engine.py**: 백테스팅 실행 엔진 및 시뮬레이션 로직
- **portfolio.py**: 포트폴리오 관리 및 자산 배분
- **execution.py**: 주문 실행 및 거래 시뮬레이션

### 3.4 src/analysis/
- **metrics.py**: 수익률, 샤프 비율 등 성과 지표 계산
- **risk.py**: 위험 분석 및 드로다운 계산
- **comparison.py**: 전략 간 비교 분석

### 3.5 src/visualization/
- **charts.py**: 수익률 곡선, 드로다운 차트 등 시각화
- **reports.py**: HTML/PDF 리포트 생성
- **utils.py**: 시각화 관련 유틸리티 함수