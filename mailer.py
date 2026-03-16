import os
import sys
import json
import smtplib
import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.header import Header
from dotenv import load_dotenv
load_dotenv()
# ──────────────────────────────────────
#  SMTP 설정 
# ──────────────────────────────────────
SMTP_HOST  = "smtp.naver.com"
SMTP_PORT  = 465
SMTP_USER  = "yunseo1231@naver.com"
SMTP_PASS  = os.getenv("SMTP_PASS") 
FROM_EMAIL = SMTP_USER
TO_EMAILS  = [
    "yunseo.lee@zivid.com",
  
]
 # "bh.choi@zivid.com",
  #  "gyeonje.cho@zivid.com",
BASE_DIR      = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.join(BASE_DIR, "index_email.html")
LOGO_PATH     = os.path.join(BASE_DIR, "ZividLogo(white)_small.png")

# ──────────────────────────────────────
#  카테고리 한글 레이블
# ──────────────────────────────────────
CATEGORY_LABELS = {
    "3D카메라":           "📷 3D 카메라",
    "비전소프트웨어":      "💻 비전 소프트웨어",
    "모션_빈피킹":        "🦾 모션 &amp; 빈피킹",
    "국내로봇기업":       "🤖 국내 로봇 기업",
    "국내비전기업":       "🏢 국내 비전 기업",
    "응용분야":           "🏭 응용 분야",
    "경쟁사동향":         "🔍 경쟁사 동향",
    "EN_3D_Camera":       "📷 [EN] 3D Camera",
    "EN_Vision_Software": "💻 [EN] Vision Software",
    "EN_Competitors":     "🔍 [EN] Competitors",
    "EN_Applications":    "🏭 [EN] Applications",
    "EN_Korean_Robotics": "🤖 [EN] Korean Robotics",
}

# ──────────────────────────────────────
#  JSON 로딩
# ──────────────────────────────────────
def load_json():
    today    = datetime.date.today()
    date_str = today.strftime("%Y%m%d")
    for path in [
        os.path.join(BASE_DIR, f"news_data_{date_str}.json"),
        os.path.join(BASE_DIR, "news_data.json"),
    ]:
        if os.path.exists(path):
            print(f"[INFO] JSON 로딩: {path}")
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    raise FileNotFoundError("JSON 파일을 찾을 수 없습니다.")

# ──────────────────────────────────────
#  날짜 포맷
# ──────────────────────────────────────
def fmt_date(dstr):
    if not dstr:
        return ""
    for fmt in ("%a, %d %b %Y %H:%M:%S %z",
                "%a, %d %b %Y %H:%M:%S %Z",
                "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.datetime.strptime(dstr, fmt).strftime("%m/%d")
        except Exception:
            continue
    return dstr[:10]

# ──────────────────────────────────────
#  TOP NEWS 카드
# ──────────────────────────────────────
def build_top_news(all_articles):
    html = ""
    for a in all_articles[:3]:
        title  = a.get("title", "")
        url    = a.get("url", "#")
        source = a.get("source", "")
        pub    = fmt_date(a.get("pubDate", ""))
        flag   = "🇰🇷" if a.get("lang") == "ko" else "🇺🇸"
        html += f"""
<table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-bottom:12px;">
  <tr>
    <td style="background-color:#1A1A1A;border:1px solid #2A2A2A;
               border-left:4px solid #E8271A;padding:20px;">
      <p style="margin:0 0 8px;font-family:'Apple SD Gothic Neo','Malgun Gothic','맑은 고딕',Arial,sans-serif;
                font-size:14px;font-weight:600;line-height:1.4;">
        <a href="{url}" target="_blank" style="color:#F5F5F0;text-decoration:none;">{flag} {title}</a>
      </p>
      <p style="margin:0;font-family:'DM Mono','Courier New',monospace;
                font-size:11px;color:#A0A0A0;">
        {pub} &nbsp;·&nbsp; {source}
      </p>
    </td>
  </tr>
</table>"""
    return html

# ──────────────────────────────────────
#  카테고리 블록
# ──────────────────────────────────────
def build_category_blocks(news_dict):
    html = ""
    for cat, items in news_dict.items():
        if not items:
            continue
        seen, unique = set(), []
        for a in items:
            if a["url"] not in seen:
                seen.add(a["url"])
                unique.append(a)
        unique = unique[:3]
        label = CATEGORY_LABELS.get(cat, cat)
        html += f"""
<table width="100%" cellpadding="0" cellspacing="0" border="0"
       style="margin-top:40px;margin-bottom:14px;">
  <tr>
    <td style="border-bottom:1px solid #2A2A2A;padding-bottom:12px;">
      <span style="font-family:'DM Serif Display',Georgia,serif;
                   font-size:20px;color:#F5F5F0;">{label}</span>
    </td>
  </tr>
</table>"""
        for a in unique:
            title   = a.get("title", "")
            url     = a.get("url", "#")
            summary = a.get("summary", "")[:120]
            source  = a.get("source", "")
            pub     = fmt_date(a.get("pubDate", ""))
            flag    = "🇰🇷" if a.get("lang") == "ko" else "🇺🇸"
            html += f"""
<table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-bottom:8px;">
  <tr>
    <td style="background-color:#1A1A1A;border:1px solid #2A2A2A;padding:18px;">
      <p style="margin:0 0 6px;font-family:'Apple SD Gothic Neo','Malgun Gothic','맑은 고딕',Arial,sans-serif;
                font-size:14px;font-weight:600;line-height:1.4;">
        <a href="{url}" target="_blank" style="color:#F5F5F0;text-decoration:none;">{flag} {title}</a>
      </p>
      <p style="margin:0 0 6px;font-family:'Apple SD Gothic Neo','Malgun Gothic','맑은 고딕',Arial,sans-serif;
                font-size:12px;color:#A0A0A0;line-height:1.5;">{summary}</p>
      <p style="margin:0;font-family:'DM Mono','Courier New',monospace;
                font-size:11px;color:#606060;">
        {pub} &nbsp;·&nbsp; {source}
      </p>
    </td>
  </tr>
</table>"""
    return html

# ──────────────────────────────────────
#  템플릿 치환
# ──────────────────────────────────────
def build_final_html(data):
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        tmpl = f.read()
    news_dict    = data["news"]
    all_articles = [x for lst in news_dict.values() for x in lst]
    crawled_at   = data.get("crawled_at", "")
    try:
        dt = datetime.datetime.fromisoformat(crawled_at.split(".")[0])
        crawled_at = dt.strftime("%Y-%m-%d %H:%M")
    except Exception:
        pass
    html = tmpl
    html = html.replace("[TOP_NEWS]",        build_top_news(all_articles))
    html = html.replace("[CATEGORY_BLOCKS]", build_category_blocks(news_dict))
    html = html.replace("[TOTAL_COUNT]",     str(data.get("total_articles", 0)))
    html = html.replace("[GENERATED_AT]",    crawled_at)

    if os.path.exists(LOGO_PATH):
        import base64, mimetypes
        mime_type = mimetypes.guess_type(LOGO_PATH)[0] or "image/png"
        with open(LOGO_PATH, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")
        data_uri = f"data:{mime_type};base64,{b64}"
        html = html.replace("cid:zivid_logo", data_uri)

    return html

# ──────────────────────────────────────
#  이메일 발송
# ──────────────────────────────────────
def send_email(html_content):
    if not SMTP_PASS:
        print("[ERROR] SMTP_PASS 환경변수가 설정되지 않았습니다.")
        return

    msg = MIMEMultipart("mixed")
    subject_str = f"Zivid Korea Newsletter — {datetime.date.today()}"
    import base64 as _b64
    msg["Subject"] = "=?utf-8?B?" + _b64.b64encode(subject_str.encode("utf-8")).decode() + "?="
    msg["From"] = FROM_EMAIL
    msg["To"]   = FROM_EMAIL  # 수신자는 sendmail()로 개별 처리

    related = MIMEMultipart("related")
    msg.attach(related)

    alt = MIMEMultipart("alternative")
    related.attach(alt)
    alt.attach(MIMEText(html_content, "html", "utf-8"))

    # 로고는 build_final_html()에서 Base64로 HTML에 직접 임베딩됨

    print("[INFO] SMTP 전송 중 (네이버 SSL)...")
    try:
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as srv:
            srv.login(SMTP_USER, SMTP_PASS)
            srv.sendmail(FROM_EMAIL, TO_EMAILS, msg.as_string())
        print("[SUCCESS] 발송 완료!")
    except Exception as e:
        print(f"[ERROR] 발송 실패: {e}")

# ──────────────────────────────────────
#  MAIN
# ──────────────────────────────────────
def main():
    dry = "--dry-run" in sys.argv
    try:
        data = load_json()
        html = build_final_html(data)

        preview = os.path.join(BASE_DIR, "mailer_preview.html")
        with open(preview, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"[INFO] 미리보기: {preview}")

        if dry:
            print("[INFO] DRY RUN — 발송 생략")
            return
        send_email(html)
    except Exception as e:
        print(f"[CRITICAL] {e}")
        raise

if __name__ == "__main__":
    main()