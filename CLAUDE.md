# CLAUDE.md — 강감찬 탐험 지도 (gang-gamchan-lod)

> Claude Code가 이 폴더를 열면 가장 먼저 읽는 파일.
> 프로젝트의 맥락, 원칙, 현재 상태를 담고 있다. (최종 갱신: 2026-07-09)

## 프로젝트 정체
관악구립도서관 강감찬자료실 도서목록 **전수 239건**을 SKOS 통제어휘(71개 개념) +
RDF/Turtle(2,586 트리플)로 변환하고, Leaflet+D3 단일 파일(index.html)로 시각화한
개인 연구 프로토타입.

- **공개 사이트**: https://pinakes-me.github.io/gang-gamchan/ (GitHub Pages, 배포 완료)
- **연구 프레임**: 공공도서관 향토자료실의 LOD 적용 가능성 연구 — 관악구 강감찬자료실 사례
- **작성자**: Hailey (@pinakes_me) — 사서, 한림대 디지털인문학 석사과정(2026.9~) 예정
- **청중 구분**: 사이트·README = 구민/방문자용(도서관 평가 표현 금지),
  NOTES.md = 연구자용(품질 발견·방법론 기록)

## 폴더 구조
```
index.html            공개 사이트 (단일 파일, GitHub Pages 진입점)
data/books.csv        도서 239건 (정제 + 주제 태깅 + 검수 플래그 + note)
vocab/concepts.csv    SKOS 통제어휘 71개 (wikidata 컬럼은 대조 후 채움)
schema/ontology.ttl   데이터 모델 + 도서관/장소 인스턴스(좌표·출처 주석)
scripts/              파이프라인 (아래 '명령' 참조)
output/               생성물: books.ttl, concepts.ttl, *_candidates.csv
images/               답사 사진 (예정 — DEPLOY.md 3절 참조)
README.md(방문자용) · NOTES.md(연구노트) · DEPLOY.md · RECONCILIATION.md
```

## 명령
```bash
# 데이터/어휘 수정 후 항상:
python3 scripts/csv_to_ttl.py && python3 scripts/build_site.py

# Reconciliation (후보 수집 → Hailey 검수 → 반영):
python3 scripts/reconcile_wikidata.py      # 개념 → Q번호 후보
python3 scripts/reconcile_nlk.py           # 도서 → ISBN 후보 (정보나루 인증키 필요)
python3 scripts/apply_reconciliation.py    # accept=Y 만 원본 반영
```
- build_site.py는 index.html의 CONCEPTS/BROADER/BOOKS 상수와 히어로 통계를 자동 주입
- **어휘에 없는 개념을 태깅하면 빌드가 의도적으로 실패함** (전거제어 강제)
- ⚠️ index.html을 손으로 고친 뒤에도 반드시 빌드를 다시 돌려 통계 동기화할 것
  (2026-07-06에 이걸 빼먹어 장소 카운트가 어긋난 전례 있음)

## 절대 원칙 — 어기지 말 것
1. **원천 목록 범위 준수**: 이 데이터셋의 연구 대상은 '목록이 특정 시점에 등재한 것'
   자체다. 실제 소장 현황이 다르다는 걸 알아도 CSV를 고치지 않는다 → NOTES.md에 기록만.
   (예: 181번 고려거란전기는 실제로는 소장돼 있으나 목록엔 '-' — 그대로 둠)
2. **검수 없는 확정 금지**: LLM 태깅·API 대조 결과는 전부 '후보'다. Hailey의 accept 없이
   원본에 반영하지 않는다. 애매하면 review_flag=Y.
3. **좌표·QID 추정 금지**: 확인된 출처(공공데이터, 직접 측정) 없이는 비워둔다.
   틀린 링크가 빈 링크보다 나쁘다.
4. **스크래핑 금지**: lib.gwanak.go.kr는 robots.txt로 자동 접근을 막음. 원천 데이터는
   Hailey가 브라우저에서 직접 복사한 것만 사용.
5. **자전거 접근성 프로젝트와 분리**: 데이터·좌표를 결합하지 말 것 (Hailey 결정, 2026-07-06).

## 표기 전거
- 강감찬 영문: **Gang Gamchan** (출처: 향토문화전자대전 grandculture.net) —
  Kang Kam-chan 등 이형은 v2에서 skos:altLabel 후보

## 현재 상태 (2026-07-07)
✅ 완료: 239건 전수 데이터화 / 어휘 71개(포화 확인) / RDF 2,586 트리플 /
공개 사이트 배포 / 검수 플래그 39건 식별 / reconciliation 도구 3종 /
방문자·연구자 문서 분리 / 도서관 게시판 피드백(참고목록 갱신 요청) 제출

## 다음 작업 (우선순위순)
1. **Neo4j 워크숍 준비·실습** (7/14–16 국중도) — NEO4J.md 참조,
   books.ttl+concepts.ttl을 n10s로 임포트
2. **DH2026 (7/27) 데모** — 3분 데모 스크립트 (미작성)
3. **답사** — 별 마커 5곳 사진 + 안국사 GPS 좌표 (Hailey, 일정 미정) → DEPLOY.md 3절대로 반영
4. **Reconciliation** — 2026-07-10 기준 상태:
   - Wikidata: ✅ **검수·반영·재빌드 완료**. 73개 대상 중 57개 채택(78.1%),
     vocab/concepts.csv에 QID 반영됨. 발견 기록은 NOTES.md 07-09/07-10 절
     (상서성 제외 사례 등).
   - 정보나루: keyword= 파라미터가 잡음(대출순 정렬)임을 발견, title= 기반으로 수정.
     **현재 output/isbn_candidates.csv는 keyword 기반 1차 결과라 폐기 대상 — 검수 금지.**
     일일 호출 한도(500회) 사유로 **재실행 필요** (아직 미실행). 상세는 NOTES.md 07-09 절.
     재실행 → 검수 → apply_reconciliation.py → csv_to_ttl.py → build_site.py
5. **검수 플래그 39건 해소** — 원자료·국중도 대조 (Hailey, 급하지 않음)
6. **논문목록 1,126건 확장 여부 결정** — 규모가 다르므로 샘플링 전략부터 논의
7. **논문 집필** — NOTES.md의 발견들이 뼈대: 품질 유형학(중복 8쌍·동음이의·전거 불일치·
   매체 오배치), 소장=강감찬 불변식, 2020년 정지 vs 실소장 진행, 어휘 포화 곡선,
   일괄구축 가설(도서관 확인 필요)

## 히스토리 요약
2026-07-06: 파이프라인 구축, 239건 완료, 사이트 제작·개선(구민용 전환, 10리길,
소장처 클릭, 사각형 노드). 07-07: 영문 전거 정정, 리포명 gang-gamchan 통일, 배포.
자세한 발견·정정 기록은 NOTES.md.
