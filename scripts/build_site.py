"""CSV → index.html 데이터 자동 주입.

data/books.csv, vocab/concepts.csv 를 읽어 index.html 안의
CONCEPTS / BROADER / BOOKS 상수와 히어로 통계를 재생성한다.
사용법: python scripts/csv_to_ttl.py && python scripts/build_site.py
"""
import csv, json, re, sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE / "scripts"))
from csv_to_ttl import build_books, build_concepts  # 트리플 수 계산용

CAT_MAP = {  # vocab 범주 → site 색상 범주
    "person": "person", "event": "event", "place": "place",
    "institution": "inst", "work": "work", "material_culture": "work",
    "genre": "schol", "scholarship": "schol", "period": "period",
}
RELATED = [("nakseongdae", "gangamchan")]  # skos:related 성격의 추가 연결
ALWAYS_INCLUDE = {"nakseongdae"}           # 태깅 0건이어도 지도-그래프 다리로 유지


def load():
    with open(BASE / "vocab/concepts.csv", encoding="utf-8") as f:
        vocab = [r for r in csv.DictReader(f)]
    with open(BASE / "data/books.csv", encoding="utf-8") as f:
        books = [r for r in csv.DictReader(f)]
    return vocab, books


def main():
    vocab, books = load()
    concepts = {r["concept_id"]: r for r in vocab if r["category"] != "top"}

    count = {}
    for b in books:
        for s in filter(None, b["subjects"].split(";")):
            s = s.strip()
            if s not in concepts:
                sys.exit(f"어휘에 없는 개념 태그: '{s}' (도서 {b['id']}) — 전거제어 원칙 위반")
            count[s] = count.get(s, 0) + 1

    # 포함 규칙: 태깅 1건 이상 + broader 폐포 + 예외 목록
    include = {c for c in concepts if count.get(c, 0) > 0} | ALWAYS_INCLUDE
    changed = True
    while changed:
        changed = False
        for c in list(include):
            br = concepts[c]["broader"]
            if br in concepts and br not in include:
                include.add(br); changed = True

    js_concepts = []
    for cid in concepts:
        if cid not in include: continue
        c = concepts[cid]
        e = {"id": cid, "ko": c["pref_label_ko"], "cat": CAT_MAP[c["category"]]}
        if cid == "goryeo": e["hub"] = True
        js_concepts.append(e)

    broader = [[c["concept_id"], c["broader"]] for c in vocab
               if c["concept_id"] in include and c["broader"] in include]
    broader += [list(p) for p in RELATED if p[0] in include and p[1] in include]

    js_books = []
    for b in books:
        e = {"id": int(b["id"]), "t": b["title"], "a": b["creator"],
             "p": b["publisher"], "y": int(b["year"]),
             "s": [s.strip() for s in b["subjects"].split(";") if s.strip()]}
        if b["series_note"]: e["sr"] = b["series_note"]
        if b["volume_note"]: e.setdefault("sr", "")  # 표시엔 sr만 사용
        if b["holdings"]: e["held"] = [h.strip() for h in b["holdings"].split(";")]
        if b["review_flag"] == "Y": e["review"] = b["note"]
        js_books.append(e)

    triples = len(build_books()) + len(build_concepts())

    def js(obj): return json.dumps(obj, ensure_ascii=False, indent=1)

    html = (BASE / "index.html").read_text(encoding="utf-8")
    html = re.sub(r"const CONCEPTS = \[[\s\S]*?\n\];",
                  f"const CONCEPTS = {js(js_concepts)};", html)
    html = re.sub(r"const BROADER = \[[\s\S]*?\n\];",
                  f"const BROADER = {js(broader)};", html)
    html = re.sub(r"const BOOKS = \[[\s\S]*?\n\];",
                  f"const BOOKS = {js(js_books)};", html)
    html = re.sub(r'(<b id="st-books">)\d+', rf"\g<1>{len(js_books)}", html)
    html = re.sub(r'(<b id="st-concepts">)\d+', rf"\g<1>{len(js_concepts)}", html)
    html = re.sub(r'(<b id="st-triples">)\d+', rf"\g<1>{triples}", html)
    places = len(re.findall(r"\{id:'p-", html))
    html = re.sub(r'(<b id="st-places">)\d+', rf"\g<1>{places}", html)
    (BASE / "index.html").write_text(html, encoding="utf-8")
    print(f"index.html 갱신: 자료 {len(js_books)} · 개념 {len(js_concepts)} · 트리플 {triples} · 장소 {places}")


if __name__ == "__main__":
    main()
