# 퀀트 투자 성과 분석 시스템 (boksl_quant)

## 프로젝트 개요
- **프로젝트명**: boksl_quant
- **목적**: 다양한 퀀트 투자 전략의 성과를 분석하고 비교하는 Python 기반 백테스팅 시스템
- **주요 기능**: 일시투자 vs 적립식투자, 모멘텀 투자, 변동성 돌파 전략 분석

## 기술 스택
- **언어**: Python 3.8+
- **데이터 처리**: pandas, numpy
- **데이터 수집**: yfinance, pandas-datareader
- **기술적 분석**: ta-lib, pandas-ta
- **백테스팅**: backtrader, vectorbt
- **성과 분석**: quantstats, pyfolio
- **시각화**: matplotlib, plotly, seaborn

## 프로젝트 구조
```
boksl_quant/
├── main.py              # 메인 실행 파일
├── requirements.txt     # 의존성 라이브러리
├── src/
│   ├── config.py        # 설정 관리 (투자 변수 조정)
│   ├── data_collector.py    # 데이터 수집 모듈 (미구현)
│   ├── strategies.py        # 투자 전략 구현 (미구현)
│   ├── backtester.py       # 백테스팅 엔진 (미구현)
│   ├── analyzer.py         # 성과 분석 모듈 (미구현)
│   └── visualizer.py       # 시각화 모듈 (미구현)
├── tests/               # 테스트 디렉토리
├── data/                # 데이터 저장
└── results/             # 분석 결과 저장
```

## 현재 상태
### 완료된 기능
- [x] 프로젝트 구조 설정
- [x] 기본 설정 시스템 (config.py)
- [x] 의존성 관리 (requirements.txt)
- [x] 메인 실행 파일 구조 (main.py)

### 개발 예정 (미구현)
- [ ] 데이터 수집 모듈 (data_collector.py)
- [ ] 일시투자 전략 (strategies.py)
- [ ] 적립식투자 전략 (strategies.py)
- [ ] 백테스팅 엔진 (backtester.py)
- [ ] 성과 분석 모듈 (analyzer.py)
- [ ] 시각화 모듈 (visualizer.py)
- [ ] 모멘텀 전략
- [ ] 변동성 돌파 전략

## 주요 설정 (config.py)
- **분석 대상**: S&P 500 지수 (^GSPC)
- **분석 기간**: 10년 (현재 - 10년)
- **초기 자본**: $100,000
- **월 적립금**: $1,000
- **수수료**: 0.1%
- **리밸런싱**: 월별

## 명령어
```bash
# 의존성 설치
pip install -r requirements.txt

# 실행 (현재 미완성)
python main.py
```

## 지원 투자 대상
- 주요 지수: S&P 500 (^GSPC), 나스닥 (^IXIC)
- ETF: SPY, QQQ, VTI
- 개별 주식: AAPL, MSFT, GOOGL
- 암호화폐: BTC-USD, ETH-USD

## 목표 성과 지표
- 총 수익률, 연평균 수익률
- 샤프 비율 (위험 대비 수익률)
- 최대 손실(MDD)
- 승률

## 개발 노트
- 프로젝트는 초기 단계로 main.py에서 참조하는 대부분의 모듈이 아직 구현되지 않음
- 설정 시스템만 완성되어 있음
- 향후 모듈별 순차적 개발 필요