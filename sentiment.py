import matplotlib
matplotlib.use('Agg')  # Use a non-interactive backend for matplotlib
import matplotlib.pyplot as plt
from wordcloud import WordCloud
# from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
# import torch
# import torch.nn.functional as F
import re
# from youtube_transcript_api import YouTubeTranscriptApi
import os, requests
import nltk
nltk.download('vader_lexicon')
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from textblob import TextBlob
# def clean_text(text):
#     if not text:
#         return ""
#     text = text.lower()
#     text = re.sub(r"http\S+", "", text)                  # remove URLs
#     text = re.sub(r"<.*?>", "", text)                    # remove HTML tags
#     text = re.sub(r"[^\w\s]", "", text)                  # remove punctuation/symbols
#     text = re.sub(r"\s+", " ", text).strip()             # remove extra spaces
#     return text


# def get_transcript(video_id):
#     try:
#         transcript = ytt_api.get_transcript(video_id, languages=['en'])
#         text = " ".join([t["text"] for t in transcript])
#         return text
#     except Exception as e:
#         print(f"[Transcript Error] {e}")
#         return None

def enhanced_clean_text(text):
    """Enhanced text cleaning for better sentiment analysis"""
    if not text:
        return ""
    
    # Convert to lowercase
    text = text.lower()
    
    # Handle common abbreviations and slang
    text = re.sub(r'\bu\b', 'you', text)
    text = re.sub(r'\bur\b', 'your', text)
    text = re.sub(r'\bthx\b', 'thanks', text)
    text = re.sub(r'\bomg\b', 'oh my god', text)
    text = re.sub(r'\blol\b', 'laugh out loud', text)
    text = re.sub(r'\bwtf\b', 'what the hell', text)
    
    # Handle repeated characters (e.g., "sooooo good" -> "so good")
    text = re.sub(r'(.)\1{2,}', r'\1\1', text)
    
    # Handle negation contractions properly
    text = re.sub(r"won't", "will not", text)
    text = re.sub(r"can't", "cannot", text)
    text = re.sub(r"n't", " not", text)
    
    return text

# HUGGINGFACE_TOKEN = os.environ.get("HUGGING_FACE_TOKEN")
# API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
# headers = {"Authorization": f"Bearer {HUGGINGFACE_TOKEN}"}

# def chunk_text(text, chunk_size=700):
#     words = text.strip().split()
#     for i in range(0, len(words), chunk_size):
#         yield " ".join(words[i:i + chunk_size])


# def summarize_chunk(chunk):
#     prompt = f"Explain the main topic and purpose of this YouTube video transcript:\n{chunk}"
#     payload = {"inputs": prompt}

#     try:
#         response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
#         if response.status_code != 200:
#             print(f"[API Error] {response.status_code}: {response.text}")
#             return None

#         result = response.json()

#         if isinstance(result, list) and result:
#             # Support both Hugging Face response formats
#             return result[0].get("summary_text") or result[0].get("generated_text")
#         else:
#             print("[Unexpected Response]", result)
#             return None

#     except Exception as e:
#         print("[Request Error]", e)
#         return None


# def clean_summary(text):
#     if "Use the weekly Newsquiz" in text:
#         return text.split("Use the weekly Newsquiz")[0].strip()
#     return text


# def summarize_transcript(text):
#     if not text:
#         raise ValueError("Transcript is empty or unavailable.")
#     text=enhanced_clean_text(text)
#     if not text or len(text.strip()) < 20:
#         return "Transcript too short to summarize."

#     chunks = list(chunk_text(text, chunk_size=700))
#     summaries = []

#     for i, chunk in enumerate(chunks):
#         print(f"[Falcon] Analyzing chunk {i+1}/{len(chunks)}...")
#         summary = summarize_chunk(chunk)
#         if summary:
#             summaries.append(summary)

#     # Optional: Final compression summary
#     final_text = " ".join(summaries)
#     if len(final_text.split()) > 700:
#         final_text = " ".join(final_text.split()[:700])

#     final_summary = summarize_chunk(final_text)
#     final_summary = clean_summary(final_summary)

#     return final_summary or "Could not generate context."



sia = SentimentIntensityAnalyzer()

# def analyze_sentiment(comments, threshold=0.05):
#     summary = {'positive': 0, 'neutral': 0, 'negative': 0}
#     detailed = []

#     for text in comments:
#         text_clean = clean_text(text)
#         score = sia.polarity_scores(text_clean)['compound']

#         if score >= threshold:
#             sentiment = 'positive'
#         elif score <= -threshold:
#             sentiment = 'negative'
#         else:
#             sentiment = 'neutral'

#         summary[sentiment] += 1
#         detailed.append({
#             "text": text,
#             "sentiment": sentiment,
#             "confidence": round(abs(score), 3)
#         })

#     return summary, detailed

def analyze_sentiment_enhanced(comments, threshold=0.05, use_ensemble=True):
    """
    Enhanced sentiment analysis with multiple approaches
    
    Args:
        comments: List of text comments
        threshold: Threshold for neutral classification
        use_ensemble: Whether to use ensemble of multiple models
    """
    summary = {'positive': 0, 'neutral': 0, 'negative': 0}
    detailed = []

    for text in comments:
        if not text or text.strip() == '':
            continue
            
        text_clean = enhanced_clean_text(text)
        
        if use_ensemble:
            # Method 1: VADER
            vader_score = sia.polarity_scores(text_clean)['compound']
            
            # Method 2: TextBlob
            blob = TextBlob(text_clean)
            textblob_score = blob.sentiment.polarity
            
            # Method 3: Rule-based adjustments
            adjusted_score = apply_rule_based_adjustments(text_clean, vader_score)
            
            # Ensemble: Average the scores with weights
            final_score = (vader_score * 0.4 + textblob_score * 0.4 + adjusted_score * 0.2)
            
        else:
            # Use only VADER with adjustments
            final_score = apply_rule_based_adjustments(text_clean, 
                                                     sia.polarity_scores(text_clean)['compound'])
        
        # Classify sentiment
        if final_score >= threshold:
            sentiment = 'positive'
        elif final_score <= -threshold:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'

        summary[sentiment] += 1
        detailed.append({
            "text": text,
            "sentiment": sentiment,
            "confidence": round(abs(final_score), 3),
            "raw_score": round(final_score, 3)
        })

    return summary, detailed

def apply_rule_based_adjustments(text, base_score):
    """Apply rule-based adjustments to improve accuracy"""
    adjusted_score = base_score
    
    # Positive indicators that VADER might miss
    positive_patterns = [
        r'\b(love|amazing|awesome|fantastic|excellent|perfect|wonderful|great|good|nice|happy|glad|pleased)\b',
        r'\b(thank|thanks|appreciate|grateful|blessed)\b',
        r'\b(recommend|worth|helpful|useful)\b',
        r'[!]{2,}',  # Multiple exclamation marks often indicate excitement
        r':\)|:D|:-\)|:-D',  # Emoticons
    ]
    
    # Negative indicators that VADER might miss
    negative_patterns = [
        r'\b(hate|awful|terrible|horrible|worst|bad|disappointed|angry|frustrated|annoyed)\b',
        r'\b(problem|issue|complain|complaint|wrong|error|fail|broken)\b',
        r':\(|:-\(',  # Sad emoticons
    ]
    
    # Intensifiers
    if re.search(r'\b(very|really|extremely|absolutely|totally|completely)\b', text):
        adjusted_score *= 1.2
    
    # Check for positive patterns
    positive_matches = sum(1 for pattern in positive_patterns if re.search(pattern, text))
    if positive_matches > 0:
        adjusted_score += 0.1 * positive_matches
    
    # Check for negative patterns
    negative_matches = sum(1 for pattern in negative_patterns if re.search(pattern, text))
    if negative_matches > 0:
        adjusted_score -= 0.1 * negative_matches
    
    # Handle negation more carefully
    negation_words = r'\b(not|no|never|neither|nobody|nothing|nowhere|none)\b'
    if re.search(negation_words, text):
        # If there's negation, flip the score partially
        adjusted_score *= -0.5
    
    # Ensure score stays within bounds
    adjusted_score = max(-1.0, min(1.0, adjusted_score))
    
    return adjusted_score


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

