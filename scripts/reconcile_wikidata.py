"""Wikidata reconciliation: 통제어휘 개념의 Q번호 후보 수집.

사용법:  python scripts/reconcile_wikidata.py
입력:    vocab/concepts.csv (wikidata 컬럼이 비어 있는 개념만 대상)
출력:    output/wikidata_candidates.csv — 사람이 검수할 후보 목록

⚠️ 이 스크립트는 후보를 '제안'만 한다. 어떤 QID도 자동 확정하지 않는다.
   검수 후 accept 컬럼에 Y를 적고 apply_reconciliation.py를 실행할 것.
"""
import csv, json, time, urllib.error, urllib.parse, urllib.request
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
API = ("https://www.wikidata.org/w/api.php?action=wbsearchentities"
       "&format=json&language=ko&uselang=ko&type=item&limit=5&search=")
HEADERS = {"User-Agent": "gang-gamchan-lod/0.1 (personal research prototype; @pinakes_me)"}


def search(term, retries=4):
    url = API + urllib.parse.quote(term)
    req = urllib.request.Request(url, headers=HEADERS)
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=15) as r:
                return json.load(r).get("search", [])
        except urllib.error.HTTPError as e:
            # 2026-07-09 실측: 1초 간격에도 429가 무더기로 나옴 → 지수적 대기 후 재시도
            if e.code == 429 and attempt < retries:
                wait = int(e.headers.get("Retry-After") or 0) or 5 * (attempt + 1)
                time.sleep(wait)
                continue
            raise


def main():
    with open(BASE / "vocab/concepts.csv", encoding="utf-8") as f:
        vocab = [r for r in csv.DictReader(f)]
    targets = [r for r in vocab if r["category"] != "top" and not r["wikidata"]]
    print(f"대조 대상: {len(targets)}개 개념")

    out_rows = []
    for i, c in enumerate(targets, 1):
        label = c["pref_label_ko"]
        err = None
        try:
            results = search(label)
            # '관제·정치제도'처럼 복합 라벨은 첫 토큰으로 재시도
            if not results and "·" in label:
                results = search(label.split("·")[0])
        except Exception as e:
            print(f"  [{i}] {label}: 오류 — {e}")
            results, err = [], e
        if not results:
            # 오류는 '후보 없음'과 다르다 — 오류 행은 검수 대상이 아니라 재실행 대상
            out_rows.append({"concept_id": c["concept_id"], "label_ko": label,
                             "rank": "", "qid": "", "item_label": "",
                             "description": f"(오류: {err} — 재실행 필요)" if err else "(후보 없음)",
                             "accept": ""})
        for rank, r in enumerate(results, 1):
            out_rows.append({
                "concept_id": c["concept_id"], "label_ko": label, "rank": rank,
                "qid": r.get("id", ""), "item_label": r.get("label", ""),
                "description": r.get("description", ""), "accept": ""})
        print(f"  [{i}/{len(targets)}] {label}: 후보 {len(results)}건")
        time.sleep(1.5)  # Wikidata 예의범절 (1.0초로도 429 관측됨, 2026-07-09)

    out = BASE / "output/wikidata_candidates.csv"
    with open(out, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["concept_id", "label_ko", "rank", "qid",
                                          "item_label", "description", "accept"])
        w.writeheader(); w.writerows(out_rows)
    print(f"\n완료 → {out}")
    print("다음 단계: 파일을 열어 각 개념당 맞는 후보 한 줄에만 accept=Y 표기.")
    print("확신이 없으면 비워둘 것 — 틀린 링크가 빈 링크보다 나쁘다.")


if __name__ == "__main__":
    main()
