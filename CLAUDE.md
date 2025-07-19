# 복슬퀀트

## 프로젝트 개요
- **프로젝트명**: 복슬퀀트
- **목적**: 다양한 퀀트 투자 전략의 성과를 분석하고 비교하는 Python 기반 백테스팅 시스템
- **주요 기능**: 일시투자 vs 적립식투자, 모멘텀 투자, 변동성 돌파 전략 분석 등

## 명령어
```bash
# 의존성 설치
pip install -r requirements.txt

# 일시투자 vs 적립투자 백테스팅 실행 (테스트 코드 방식)
cd backtests/lump_sum_vs_dca
# 1. run_backtest.py에서 BACKTEST_CONFIG 변수 수정
# 2. 실행
python run_backtest.py

# 기존 방식 (중앙 집중식)
python test_sample.py
```


## 개발 노트
- **일시투자 vs 적립투자 백테스팅**: `backtests/lump_sum_vs_dca/` - ✅ 완성
- **새로운 백테스팅 구조**: 각 백테스팅별 독립 모듈로 구성
- **공통 모듈**: `src/` - 베이스 클래스 및 공통 유틸리티
- **향후 백테스팅**: 모멘텀 전략, 변동성 돌파, 섹터 로테이션 등 계획됨

## 개발 표준 및 가이드라인

### 📊 Excel 파일 생성 표준
Excel 파일을 생성할 때 반드시 다음 기준을 적용하세요:

#### 1. 셀 서식 설정
```python
# 컬럼별 데이터 타입에 맞는 서식 적용
- 날짜: "YYYY-MM-DD" 형식, 가운데 정렬
- 경과월수: 정수 형식, 가운데 정렬  
- 가격/가치/금액: FORMAT_NUMBER_COMMA_SEPARATED1, 오른쪽 정렬
- 수익률/MDD: FORMAT_PERCENTAGE_00 (데이터는 100으로 나누어 저장), 오른쪽 정렬
- 수량/평균단가: "#,##0.00" 형식, 오른쪽 정렬
- 일반 숫자: 정규식 r'^-?\d+\.?\d*$'로 감지, 오른쪽 정렬
- 모든 숫자 데이터: 헤더를 제외한 모든 숫자 데이터는 오른쪽 정렬 필수
```

#### 2. 머리행 고정
```python
# 모든 데이터 시트에 머리행 고정 적용
ws.freeze_panes = 'A2'
```

#### 3. 열 너비 최적화
```python
# 데이터 내용에 맞는 적절한 열 너비 설정
# 길이가 긴 컬럼은 18, 짧은 컬럼은 8-12로 조정
```

#### 4. Excel 수식 오류 방지
```python
# Excel에서 '='로 시작하는 문자열은 수식으로 인식되어 오류 발생
# 제목이나 섹션 구분자에 '='를 사용하지 않도록 주의
# 잘못된 예: '=== 투자 설정 정보 ===' 
# 올바른 예: '[ 투자 설정 정보 ]', '▶ 투자 설정 정보', '투자 설정 정보'
```

### 📈 차트 생성 표준
차트를 생성할 때 반드시 다음 기준을 적용하세요:

#### 1. 한글 폰트 설정 (필수)
```python
import matplotlib.font_manager as fm

# 폰트 캐시 클리어 및 시스템 폰트 재로드
fm._get_fontconfig_fonts.cache_clear()
fm.fontManager.__init__()

# 한글 폰트 찾기 및 설정
korean_fonts = [f.name for f in fm.fontManager.ttflist if 'CJK' in f.name or 'Nanum' in f.name]
if korean_fonts:
    font_name = korean_fonts[0]
    plt.rcParams['font.family'] = font_name
    plt.rcParams['font.sans-serif'] = [font_name] + plt.rcParams['font.sans-serif']
    plt.rcParams['font.monospace'] = [font_name] + plt.rcParams['font.monospace']
    plt.rcParams['font.serif'] = [font_name] + plt.rcParams['font.serif']
else:
    # 대체 폰트 설정
    font_path = '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
    if os.path.exists(font_path):
        prop = fm.FontProperties(fname=font_path)
        font_name = prop.get_name()
        plt.rcParams['font.family'] = font_name
        plt.rcParams['font.sans-serif'] = [font_name] + plt.rcParams['font.sans-serif']

plt.rcParams['axes.unicode_minus'] = False
```

#### 2. 차트 품질 설정
```python
# 고품질 차트 저장
plt.savefig(chart_path, dpi=300, bbox_inches='tight')
```

### 📁 파일 구조 표준

#### 새로운 독립 모듈 구조 (권장)
- 백테스팅별 독립 디렉토리: `backtests/{백테스팅타입}/`
- Excel 파일: `backtests/{백테스팅타입}/results/excel/`
- 차트 파일: `backtests/{백테스팅타입}/results/charts/`
- 보고서: `backtests/{백테스팅타입}/results/reports/`
- 설정 파일: `backtests/{백테스팅타입}/configs/`

#### 기존 중앙 집중식 구조 (레거시)
- Excel 파일: `results/{백테스팅타입}/` 디렉토리에 저장
- 파일명: `{분석종류}_{지수}_{시작일}_{타임스탬프}` 형식 사용

### 🔧 코드 품질 표준
- 중복 코드 방지: 동일한 알고리즘은 하나의 모듈에서 관리
- 메서드 네이밍: 기능을 명확히 표현하는 이름 사용
- 에러 처리: try-except 블록으로 안전한 처리
- 타입 힌트: 함수 시그니처에 타입 명시

### 🚀 백테스팅 실행 표준
백테스팅 실행 시에는 **대화형 입력 방식보다 테스트 코드 방식**을 사용합니다.

#### 테스트 코드 방식 (권장)
```python
# run_backtest.py 파일의 설정 변수 수정
BACKTEST_CONFIG = {
    'symbol': 'NASDAQ',                    # 투자 지수
    'start_year': 2020,                    # 투자 시작 연도
    'start_month': 1,                      # 투자 시작 월
    'investment_period_years': 3,          # 투자 기간 (년)
    'dca_months': 24,                      # 적립 분할 월수
}
```

#### 장점
- **반복 실행 용이**: 동일한 설정으로 여러 번 실행 가능
- **설정 관리**: 변수 값만 수정하면 되므로 간편
- **자동화 가능**: 스크립트나 배치 실행에 적합
- **버전 관리**: 설정 변경 내역을 Git으로 추적 가능

#### 사용법
```bash
# 1. 설정 변수 수정
# 2. 실행
python run_backtest.py
```

## 상세 문서 참조
개발 시 아래 문서들을 반드시 참조하세요:

- **프로젝트 구조**: `docs/project_structure.md` - 디렉토리 구조, 모듈별 역할, 기술 스택
- **기능 요구사항**: `docs/functional_requirements.md` - 핵심 기능, 사용자 시나리오, 확장 계획
- **TODO 리스트**: `docs/todo_list.md` - 개발 단계별 할일, 모듈별 상세 작업 항목

개발 작업 전에 해당 문서들을 읽고 요구사항을 파악한 후 진행하세요.