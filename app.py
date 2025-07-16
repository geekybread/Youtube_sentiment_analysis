# app.py
from flask import Flask, render_template, request
from scraper import scrape_comments
from sentiment import analyze_sentiment, plot_sentiment_pie, generate_wordcloud

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    url = request.form['video_url']
    comments, video_title = scrape_comments(url, max_comments=100)
    summary, detailed = analyze_sentiment(comments)
    plot_sentiment_pie(summary) 
    generate_wordcloud([c['text'] for c in detailed]) 
    return render_template('index.html', summary=summary, comments=detailed, video_title=video_title, chart='sentiment_pie.png', wordcloud='wordcloud.png')

if __name__ == '__main__':
    app.run(debug=True)
