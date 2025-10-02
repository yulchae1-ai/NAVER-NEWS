# Naver Popular News Scraper (Sections → JSON)

학습/연구용: 네이버 많이 본 뉴스(일간)에서 섹션별 상위 기사 URL + 본문을 수집해 JSON/CSV로 저장합니다.

## 사용법
```bash
pip install requests beautifulsoup4 lxml

# 오늘 기준 (config.json의 date: "today")
python scrape_naver_popular.py

# 특정 날짜
python scrape_naver_popular.py --date 20251002 --top-k 3
```
출력: outputs/all_sections.json, outputs/politics.json 등, outputs/all_sections.csv
