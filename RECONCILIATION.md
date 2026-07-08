# Reconciliation 가이드 — OpenRefine 없이 하기

Reconciliation(대조)은 우리 데이터의 문자열("강감찬", "고려청자")을
외부 지식베이스의 식별자(Wikidata Q번호, ISBN)와 연결하는 작업.
이게 끝나면 이 프로젝트가 진짜 "**Linked**" Open Data가 된다.

## 준비 (한 번만)
- Python 3 설치 확인: 터미널에서 `python3 --version`
- 이 폴더에서 실행한다는 가정 (`cd gang-gamchan-lod`)
- 표준 라이브러리만 사용 — 별도 pip 설치 불필요

## 1단계 — Wikidata (개념 71개, 약 2분 소요)
```bash
python3 scripts/reconcile_wikidata.py
```
→ `output/wikidata_candidates.csv` 생성. 개념당 최대 5개 후보가 나온다.

**검수 방법** (엑셀/Numbers로 열기):
- 각 개념(concept_id)당 맞는 후보 **한 줄에만** accept 컬럼에 `Y`
- description을 보고 판단: '강감찬' → "고려의 장군"이 맞고 동명 야구선수는 아님
- **확신 없으면 비워둔다.** 틀린 링크가 빈 링크보다 나쁘다.
- 후보가 다 틀리면 전부 비워두고, 필요하면 wikidata.org에서 직접 검색해
  vocab/concepts.csv에 URI를 수기 입력해도 됨

## 2단계 — ISBN (도서 239권, 약 3분 소요)

**인증키 발급** (5분, 최초 1회):
1. **data4library.kr** 접속 → 우상단 **회원가입** → **로그인**
2. **마이페이지 → 인증키 관리** → **인증키 신청** (즉시 발급, 무료)
3. 기본 호출 한도는 하루 500회 — 우리는 239건이라 충분함(서버IP 등록 불필요)

**실행**:
1. `scripts/reconcile_nlk.py` 를 열어 `AUTH_KEY = "..."` 에 발급받은 키 붙여넣기
2. ```bash
   python3 scripts/reconcile_nlk.py
   ```
→ `output/isbn_candidates.csv` 생성.
(API는 XML로 응답함 — 공식 문서 data4library.kr/apiUtilization 2026-07-09 확인,
스크립트에 이미 반영되어 있음)

**검수 방법**: 저자·출판사·연도가 원목록과 일치하는 후보에만 `Y`.
- 지역 출판물·오래된 책은 매칭이 안 될 수 있음 — 정상이며,
  **매칭률 수치 자체가 논문의 결과 데이터**이니 실패 건수를 기록해둘 것
- 중복 등재 쌍(고려도경 22·23·235 등)은 같은 ISBN이 나올 수 있음 —
  그 자체가 중복의 증거

## 3단계 — 반영
```bash
python3 scripts/apply_reconciliation.py
python3 scripts/csv_to_ttl.py && python3 scripts/build_site.py
```
- vocab의 wikidata 컬럼 → RDF에서 `owl:sameAs`로 자동 출력
- books의 isbn 컬럼 → RDF에서 `schema:isbn`으로 자동 출력
- 한 항목에 accept가 2줄이면 스크립트가 멈춤 (안전장치)

## 검수 원칙 (이 프로젝트의 헌법)
1. 스크립트는 후보를 제안할 뿐, 확정은 항상 사람(사서)이 한다
2. 확신 없으면 비워둔다
3. 실패와 공백도 데이터다 — 지우지 말고 기록한다

## 주의
- 두 API 모두 파라미터가 바뀔 수 있음 — 오류가 나면 각 사이트의
  최신 문서(wikidata.org/w/api.php, data4library.kr)와 대조할 것
- Wikidata 호출엔 1초 간격을 두었음(예의범절) — 임의로 줄이지 말 것
