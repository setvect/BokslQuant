# 백테스팅 디렉토리 구조 가이드

## 제안하는 새로운 구조

```
boksl_quant/
├── backtests/                      # 백테스팅별 독립 디렉토리
│   ├── lump_sum_vs_dca/           # 일시투자 vs 적립투자
│   │   ├── src/                   # 백테스팅 전용 소스코드
│   │   │   ├── strategies/
│   │   │   ├── backtester.py
│   │   │   ├── excel_exporter.py
│   │   │   └── main.py
│   │   ├── results/               # 분석 결과물
│   │   │   ├── excel/            # Excel 파일들
│   │   │   ├── charts/           # 차트 파일들
│   │   │   └── reports/          # 보고서들
│   │   ├── configs/               # 설정 파일들
│   │   ├── data/                  # 백테스팅별 전용 데이터
│   │   └── docs/                  # 백테스팅별 문서
│   │
│   ├── momentum_strategy/          # 모멘텀 전략 (향후)
│   │   ├── src/
│   │   ├── results/
│   │   ├── configs/
│   │   └── docs/
│   │
│   ├── volatility_breakout/        # 변동성 돌파 전략 (향후)
│   │   ├── src/
│   │   ├── results/
│   │   ├── configs/
│   │   └── docs/
│   │
│   └── sector_rotation/            # 섹터 로테이션 전략 (향후)
│       ├── src/
│       ├── results/
│       ├── configs/
│       └── docs/
│
├── src/                           # 공통 모듈 (기존)
│   ├── config.py                  # 공통 설정
│   ├── data_collector.py          # 데이터 수집
│   ├── analyzer.py                # 공통 분석 도구
│   └── backtester.py             # 베이스 백테스터
│
├── data/                          # 공통 데이터 (기존)
└── docs/                          # 프로젝트 전체 문서 (기존)
```

## 장점

1. **독립성**: 각 백테스팅이 완전히 독립적으로 관리됨
2. **확장성**: 새로운 백테스팅 추가가 용이함
3. **결과물 관리**: 백테스팅별로 결과물이 명확히 구분됨
4. **버전 관리**: 각 백테스팅별로 독립적인 버전 관리 가능
5. **재사용성**: 공통 모듈은 여러 백테스팅에서 재사용

## 구현 계획

1. `backtests/lump_sum_vs_dca/` 디렉토리 생성
2. 기존 `src/analysis_types/lump_sum_vs_dca/` 내용을 새 구조로 이동
3. 결과물 저장 경로 업데이트
4. 설정 시스템 개선
5. 문서 업데이트