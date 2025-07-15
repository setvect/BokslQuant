# 복슬퀀트

## 프로젝트 개요
- **프로젝트명**: 복슬퀀트
- **목적**: 다양한 퀀트 투자 전략의 성과를 분석하고 비교하는 Python 기반 백테스팅 시스템
- **주요 기능**: 일시투자 vs 적립식투자, 모멘텀 투자, 변동성 돌파 전략 분석 등

## 명령어
```bash
# 의존성 설치
pip install -r requirements.txt

# 실행 (현재 미완성)
python main.py
```


## 개발 노트
- 프로젝트는 초기 단계로 main.py에서 참조하는 대부분의 모듈이 아직 구현되지 않음
- 설정 시스템만 완성되어 있음
- 향후 모듈별 순차적 개발 필요

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
- 수량/평균단가: "#,##0.0000" 형식, 오른쪽 정렬
- 일반 숫자: 정규식 r'^-?\d+\.?\d*$'로 감지, 오른쪽 정렬
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
- Excel 파일: `results/{분석종류}/` 디렉토리에 저장
- 차트 파일: `results/{분석종류}/charts/` 디렉토리에 저장
- 파일명: `{분석종류}_{시작일}_{타임스탬프}` 형식 사용

### 🔧 코드 품질 표준
- 중복 코드 방지: 동일한 알고리즘은 하나의 모듈에서 관리
- 메서드 네이밍: 기능을 명확히 표현하는 이름 사용
- 에러 처리: try-except 블록으로 안전한 처리
- 타입 힌트: 함수 시그니처에 타입 명시

## 상세 문서 참조
개발 시 아래 문서들을 반드시 참조하세요:

- **프로젝트 구조**: `docs/project_structure.md` - 디렉토리 구조, 모듈별 역할, 기술 스택
- **기능 요구사항**: `docs/functional_requirements.md` - 핵심 기능, 사용자 시나리오, 확장 계획
- **TODO 리스트**: `docs/todo_list.md` - 개발 단계별 할일, 모듈별 상세 작업 항목

개발 작업 전에 해당 문서들을 읽고 요구사항을 파악한 후 진행하세요.