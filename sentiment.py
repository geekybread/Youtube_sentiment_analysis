import matplotlib
matplotlib.use('Agg')  # Use a non-interactive backend for matplotlib
import matplotlib.pyplot as plt
from wordcloud import WordCloud
# from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
# import torch
# import torch.nn.functional as F
import re
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.proxies import WebshareProxyConfig
import os, requests
import nltk
nltk.download('vader_lexicon')



ytt_api = YouTubeTranscriptApi(
    proxy_config=WebshareProxyConfig(
        proxy_username="pcgmxnbc",
        proxy_password="<vazvu89qhxtd",
    )
)


def clean_text(text):
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r"http\S+", "", text)                  # remove URLs
    text = re.sub(r"<.*?>", "", text)                    # remove HTML tags
    text = re.sub(r"[^\w\s]", "", text)                  # remove punctuation/symbols
    text = re.sub(r"\s+", " ", text).strip()             # remove extra spaces
    return text


def get_transcript(video_id):
    try:
        transcript = ytt_api.get_transcript(video_id, languages=['en'])
        text = " ".join([t["text"] for t in transcript])
        return text
    except Exception as e:
        print(f"[Transcript Error] {e}")
        return None


HUGGINGFACE_TOKEN = os.environ.get("HUGGING_FACE_TOKEN")
API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
headers = {"Authorization": f"Bearer {HUGGINGFACE_TOKEN}"}

def chunk_text(text, chunk_size=700):
    words = text.strip().split()
    for i in range(0, len(words), chunk_size):
        yield " ".join(words[i:i + chunk_size])


def summarize_chunk(chunk):
    prompt = f"Explain the main topic and purpose of this YouTube video transcript:\n{chunk}"
    payload = {"inputs": prompt}

    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
        if response.status_code != 200:
            print(f"[API Error] {response.status_code}: {response.text}")
            return None

        result = response.json()

        if isinstance(result, list) and result:
            # Support both Hugging Face response formats
            return result[0].get("summary_text") or result[0].get("generated_text")
        else:
            print("[Unexpected Response]", result)
            return None

    except Exception as e:
        print("[Request Error]", e)
        return None


def clean_summary(text):
    if "Use the weekly Newsquiz" in text:
        return text.split("Use the weekly Newsquiz")[0].strip()
    return text


def summarize_transcript(text):
    if not text:
        raise ValueError("Transcript is empty or unavailable.")
    text=clean_text(text)
    if not text or len(text.strip()) < 20:
        return "Transcript too short to summarize."

    chunks = list(chunk_text(text, chunk_size=700))
    summaries = []

    for i, chunk in enumerate(chunks):
        print(f"[Falcon] Analyzing chunk {i+1}/{len(chunks)}...")
        summary = summarize_chunk(chunk)
        if summary:
            summaries.append(summary)

    # Optional: Final compression summary
    final_text = " ".join(summaries)
    if len(final_text.split()) > 700:
        final_text = " ".join(final_text.split()[:700])

    final_summary = summarize_chunk(final_text)
    final_summary = clean_summary(final_summary)

    return final_summary or "Could not generate context."



from nltk.sentiment.vader import SentimentIntensityAnalyzer

sia = SentimentIntensityAnalyzer()

def analyze_sentiment(comments, threshold=0.05):
    summary = {'positive': 0, 'neutral': 0, 'negative': 0}
    detailed = []

    for text in comments:
        text_clean = clean_text(text)
        score = sia.polarity_scores(text_clean)['compound']

        if score >= threshold:
            sentiment = 'positive'
        elif score <= -threshold:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'

        summary[sentiment] += 1
        detailed.append({
            "text": text,
            "sentiment": sentiment,
            "confidence": round(abs(score), 3)
        })

    return summary, detailed



def plot_sentiment_pie(results):
    labels = list(results.keys())
    sizes = list(results.values())
    colors = ['green', 'grey', 'red']

    plt.figure(figsize=(5,5))
    plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
    plt.title('Sentiment Distribution')

    plt.savefig('static/sentiment_pie.png')  # Save to static folder
    plt.close()


def generate_wordcloud(comments):
    # Combine all comments into one string
    text = " ".join(comments)

    # Generate word cloud
    wordcloud = WordCloud(width=800, height=400, background_color='white', colormap='viridis').generate(text)

    # Save image
    wordcloud.to_file("static/wordcloud.png")

