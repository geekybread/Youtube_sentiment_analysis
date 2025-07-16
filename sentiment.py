from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import matplotlib.pyplot as plt
from wordcloud import WordCloud

def analyze_sentiment(comments):
    analyzer = SentimentIntensityAnalyzer()
    results = {"positive": 0, "neutral": 0, "negative": 0}
    analyzed = []

    for c in comments:
        score = analyzer.polarity_scores(c)
        compound = score['compound']
        if compound >= 0.05:
            label = "positive"
        elif compound <= -0.05:
            label = "negative"
        else:
            label = "neutral"
        results[label] += 1
        analyzed.append({"text": c, "sentiment": label, "score": compound})

    return results, analyzed


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

