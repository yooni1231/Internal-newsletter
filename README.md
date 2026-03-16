# 📰 Zivid Korea Newsletter

Zivid Korea팀을 위한 **자동 뉴스 크롤링 & 이메일 발송 시스템**입니다.  
매주 월요일 오전 9시, 국내외 3D 비전 / 로봇 자동화 관련 뉴스를 수집하여 HTML 이메일로 자동 발송합니다.

---

## 📁 프로젝트 구조

```
automation/
├── crawler.py                  # 네이버 뉴스 API + Google News RSS 크롤러
├── mailer.py                   # HTML 이메일 빌더 & 발송
├── index_email.html            # 이메일 HTML 템플릿
├── ZividLogo(white)_small.png  # 헤더 로고 이미지
├── .env                        # 환경변수 (Git 제외)
├── .gitignore
├── run.bat                     # 크롤러 + 메일러 일괄 실행 (Windows)
└── news_data_YYYYMMDD.json     # 크롤링 결과 (자동 생성, Git 제외)
```

---

## ⚙️ 설치 방법

### 1. 레포지터리 클론

```bash
git clone https://github.com/본인아이디/zivid-newsletter.git
cd zivid-newsletter/automation
```
> 네이버 앱 비밀번호 발급:  
> 네이버 메일 → 환경설정 → POP3/SMTP 설정 → SMTP 사용 설정  
> → [네이버 보안설정](https://nid.naver.com/user2/help/myInfoV2) → 2단계 인증 → 앱 비밀번호 발급

---

## 🚀 실행 방법

### 수동 실행

```bash
# 1. 크롤링 먼저
python crawler.py

# 2. 이메일 발송
python mailer.py

# 발송 없이 미리보기만 (mailer_preview.html 생성)
python mailer.py --dry-run
```

### 일괄 실행 (run.bat)

```bat
cd /d C:\valentine\newsletter\automation
python crawler.py
python mailer.py
```

---

## 📂 뉴스 카테고리

### 🇰🇷 국내 (네이버 뉴스 API)

| 카테고리 | 설명 |
|----------|------|
| 📷 3D 카메라 | 산업용 3D 카메라, ToF, 구조광, 포인트 클라우드 |
| 💻 비전 소프트웨어 | 머신비전 AI, 딥러닝 검사, 스마트팩토리 |
| 🦾 모션 & 빈피킹 | 빈피킹, 협동로봇 피킹, 6축 로봇 비전 |
| 🤖 국내 로봇 기업 | 두산로보틱스, 한화로보틱스, 레인보우로보틱스 등 |
| 🏢 국내 비전 기업 | 뷰웍스, 국내 머신비전 시장 |
| 🏭 응용 분야 | 용접, 방산, 물류, 반도체, 의료 자동화 |
| 🔍 경쟁사 동향 | 

### 🇺🇸 영문 (Google News RSS)

| 카테고리 | 설명 |
|----------|------|
| 📷 3D Camera | Industrial 3D camera, structured light |
| 💻 Vision Software | Machine vision AI, defect detection |
| 🔍 Competitors | 
| 🏭 Applications | Welding, logistics, bin picking, depalletizing |
| 🤖 Korean Robotics | Doosan, Hyundai, Rainbow Robotics |

---

## 🛠️ 주요 파일 설명

### `crawler.py`
- 네이버 뉴스 API로 한국어 뉴스 수집
- Google News RSS로 영문 뉴스 수집
- 결과를 `news_data_YYYYMMDD.json` 으로 저장

### `mailer.py`
- JSON 데이터를 읽어 HTML 이메일 생성
- 로고를 Base64로 인라인 임베딩 (Gmail/Outlook 호환)
- 네이버 SMTP SSL(465)로 발송
- `--dry-run` 옵션으로 발송 없이 미리보기 생성 가능

### `index_email.html`
- 이메일 전용 HTML 템플릿
- `display:grid/flex` 없이 순수 `<table>` 레이아웃 (Outlook 호환)
- 모든 스타일 인라인 적용 (Gmail `<head>` strip 대응)
- 플레이스홀더: `[TOP_NEWS]`, `[CATEGORY_BLOCKS]`, `[TOTAL_COUNT]`, `[GENERATED_AT]`

---

## 🔐 보안

`.gitignore` 에 아래 항목이 포함되어 있어 민감 정보는 Git에 올라가지 않습니다:

```
.env
*.json
mailer_preview.html
__pycache__/
*.md
```

---

## 📋 API 키 설정

### 네이버 뉴스 API
`crawler.py` 상단에서 직접 설정:
```python
NAVER_CLIENT_ID     = "your_client_id"
NAVER_CLIENT_SECRET = "your_client_secret"
```
> 발급: [네이버 개발자센터](https://developers.naver.com) → 애플리케이션 등록 → 뉴스 검색 API

---

## 📧 문의

**Zivid Korea Team**  
yunseo.lee@zivid.com
