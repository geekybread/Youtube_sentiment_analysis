# app.py
from flask import Flask, render_template, request
from scraper import scrape_comments
from sentiment import analyze_sentiment_enhanced, plot_sentiment_pie, generate_wordcloud, summarize_transcript
from selenium_transcript import get_transcript

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    url = request.form['video_url']
    print("<--------------------Scraping comments ------------------->")
    video_id, comments, video_title, channel_name = scrape_comments(url, max_comments=100)
    print("<--------------------Scraping completed ------------------->")
    print("<--------------------Analyzing sentiment ------------------->")
    summary, detailed = analyze_sentiment_enhanced(comments)
    print("<--------------------Sentiment analysis completed ------------------->")
    plot_sentiment_pie(summary) 
    generate_wordcloud([c['text'] for c in detailed]) 
    #transcript = get_transcript(url, headless=True)
    #video_summary = summarize_transcript(transcript)
    return render_template('index.html', summary=summary, comments=detailed, video_title=video_title, channel_name=channel_name, chart='sentiment_pie.png', wordcloud='wordcloud.png')

if __name__ == '__main__':
    app.run(debug=True)
