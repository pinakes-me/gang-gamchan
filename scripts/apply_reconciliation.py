"""검수 완료(accept=Y) 후보를 원본 데이터에 반영.

사용법: python scripts/apply_reconciliation.py
  - output/wikidata_candidates.csv 의 accept=Y → vocab/concepts.csv wikidata 컬럼
  - output/isbn_candidates.csv 의 accept=Y → data/books.csv isbn 컬럼(신설)
안전장치: 한 개념/도서에 accept가 2줄 이상이면 중단.
반영 후 파이프라인 재실행 필요: python scripts/csv_to_ttl.py && python scripts/build_site.py
"""
import csv, sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent


def load(path):
    with open(path, encoding="utf-8") as f:
        r = csv.DictReader(f)
        return list(r), r.fieldnames


def accepted(path, key):
    rows, _ = load(path)
    chosen = {}
    for r in rows:
        if r["accept"].strip().upper() == "Y":
            if r[key] in chosen:
                sys.exit(f"중복 accept: {key}={r[key]} — 한 항목엔 하나만 Y로.")
            chosen[r[key]] = r
    return chosen


def main():
    changed = 0
    # 1. Wikidata → vocab
    wd_path = BASE / "output/wikidata_candidates.csv"
    if wd_path.exists():
        chosen = accepted(wd_path, "concept_id")
        vocab, fields = load(BASE / "vocab/concepts.csv")
        for row in vocab:
            c = chosen.get(row["concept_id"])
            if c and c["qid"]:
                row["wikidata"] = "http://www.wikidata.org/entity/" + c["qid"]
                changed += 1
        with open(BASE / "vocab/concepts.csv", "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(vocab)
        print(f"vocab: QID {len([1 for r in vocab if r['wikidata']])}개 보유 (이번에 +{changed})")

    # 2. ISBN → books
    isbn_path = BASE / "output/isbn_candidates.csv"
    if isbn_path.exists():
        chosen = accepted(isbn_path, "book_id")
        books, fields = load(BASE / "data/books.csv")
        if "isbn" not in fields:
            fields = list(fields) + ["isbn"]
        n = 0
        for row in books:
            row.setdefault("isbn", "")
            c = chosen.get(row["id"])
            if c and c["isbn13"]:
                row["isbn"] = c["isbn13"]; n += 1
        with open(BASE / "data/books.csv", "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(books)
        print(f"books: ISBN {n}건 반영")

    print("\n반영 완료. 파이프라인을 재실행하세요:")
    print("  python scripts/csv_to_ttl.py && python scripts/build_site.py")


if __name__ == "__main__":
    main()
