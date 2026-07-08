"""국내 서지 reconciliation: 도서관 정보나루 API로 ISBN 후보 수집.

사용법:
  1. data4library.kr 회원가입 → 로그인 → 마이페이지 → 인증키 관리에서
     인증키 신청 (즉시 발급, 무료, 기본 호출 한도 500회/일)
  2. 아래 AUTH_KEY에 붙여넣기
  3. python scripts/reconcile_nlk.py

입력:  data/books.csv
출력:  output/isbn_candidates.csv — 사람이 검수할 후보 목록

⚠️ 이 API는 XML로 응답한다 (2026-07-09 공식 문서 확인: data4library.kr/apiUtilization).
⚠️ 후보 '제안'만 한다 — 검수 후 accept=Y 표기 → apply_reconciliation.py 실행.
"""
import csv, time, urllib.parse, urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
AUTH_KEY = "여기에_발급받은_인증키를_붙여넣기"
API = "http://data4library.kr/api/srchBooks?authKey={key}&keyword={q}&pageSize=5"


def text(doc, tag):
    el = doc.find(tag)
    return el.text.strip() if el is not None and el.text else ""


def search(title):
    url = API.format(key=AUTH_KEY, q=urllib.parse.quote(title))
    with urllib.request.urlopen(url, timeout=15) as r:
        xml_bytes = r.read()
    root = ET.fromstring(xml_bytes)
    err = root.find(".//error")
    if err is not None:
        raise RuntimeError(f"API 오류: {ET.tostring(err, encoding='unicode')}")
    return root.findall(".//docs/doc")


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
                "isbn13": text(d, "isbn13"), "c_title": text(d, "bookname"),
                "c_author": text(d, "authors"), "c_publisher": text(d, "publisher"),
                "c_year": text(d, "publication_year"), "accept": ""})
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
