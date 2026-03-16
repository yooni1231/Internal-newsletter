"""
Zivid FAE 뉴스레터 크롤러
- 국내: 네이버 뉴스 API (전자신문, 로봇신문, AI타임스, 연합뉴스 등)
- 영문: Google News RSS (The Robot Report, Vision Systems Design 등)
- 카테고리: 3D카메라 / 비전소프트웨어 / 모션&빈피킹 / 국내로봇기업 /
           국내비전기업 / 응용분야(방산·용접 등) / 경쟁사동향
"""

import urllib.request
import urllib.parse
import urllib.error
import json
import os
import datetime
import time
import xml.etree.ElementTree as ET
import re

# ─────────────────────────────────────────────────────────────
#  인증키 설정

# ─────────────────────────────────────────────────────────────
NAVER_CLIENT_ID     = "qrjhv6MJOINvMhwI3srK"       
NAVER_CLIENT_SECRET = "Qef03RNTyy" 

# ─────────────────────────────────────────────────────────────
#  카테고리별 한국어 키워드 (네이버 뉴스 API)
# ─────────────────────────────────────────────────────────────
NAVER_QUERIES = {
    "3D카메라": [
        "산업용 3D 카메라",
        "구조광 카메라 로봇",
        "ToF 카메라 자동화",
        "포인트 클라우드 산업",
        "뎁스 카메라 제조",
    ],
    "비전소프트웨어": [
        "머신비전 소프트웨어 AI",
        "딥러닝 비전 결함 검출",
        "비전 AI 검사 자동화",
        "스마트팩토리 비전 솔루션",
        "비전 소프트웨어 로봇 자동화",
    ],
    "모션_빈피킹": [
        "bin picking 로봇 자동화",
        "빈피킹 3D 비전",
        "로봇 모션 제어 비전",
        "협동로봇 피킹 자동화",
        "6축 로봇 비전 피킹",
    ],
    "국내로봇기업": [
        "두산로보틱스 협동로봇",
        "한화로보틱스 신제품",
        "레인보우로보틱스 비전",
        "현대로보틱스 자동화",
        "뉴로메카 로봇 솔루션",
        "국내 협동로봇 시장",
    ],
    "국내비전기업": [
        "뷰웍스 머신비전",
        "국내 머신비전 기업",
        "비전 검사 시스템 국내",
        "스마트팩토리 비전 기업",
        "산업용 카메라 국내 시장",
    ],
    "응용분야": [
        "용접 자동화 3D 비전",
        "로봇 용접 비전 센서",
        "방산 자동화 무인화 로봇",
        "물류 자동화 비전 소터",
        "반도체 검사 3D 비전",
        "자동차 부품 비전 검사",
        "의료 로봇 3D 카메라",
        "디팔레타이징 자동화",
    ],
    "경쟁사동향": [
       
    ],
}

# ─────────────────────────────────────────────────────────────
#  카테고리별 영문 키워드 (Google News RSS)
# ─────────────────────────────────────────────────────────────
GOOGLE_NEWS_QUERIES = {
    "EN_3D_Camera": [
        "industrial 3D camera robot",
        "structured light camera automation",
        "depth camera bin picking",
        "point cloud robot grasping",
    ],
    "EN_Vision_Software": [
        "machine vision software AI inspection",
        "deep learning vision defect detection",
        "robot vision system industrial",
    ],
    "EN_Competitors": [
        "Zivid 3D camera"

    ],
    "EN_Applications": [
        "welding automation 3D vision",
        "logistics automation depth camera",
        "bin picking point cloud 2025",
        "depalletizing robot vision",
        "defense robotics vision sensor",
    ],
    "EN_Korean_Robotics": [
        "Doosan Robotics cobot",
        "Hyundai Robotics automation",
        "Rainbow Robotics new product",
    ],
}

EXCLUDED_SOURCES = [
    "automationworld.com",
    "automation world",
    "오토메이션월드",
]

def is_excluded(text: str) -> bool:
    """제외 매체 여부 확인"""
    text = text.lower()
    return any(src in text for src in EXCLUDED_SOURCES)


# ─────────────────────────────────────────────────────────────
#  신뢰도 높은 뉴스 출처 (참고용 - 실제 필터링에 사용 가능)
# ─────────────────────────────────────────────────────────────
TRUSTED_KO_SOURCES = [
    "전자신문", "로봇신문", "AI타임스", "연합뉴스", "한국경제",
    "디지털타임스", "머니투데이", "이데일리", "ZDNet Korea",
    "테크월드", "오토메이션월드"
]

TRUSTED_EN_SOURCES = [
    "The Robot Report", "Robotics Business Review", "Vision Systems Design",
    "Automation World", "Manufacturing.net", "IEEE Spectrum",
    "Control Engineering", "Industry Week"
]


# ─────────────────────────────────────────────────────────────
#  네이버 뉴스 API 호출
# ─────────────────────────────────────────────────────────────
def fetch_naver_news(query: str, display: int = 5) -> list:
    if NAVER_CLIENT_ID == "YOUR_NAVER_CLIENT_ID":
        return []

    enc_query = urllib.parse.quote(query)
    url = (
        f"https://openapi.naver.com/v1/search/news.json"
        f"?query={enc_query}&display={display}&sort=date"
    )

    req = urllib.request.Request(url)
    req.add_header("X-Naver-Client-Id", NAVER_CLIENT_ID)
    req.add_header("X-Naver-Client-Secret", NAVER_CLIENT_SECRET)

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        results = []
        for item in data.get("items", []):
            title = re.sub(r"<[^>]+>", "", item.get("title", ""))
            desc  = re.sub(r"<[^>]+>", "", item.get("description", ""))
            link  = item.get("originallink") or item.get("link")
            source = link.split("/")[2]

            # 🔴 AW 출처 제거
            if is_excluded(source):
                continue

            results.append({
                "title": title,
                "url": link,
                "source": source,
                "summary": desc,
                "pubDate": item.get("pubDate", ""),
                "lang": "ko",
            })
        return results

    except Exception as e:
        print(f"[ERROR] Naver API ({query}): {e}")
        return []

# ─────────────────────────────────────────────────────────────
#  Google News RSS 호출 (API 키 불필요)
# ─────────────────────────────────────────────────────────────
def fetch_google_news_rss(query: str, max_results: int = 5) -> list:
    enc_query = urllib.parse.quote(query)
    url = f"https://news.google.com/rss/search?q={enc_query}&hl=en-US&gl=US&ceid=US:en"

    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            raw = resp.read()

        root = ET.fromstring(raw)
        channel = root.find("channel")
        if channel is None:
            return []

        results = []
        for item in channel.findall("item")[:max_results]:
            title = item.findtext("title", "")
            link  = item.findtext("link", "")
            pub   = item.findtext("pubDate", "")
            desc  = re.sub(r"<[^>]+>", "", item.findtext("description", ""))

            # 🔴 AW 출처 제거
            if is_excluded(title) or is_excluded(desc):
                continue

            results.append({
                "title": title,
                "url": link,
                "source": "Google News RSS",
                "summary": desc[:200],
                "pubDate": pub,
                "lang": "en",
            })
        return results

    except Exception as e:
        print(f"[ERROR] Google RSS ({query}): {e}")
        return []
        
        
# ─────────────────────────────────────────────────────────────
#  전체 크롤링 실행
# ─────────────────────────────────────────────────────────────
def run_crawler():
    print("=" * 60)
    print("  Zivid FAE 뉴스레터 크롤러 시작")
    print(f"  수집 시각: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)

    collected = {}
    total = 0

    # ── 한국어 뉴스 (네이버 API) ──────────────────────────────
    print("\n[1/2] 네이버 뉴스 수집 중...")
    for category, queries in NAVER_QUERIES.items():
        collected[category] = []
        for q in queries:
            print(f"  → {category} | {q}")
            articles = fetch_naver_news(q, display=5)
            for a in articles:
                a["category"] = category
                a["keyword"]  = q
            collected[category].extend(articles)
            total += len(articles)
            time.sleep(0.2)   # API rate limit 방지

    # ── 영문 뉴스 (Google News RSS) ───────────────────────────
    print("\n[2/2] Google News RSS 수집 중 (영문)...")
    for category, queries in GOOGLE_NEWS_QUERIES.items():
        collected[category] = []
        for q in queries:
            print(f"  → {category} | {q}")
            articles = fetch_google_news_rss(q, max_results=4)
            for a in articles:
                a["category"] = category
                a["keyword"]  = q
            collected[category].extend(articles)
            total += len(articles)
            time.sleep(0.3)

    # ── 결과 저장 ──────────────────────────────────────────────
    output_dir  = os.path.dirname(os.path.abspath(__file__))
    today_str   = datetime.datetime.now().strftime("%Y%m%d")
    output_file = os.path.join(output_dir, f"news_data_{today_str}.json")

    payload = {
        "crawled_at":        datetime.datetime.now().isoformat(),
        "total_articles":    total,
        "trusted_ko_sources": TRUSTED_KO_SOURCES,
        "trusted_en_sources": TRUSTED_EN_SOURCES,
        "news":              collected,
    }

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 60)
    print(f"  수집 완료! 총 {total}건")
    print(f"  저장 경로: {output_file}")
    print("=" * 60)

    print("\n[카테고리별 수집 현황]")
    for cat, arts in collected.items():
        print(f"  {cat:35s}: {len(arts):>3}건")

    return output_file


# ─────────────────────────────────────────────────────────────
#  뉴스레터용 Markdown 리포트 생성
# ─────────────────────────────────────────────────────────────
def generate_markdown_report(json_file: str) -> str:
    """수집된 JSON → 뉴스레터 Markdown 변환"""
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    today = datetime.datetime.now().strftime("%Y년 %m월 %d일")
    lines = [
        f"# Zivid FAE 뉴스레터 — {today}\n",
        f"> 수집 기준: {data['crawled_at']} | 총 {data['total_articles']}건\n",
        "---\n",
    ]

    LABELS = {
        "3D카메라":        "📷 3D 카메라",
        "비전소프트웨어":   "💻 비전 소프트웨어",
        "모션_빈피킹":     "🦾 모션 & 빈피킹",
        "국내로봇기업":    "🤖 국내 로봇 기업",
        "국내비전기업":    "🏢 국내 비전 기업",
        "응용분야":        "🏭 응용 분야 (방산·용접 등)",
        "경쟁사동향":      "🔍 경쟁사 동향",
        "EN_3D_Camera":    "📷 [EN] 3D Camera",
        "EN_Vision_Software": "💻 [EN] Vision Software",
        "EN_Competitors":  "🔍 [EN] Competitors",
        "EN_Applications": "🏭 [EN] Applications",
        "EN_Korean_Robotics": "🤖 [EN] Korean Robotics",
    }

    for cat, articles in data["news"].items():
        label = LABELS.get(cat, cat)
        lines.append(f"\n## {label}\n")
        if not articles:
            lines.append("_수집된 기사 없음 (API 키 확인 필요)_\n")
            continue

        # 중복 URL 제거 후 최대 5건
        seen, unique = set(), []
        for a in articles:
            if a["url"] not in seen:
                seen.add(a["url"])
                unique.append(a)

        for a in unique[:5]:
            flag = "🇰🇷" if a.get("lang") == "ko" else "🇺🇸"
            lines.append(f"- {flag} **[{a['title']}]({a['url']})**  ")
            lines.append(f"  {a.get('summary','')[:120]}  ")
            lines.append(f"  `{a.get('pubDate','')[:16]}` | {a.get('source','')}\n")

    md_path = json_file.replace(".json", ".md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"\n[Markdown 리포트 저장]: {md_path}")
    return md_path


# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    json_path = run_crawler()
    generate_markdown_report(json_path)
