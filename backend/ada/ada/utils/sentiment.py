from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Initialize once
analyzer = SentimentIntensityAnalyzer()

def analyze_text(text):
    scores = analyzer.polarity_scores(text)
    compound = scores["compound"]

    if compound >= 0.05:
        sentiment = "positive"
    elif compound <= -0.05:
        sentiment = "negative"
    else:
        sentiment = "neutral"

    return sentiment, abs(compound)  # return sentiment + confidence
