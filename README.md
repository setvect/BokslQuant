# 퀀트 투자 성과 분석 시스템

다양한 퀀트 투자 전략의 성과를 분석하고 비교하는 Python 기반 백테스팅 시스템입니다.

## 주요 기능

- **일시투자 vs 적립식투자** 성과 비교
- **모멘텀 투자** 전략 분석
- **변동성 돌파** 전략 구현
- **백테스팅 엔진** 및 성과 지표 계산
- **시각화** 차트 생성

## 프로젝트 구조

```
boksl_quant/
├── main.py              # 메인 실행 파일
├── requirements.txt     # 필요 라이브러리 목록
├── README.md           # 프로젝트 설명서
├── src/
│   ├── __init__.py
│   ├── config.py        # 설정 관리 (투자 변수 조정)
│   ├── data_collector.py    # 데이터 수집 모듈
│   ├── strategies.py        # 투자 전략 구현
│   ├── backtester.py       # 백테스팅 엔진
│   ├── analyzer.py         # 성과 분석 모듈
│   └── visualizer.py       # 시각화 모듈
├── tests/              # 테스트 파일
├── data/               # 수집된 데이터 저장
└── results/            # 분석 결과 및 차트 저장
```

## 설치 및 실행

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. 설정 변경
`src/config.py` 파일에서 다음 변수들을 원하는 값으로 수정:

```python
# 분석 대상 심볼
self.symbol = "^GSPC"  # S&P 500 지수

# 투자 설정
self.initial_capital = 100000    # 초기 자본 ($100,000)
self.monthly_investment = 1000   # 월 적립금 ($1,000)

# 분석 기간 (10년)
self.start_date = self.end_date - timedelta(days=365 * 10)
```

### 3. 실행
```bash
python main.py
```

## 지원하는 투자 대상

- **주요 지수**: S&P 500 (^GSPC), 나스닥 (^IXIC)
- **ETF**: SPY, QQQ, VTI 등
- **개별 주식**: AAPL, MSFT, GOOGL 등
- **암호화폐**: BTC-USD, ETH-USD 등

## 분석 결과

실행 후 다음 결과를 얻을 수 있습니다:

1. **콘솔 출력**: 전략별 성과 비교 테이블
2. **차트 생성**: 포트폴리오 가치 변화 그래프
3. **성과 지표**: 수익률, 샤프비율, 최대 손실 등

## 주요 성과 지표

- **총 수익률**: 투자 기간 동안의 누적 수익률
- **연평균 수익률**: 연간 기준 평균 수익률
- **샤프 비율**: 위험 대비 수익률
- **최대 손실(MDD)**: 최대 낙폭
- **승률**: 수익을 낸 거래의 비율

## 개발 현황

### 완료된 기능
- [x] 프로젝트 구조 설정
- [x] 기본 설정 시스템
- [x] 의존성 관리

### 개발 예정
- [ ] 데이터 수집 모듈
- [ ] 일시투자 전략
- [ ] 적립식투자 전략
- [ ] 백테스팅 엔진
- [ ] 성과 분석 모듈
- [ ] 시각화 모듈
- [ ] 모멘텀 전략
- [ ] 변동성 돌파 전략

## 기술 스택

- **언어**: Python 3.8+
- **데이터**: pandas, numpy, yfinance
- **백테스팅**: backtrader, vectorbt
- **분석**: quantstats, pyfolio
- **시각화**: matplotlib, plotly, seaborn

## 라이선스

MIT License

---

## 업데이트 로그

### 2025-07-10
- 프로젝트 초기 구조 설정
- 기본 설정 시스템 구현
- README 파일 생성