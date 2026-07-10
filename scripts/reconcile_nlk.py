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
import csv, re, time, urllib.parse, urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
AUTH_KEY = "ef9aae7db6427e2689574702dc184455cd8c438628846ff87febc06c91a7713d"
# keyword= 는 느슨한 검색을 대출순으로 정렬해 무관한 베스트셀러가 나옴 (2026-07-09 실측:
# '고려시대 대간제도 연구' → 9,652건, 1위 데미안). title= 은 서명 부분일치라 정확함.
API = "http://data4library.kr/api/srchBooks?authKey={key}&title={q}&pageSize=5"


def text(doc, tag):
    el = doc.find(tag)
    return el.text.strip() if el is not None and el.text else ""


def search(title):
    url = API.format(key=AUTH_KEY, q=urllib.parse.quote(title))
    with urllib.request.urlopen(url, timeout=15) as r:
        xml_bytes = r.read()
    # 정상 응답은 XML이지만 오류(미활성 키 등)는 JSON으로 온다 (2026-07-09 실측)
    if xml_bytes.lstrip().startswith(b"{"):
        raise RuntimeError(f"API 오류 응답: {xml_bytes.decode('utf-8', 'replace')}")
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
        # 부제 앞부분만 사용. '[전자책]' 같은 매체 표기는 제거 —
        # 대괄호가 검색어에 들어가면 API가 빈 응답을 반환함 (2026-07-09 실측)
        q = re.sub(r"\[[^\]]*\]", " ", b["title"].split(":")[0]).strip()
        # 서명 부분일치는 띄어쓰기·접두어 차이에 약하므로, 0건이면 어절을 줄여 재시도:
        # 전체 → 첫 어절 제거(시대명 등) → 끝 어절 제거('연구' 등) → 가운데 어절만
        # 문장부호만 있는 토큰('-' 등)은 제거 — 남겨두면 축소된 쿼리가 문장부호로
        # 끝나 API가 빈 응답을 내는 경우가 있음 (2026-07-10 실측: '... - 고려편')
        words = [w for w in q.split() if re.search(r"[가-힣A-Za-z0-9]", w)]
        attempts = [q]
        if len(words) >= 2:
            attempts += [" ".join(words[1:]), " ".join(words[:-1])]
        if len(words) >= 3:
            attempts.append(" ".join(words[1:-1]))
        docs = []
        for attempt in attempts:
            try:
                docs = search(attempt)
            except Exception as e:
                print(f"  [{i}] {attempt}: 오류 — {e}")
                docs = []
            if docs:
                break
            time.sleep(0.6)
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
