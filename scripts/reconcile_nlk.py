"""국내 서지 reconciliation: 도서관 정보나루 API로 ISBN 후보 수집.

사용법:
  1. data4library.kr 회원가입 → 마이페이지에서 인증키(authKey) 발급 (무료, 즉시)
  2. 아래 AUTH_KEY에 붙여넣기
  3. python scripts/reconcile_nlk.py

입력:  data/books.csv
출력:  output/isbn_candidates.csv — 사람이 검수할 후보 목록

⚠️ API 파라미터는 data4library.kr 공식 문서 기준으로 확인할 것 (변경 가능).
⚠️ 후보 '제안'만 한다 — 검수 후 accept=Y 표기 → apply_reconciliation.py 실행.
"""
import csv, json, time, urllib.parse, urllib.request
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
AUTH_KEY = "여기에_발급받은_인증키를_붙여넣기"
API = "http://data4library.kr/api/srchBooks?authKey={key}&keyword={q}&pageSize=5&format=json"


def search(title):
    url = API.format(key=AUTH_KEY, q=urllib.parse.quote(title))
    with urllib.request.urlopen(url, timeout=15) as r:
        data = json.load(r)
    docs = data.get("response", {}).get("docs", [])
    return [d.get("doc", d) for d in docs]


def main():
    if "붙여넣기" in AUTH_KEY:
        raise SystemExit("먼저 data4library.kr에서 인증키를 발급받아 AUTH_KEY에 넣어주세요.")
    with open(BASE / "data/books.csv", encoding="utf-8") as f:
        books = [r for r in csv.DictReader(f)]
    print(f"대조 대상: {len(books)}권")

    out_rows = []
    for i, b in enumerate(books, 1):
        # 부제 앞부분만으로 검색 (매칭률 향상)
        q = b["title"].split(":")[0].strip()
        try:
            docs = search(q)
        except Exception as e:
            print(f"  [{i}] {q}: 오류 — {e}")
            docs = []
        if not docs:
            out_rows.append({"book_id": b["id"], "title": b["title"], "creator": b["creator"],
                             "rank": "", "isbn13": "", "c_title": "", "c_author": "",
                             "c_publisher": "", "c_year": "", "accept": ""})
        for rank, d in enumerate(docs, 1):
            out_rows.append({
                "book_id": b["id"], "title": b["title"], "creator": b["creator"], "rank": rank,
                "isbn13": d.get("isbn13", ""), "c_title": d.get("bookname", ""),
                "c_author": d.get("authors", ""), "c_publisher": d.get("publisher", ""),
                "c_year": d.get("publication_year", ""), "accept": ""})
        if i % 20 == 0:
            print(f"  진행 {i}/{len(books)}")
        time.sleep(0.6)

    out = BASE / "output/isbn_candidates.csv"
    with open(out, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["book_id", "title", "creator", "rank", "isbn13",
                                          "c_title", "c_author", "c_publisher", "c_year", "accept"])
        w.writeheader(); w.writerows(out_rows)
    print(f"\n완료 → {out}")
    print("검수 요령: 저자·출판사·연도가 원목록과 일치하는 후보에만 accept=Y.")
    print("매칭 실패·불확실 건수 자체가 논문의 정량 데이터가 된다 — 기록해둘 것.")


if __name__ == "__main__":
    main()
