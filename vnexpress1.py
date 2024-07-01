import os
import feedparser
import requests
from bs4 import BeautifulSoup
import openai
from openai import OpenAI, OpenAIError

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# URL of the RSS feed
news_feed_url = "https://vnexpress.net/rss/tin-moi-nhat.rss"

# Parse the RSS feed
news_feed = feedparser.parse(news_feed_url)

# Print the number of entries
print("The number of news entries is", len(news_feed.entries))

# Function to fetch the full content of a news article
def get_full_article(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Ensure we notice bad responses
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract the main content of the article
        content = soup.find('article', {'class': 'fck_detail'})
        if content:
            paragraphs = content.find_all('p')
            full_text = "\n".join(paragraph.get_text() for paragraph in paragraphs)
            return full_text
        else:
            return "Nội dung bài báo không tìm thấy."
    except requests.RequestException as e:
        return f"Đã xảy ra lỗi khi lấy bài báo: {e}"

# Function to summarize text using OpenAI's API
def summarize_text(text):
    try:
        response = client.chat.completions.create(model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Bạn là trợ lý hữu ích tóm tắt các bài báo tin tức."},
            {"role": "user", "content": f"Tóm tắt các bài báo sau thành 1 đoạn văn dưới 100 từ. One article, one sentence: {text}"}
        ],
        temperature=0,
        max_tokens=500)
        summary = response.choices[0].message.content
        return summary.strip()
    except OpenAIError as e:
        return f"Đã xảy ra lỗi khi tóm tắt bài báo: {e}"

# Get full content and summarize for the first 5 news entries
all_articles = ""
for entry in news_feed.entries[:5]:
    print(f"Title: {entry.title}")
    print(f"Link: {entry.link}")
    full_text = get_full_article(entry.link)
    if full_text != "Nội dung bài báo không tìm thấy." and "Đã xảy ra lỗi" not in full_text:
        all_articles += f"{full_text}\n\n"

if all_articles:
    summary = summarize_text(all_articles)
    print("Summary of the first 5 articles:")
    print(summary)
else:
    print("Không có bài báo nào để tóm tắt.")

