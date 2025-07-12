# 데이터 수집 가이드

## 개요
`src/data_collector.py`는 주요 주식 지수의 일봉 데이터를 수집하는 Python 모듈입니다. yfinance API를 사용하여 전 세계 주요 지수의 과거 데이터를 수집하고 CSV 파일로 저장합니다.

## 프로그램 실행 방법

### 기본 사용법

```bash
# 의존성 설치 (최초 1회)
pip install -r requirements.txt

# 지원하는 지수 목록 확인
python src/data_collector.py --list

# 특정 지수들 수집
python src/data_collector.py --indices NASDAQ SP500 KOSPI

# 모든 지수 수집
python src/data_collector.py --all

# 저장된 데이터 요약 확인
python src/data_collector.py --summary

# 도움말
python src/data_collector.py --help
```

### 고급 옵션

```bash
# 사용자 정의 데이터 디렉토리 지정
python src/data_collector.py --indices NASDAQ --data-dir custom_data

# 한국 지수 전용 수집기 (더 나은 한국 데이터)
python src/korea_data_collector.py --indices KOSPI
```

## 지원하는 지수 목록

| 지수명 | 심볼   | 예상 시작일 | 설명              | 비고                 |
| ------ | ------ | ----------- | ----------------- | -------------------- |
| NASDAQ | ^IXIC  | 1971-02-05  | 나스닥 종합지수   |                      |
| SP500  | ^GSPC  | 1957-03-04  | S&P 500           | 실제 500개 기업 기준 |
| DOW    | ^DJI   | 1896-05-26  | 다우존스 산업평균 |                      |
| KOSPI  | ^KS11  | 1980-01-04  | 한국 종합주가지수 | ⚠️ 데이터 누락 가능   |
| KOSDAQ | ^KQ11  | 1996-07-01  | 한국 코스닥지수   | ⚠️ 데이터 누락 가능   |
| NIKKEI | ^N225  | 1950-09-07  | 니케이 225        |                      |
| FTSE   | ^FTSE  | 1984-01-03  | FTSE 100          |                      |
| DAX    | ^GDAXI | 1959-12-31  | 독일 DAX          |                      |
| CAC    | ^FCHI  | 1987-12-31  | 프랑스 CAC 40     |                      |
| HSI    | ^HSI   | 1964-07-31  | 홍콩 항셍지수     |                      |

## 수집 데이터 항목

각 지수에 대해 다음 데이터가 수집됩니다:

### 기본 OHLCV 데이터
- **Date**: 거래일 (인덱스 컬럼)
- **Open**: 시가 - 해당일 첫 거래 가격
- **High**: 고가 - 해당일 최고 거래 가격
- **Low**: 저가 - 해당일 최저 거래 가격
- **Close**: 종가 - 해당일 마지막 거래 가격
- **Volume**: 거래량 - 해당일 총 거래된 주식 수

### 추가 정보
- **Dividends**: 배당금 정보 (지수의 경우 일반적으로 0)
- **Stock Splits**: 주식 분할 정보 (지수의 경우 일반적으로 0)

### 데이터 특성
- **단위**: 지수 포인트 (Volume은 주식 수)
- **정밀도**: 소수점 2자리로 반올림
- **주기**: 일봉 (1일 단위)
- **시간대**: 각 지수의 현지 시간대
- **기간**: 각 지수별 사용 가능한 전체 기간 (`period="max"`)

## 저장 파일 형식

### 파일명 규칙
```
data/{INDEX_NAME}_data.csv
```
예시:
- `data/NASDAQ_data.csv`
- `data/SP500_data.csv`
- `data/KOSPI_data.csv`

### CSV 파일 구조
```csv
Date,Open,High,Low,Close,Volume,Dividends,Stock Splits
2024-01-02,15000.15,15100.25,14950.80,15080.45,2500000000,0.0,0.0
2024-01-03,15080.45,15120.60,15020.30,15105.20,2600000000,0.0,0.0
...
```

## 데이터 품질 및 주의사항

### 데이터 검증
- 각 지수별 예상 시작일과 실제 데이터 시작일 비교
- 누락된 연수 계산 및 경고 표시
- 중복 데이터 자동 제거

### 알려진 제약사항
1. **한국 지수 (KOSPI, KOSDAQ)**: Yahoo Finance에서 일부 기간 데이터 누락
   - 해결책: `korea_data_collector.py` 사용 권장
2. **주말/공휴일**: 해당 거래소의 휴장일 데이터는 없음
3. **시간대**: 각 거래소 현지 시간 기준

### 데이터 업데이트
- 기존 파일이 있는 경우 자동으로 병합
- 중복 제거 후 날짜순 정렬
- 최신 데이터로 덮어쓰기 (`keep='last'`)

## 사용 예시

### 단일 지수 수집
```bash
python src/data_collector.py --indices NASDAQ
```

### 여러 지수 동시 수집
```bash
python src/data_collector.py --indices NASDAQ SP500 DOW KOSPI
```

### 전체 지수 수집 (약 10분 소요)
```bash
python src/data_collector.py --all
```

### 결과 확인
```bash
python src/data_collector.py --summary
```

## 문제 해결

### 일반적인 오류
1. **네트워크 오류**: 인터넷 연결 확인
2. **의존성 오류**: `pip install -r requirements.txt` 재실행
3. **권한 오류**: 데이터 디렉토리 쓰기 권한 확인
4. **한국 지수 데이터 부족**: `korea_data_collector.py` 사용

### 성능 최적화
- 필요한 지수만 선택적으로 수집
- 캐시 디렉토리 활용 (`data/cache/`)
- 정기적인 점진적 업데이트 수행

## 개발자 정보

### 주요 클래스
- `IndexDataCollector`: 메인 데이터 수집기 클래스

### 주요 메서드
- `collect_index_data()`: 단일 지수 데이터 수집
- `collect_multiple_indices()`: 다중 지수 데이터 수집
- `save_data()`: CSV 파일 저장
- `get_summary()`: 저장된 데이터 요약 정보

### 의존성
- `pandas`: 데이터 처리
- `yfinance`: Yahoo Finance API
- `argparse`: 명령행 인수 처리
- `pathlib`: 파일 경로 처리