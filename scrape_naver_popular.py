#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse, csv, datetime as dt, json, re, time
from pathlib import Path
from typing import Dict, List, Any, Tuple
import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent
OUT  = ROOT / "outputs"

def load_config():
    return json.loads((ROOT/"config.json").read_text(encoding="utf-8"))

def resolve_date(date_str: str) -> str:
    if date_str.lower() == "today":
        return dt.datetime.now().strftime("%Y%m%d")
    if not re.fullmatch(r"\d{8}", date_str):
        raise ValueError("date must be 'today' or 'YYYYMMDD'")
    return date_str

def popular_url(date_yyyymmdd: str, sid1: int) -> str:
    return f"https://news.naver.com/main/ranking/popularDay.naver?date={date_yyyymmdd}&sid1={sid1}"

def get_soup(url: str, headers: Dict[str, str]) -> BeautifulSoup:
    res = requests.get(url, headers=headers, timeout=15)
    res.raise_for_status()
    return BeautifulSoup(res.text, "lxml")

def extract_article_links_from_popular(soup: BeautifulSoup) -> List[str]:
    links = set()
    for a in soup.select("a"):
        href = a.get("href") or ""
        if not href:
            continue
        if "/read.naver" in href or "/mnews/article/" in href:
            if href.startswith("http"):
                links.add(href)
            else:
                links.add("https://news.naver.com" + href)
    return list(links)

def extract_title_and_body(url: str, headers: Dict[str, str]) -> Tuple[str, str]:
    try:
        s = get_soup(url, headers)
    except Exception:
        return "", ""
    title = ""
    for sel in ["h2#title_area", ".media_end_head_headline", "h1#title_area", "h1.end_tit", "title"]:
        el = s.select_one(sel)
        if el and el.get_text(strip=True):
            title = el.get_text(" ", strip=True)
            break
    if not title:
        title = s.title.get_text(strip=True) if s.title else ""
    body = ""
    for sel in ["div#dic_area", "div#articeBody", "div#articleBodyContents", "article#newsct_article"]:
        el = s.select_one(sel)
        if el and el.get_text(strip=True):
            body = el.get_text(" ", strip=True)
            break
    return title, body

def scrape_section(name: str, sid1: int, date_yyyymmdd: str, headers: Dict[str, str], top_k: int, delay: float):
    url = popular_url(date_yyyymmdd, sid1)
    soup = get_soup(url, headers)
    links = extract_article_links_from_popular(soup)
    items = []
    for href in links[:max(top_k*3, top_k)]:
        time.sleep(delay)
        t, b = extract_title_and_body(href, headers)
        if not t or not b:
            continue
        items.append({"date": date_yyyymmdd, "section": name, "url": href, "title": t, "content": b})
        if len(items) >= top_k:
            break
    return items

def save_json(path: Path, data: Any):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def save_csv(path: Path, rows: List[Dict[str, Any]]):
    cols = ["date","section","title","url","content"]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in cols})

def main():
    cfg = load_config()
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=cfg.get("date","today"))
    ap.add_argument("--top-k", type=int, default=cfg.get("top_k",3))
    args = ap.parse_args()

    date_yyyymmdd = resolve_date(args.date)
    top_k = args.top_k
    headers = {"User-Agent": cfg["user_agent"]}
    delay = float(cfg.get("request_delay_sec", 0.8))
    sections = cfg["sections"]

    OUT.mkdir(parents=True, exist_ok=True)

    all_rows = []
    for name, sid in sections.items():
        print(f"[INFO] {name} (sid1={sid}) {date_yyyymmdd}")
        try:
            rows = scrape_section(name, sid, date_yyyymmdd, headers, top_k, delay)
        except Exception as e:
            print(f"[WARN] {name} failed: {e}")
            rows = []
        all_rows.extend(rows)
        save_json(OUT / f"{name}.json", rows)
        print(f"  -> outputs/{name}.json  ({len(rows)} items)")

    save_json(OUT / "all_sections.json", all_rows)
    save_csv(OUT / "all_sections.csv", all_rows)
    print("[DONE] outputs/all_sections.json, outputs/all_sections.csv")
    print("Hero image: assets/tiger.jpg")

if __name__ == "__main__":
    main()
