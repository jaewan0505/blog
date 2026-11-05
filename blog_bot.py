import os  #
import feedparser
import requests
from openai import OpenAI

# 1. 설정 정보 입력
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# OpenAI 클라이언트 설정
client = OpenAI(api_key=OPENAI_API_KEY)

def send_telegram_photo(token, chat_id, photo_url, caption):
    url = f"https://api.telegram.org/bot{token}/sendPhoto"
    payload = {
        "chat_id": chat_id,
        "photo": photo_url,
        "caption": caption[:1024],  # 텔레그램 사진 캡션 최대 길이 제한 (1024자)
        "parse_mode": "Markdown"
    }
    requests.post(url, data=payload)

def send_telegram_message(text):
    """텔레그램으로 메시지를 전송하는 함수"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.get(url, params={"chat_id": CHAT_ID, "text": text})

def get_latest_blog_post(blog_rss_url):
    """블로그 RSS에서 가장 최근에 올라온 글 제목과 본문을 가져옴"""
    feed = feedparser.parse(blog_rss_url)
    if not feed.entries:
        return None, None
    
    latest_post = feed.entries[0]
    return latest_post.title, latest_post.description

def generate_ai_tip(title, content):
    """챗GPT에게 글 내용을 분석하여 맞춤형 상식 글 작성을 요청"""
    prompt = f"""
    아래 블로그 글을 읽고 러닝 관련 글인지, 헬스(웨이트 트레이닝) 관련 글인지 주식 관련 글인지 판단해줘.
    그리고 그 운동이나 주식에 딱 맞는 유익한 상식이나 꿀팁을 전문적이고 친근한 어조로 블로그에 작성할수있게 작성하고 제목도 만들어줘.

    [블로그 글 제목]
    {title}

    [블로그 글 내용]
    {content}
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# --- 실행 로직 ---
# 네이버 블로그나 티스토리의 RSS 주소 입력 (예시: 네이버는 https://rss.blog.naver.com/블로그아이디)
BLOG_RSS_URL = "https://rss.blog.naver.com/jaewan0505"

title, content = get_latest_blog_post(BLOG_RSS_URL)

if title:
    print(f"최신 블로그 글 감지: {title}")
    
    # 챗GPT를 통해 운동 종류 판별 및 맞춤 상식 생성
    ai_feedback = generate_ai_tip(title, content)
    
    # 텔레그램 메시지 포맷 구성
    message = (
        f"🏃‍♂️ [운동 블로그 맞춤 상식 알림] 🏋️‍♂️\n\n"
        f"📌 감지된 글: {title}\n\n"
        f"{ai_feedback}"
    )
    
    # 텔레그램 전송
    send_telegram_message(message)
    print("맞춤 상식 글이 텔레그램으로 전송되었습니다!")
else:
    print("새로운 블로그 글을 찾지 못했습니다.")
