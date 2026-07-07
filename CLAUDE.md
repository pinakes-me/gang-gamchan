# CLAUDE.md — 강감찬자료실 LOD 파일럿

## 이 프로젝트가 뭔지
관악구립도서관 강감찬자료실(도서목록 239건, 논문목록 1,126건)을 SKOS 통제어휘 +
RDF/Turtle로 변환하고, Leaflet+D3 단일 파일로 시각화하는 연구 파일럿.
연구 프레임: "공공도서관 향토자료실의 LOD 적용 가능성 연구 — 관악구 강감찬자료실 사례"

## 원천 데이터 수집 방식 — 중요
lib.gwanak.go.kr 은 robots.txt로 자동 접근을 막아둠. **스크래핑 시도 금지.**
Hailey가 브라우저에서 페이지별 표를 직접 복사해 붙여넣으면, 그걸 `data/books.csv`에
정제해 append하는 것까지만 자동화 대상.

## 명령
```bash
python scripts/csv_to_ttl.py   # data/books.csv, vocab/concepts.csv → output/*.ttl 재생성
```
CSV나 어휘를 고칠 때마다 두 스크립트를 순서대로 실행:
```bash
python scripts/csv_to_ttl.py && python scripts/build_site.py
```
build_site.py가 index.html의 CONCEPTS/BROADER/BOOKS 상수와 히어로 통계를 자동 갱신함.
어휘에 없는 개념을 태깅하면 빌드가 실패하도록 되어 있음 (전거제어 강제).

## 통제어휘(vocab/concepts.csv) 규칙
- 새 개념은 **어휘에 먼저 추가**한 뒤 books.csv의 subjects 컬럼에서 참조 (전거제어 원칙)
- `wikidata` 컬럼은 절대 추정해서 채우지 말 것. Wikidata API(wbsearchentities)로
  대조한 결과만 채운다. 확신 없으면 비워둔다.
- broader 관계는 `vocab/concepts.csv`의 `broader` 컬럼과 `scripts/csv_to_ttl.py`의
  BROADER 로직 두 군데 다 반영되어야 함 (지금은 index.html에도 별도 BROADER 배열 있음 — 3중 동기화 지점, 주의)

## 태깅 원칙 — 반드시 지킬 것
LLM이 제목 문자열만 보고 주제를 초벌 태깅하는 건 괜찮지만, **Hailey의 검수 없이
review_flag 없는 상태로 커밋하지 말 것.** 이 프로젝트의 논지 자체가 "무검수 외주
목록화가 서지 데이터 품질을 떨어뜨린다"는 것이므로, 같은 실수를 파이프라인 안에서
반복하면 연구 전체의 신뢰도가 깎임. 애매하면 `review_flag=Y`로 표시하고 다음 검수
때 사람이 보게 할 것.

## 소장도서관(HOLDINGS) — 자전거 프로젝트와 별개
소장도서관 인스턴스에 좌표를 넣거나, 다른 접근성 프로젝트와 데이터를 결합하지 말 것.
Hailey가 두 프로젝트를 의도적으로 분리하기로 결정함 (2026-07-06).

## 다음 작업 우선순위
1. 도서목록 3페이지 이후 (20~239번) 계속 append
2. Wikidata reconciliation 스크립트 작성 (wbsearchentities 호출 → vocab wikidata 컬럼 채우기, 검수용 후보만 제시)
3. 논문목록(1,126건)은 도서목록 완료 후 별도 파이프라인으로 — 규모가 다르므로 샘플링 전략부터 논의
4. ~~자동 주입 스크립트~~ → scripts/build_site.py 구현 완료 (2026-07-06). csv_to_ttl.py 실행 후 build_site.py 실행
5. Neo4j 워크숍(7/14–16) 이후: neosemantics(n10s)로 books.ttl 임포트 실험

## Reconciliation 도구 (2026-07-07 구현 완료)
- scripts/reconcile_wikidata.py — 개념→Q번호 후보 수집 (Wikidata API)
- scripts/reconcile_nlk.py — 도서→ISBN 후보 수집 (정보나루 API, 인증키 필요)
- scripts/apply_reconciliation.py — 검수(accept=Y)된 후보만 원본 반영
- 상세: RECONCILIATION.md. **후보 자동 확정 금지 — Hailey 검수 필수** 원칙은
  이 도구들에도 그대로 적용됨.

## 배포 (2026-07-07)
- site.html → index.html 개명 (GitHub Pages 진입점)
- 배포 절차·사진 추가법: DEPLOY.md
