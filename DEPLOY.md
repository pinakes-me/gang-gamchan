# 배포 안내서 — GitHub Pages

## 0. 준비물
- GitHub 계정 (pinakes-me — 이미 있음 ✓)
- 이 폴더(gang-gamchan-lod) 전체

## 1. 리포지토리 만들기 (웹에서, 5분)
1. github.com 로그인 → 우상단 **+** → **New repository**
2. Repository name: `gang-gamchan` (추천 — URL이 짧아짐)
3. **Public** 선택 → **Create repository**
4. 생성된 페이지에서 **uploading an existing file** 링크 클릭
5. 이 폴더의 내용물 전체(폴더째가 아니라 안의 파일·폴더들)를 드래그해서 업로드
   - index.html, README.md, CLAUDE.md, DEPLOY.md, RECONCILIATION.md
   - data/, vocab/, schema/, scripts/, output/, images/
6. 하단 **Commit changes** 클릭

## 2. Pages 켜기 (2분)
1. 리포 상단 **Settings** → 왼쪽 메뉴 **Pages**
2. Source: **Deploy from a branch**
3. Branch: **main**, 폴더: **/ (root)** → **Save**
4. 1~2분 뒤 `https://pinakes-me.github.io/gang-gamchan/` 접속 → 완료 🎉

## 3. 사진 넣는 법 (답사 후)
1. **사진 준비**: 가로 1200px 이하로 리사이즈, 500KB 이하 권장
   (맥 미리보기: 도구 → 크기 조절). 파일명은 영문 소문자로:
   `nakseongdae-park.jpg`, `birthplace.jpg`, `statue.jpg`, `pagoda.jpg`, `exhibit.jpg`
2. **업로드**: 리포의 `images/` 폴더 → Add file → Upload files
3. **index.html 수정**: 리포에서 index.html 열기 → 연필(Edit) →
   `PLACES` 배열에서 해당 장소를 찾아 `photo` 필드 한 줄 추가:

   ```js
   {id:'p-park', name:'낙성대공원', lat:..., lng:..., kind:'star',
    photo:'images/nakseongdae-park.jpg',        // ← 이 줄 추가
    note:'강감찬 장군의 영정을 모신 사당 안국사가 있는 공원...', ...},
   ```
4. Commit → 1분 뒤 팝업에 사진이 뜸. 다섯 곳 반복.

### 안국사 GPS 좌표 반영법
답사에서 찍은 좌표(스마트폰 나침반/지도 앱에서 확인)를 받으면,
PLACES에 안국사 항목을 새로 추가하거나 낙성대공원 항목의 note를 수정.
좌표 출처는 "연구자 직접 측정(2026-07)"으로 온톨로지에도 기록할 것.

## 4. 데이터 갱신 워크플로 (나중에)
로컬에서 CSV·어휘 수정 →
```bash
python scripts/csv_to_ttl.py && python scripts/build_site.py
```
→ 바뀐 파일(index.html, data/, output/)을 리포에 다시 업로드(같은 경로에 올리면 덮어씀).

## 5. 확인 목록
- [ ] 사이트가 열리고 지도·그래프가 뜨는가 (폰에서도 확인)
- [ ] 도서관 마커 클릭 → 소장 자료 카드가 뜨는가
- [ ] 10리길 점선 클릭 → 코스 카드가 뜨는가
- [ ] 푸터의 고지문이 보이는가
