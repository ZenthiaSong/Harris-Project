from textblob import TextBlob

def analyze_sentiment(text):
    # Using TextBlob for simplicity
    testimonial = TextBlob(text)
    polarity = testimonial.sentiment.polarity
    # Categorize as positive, negative, or neutral based on polarity
    if polarity > 0:
        return "Positive"
    elif polarity < 0:
        return "Negative"
    else:
        return "Neutral"

def analyze_title_topics(title):
    # Define keywords for each topic
    keywords = {
        "Seriousness of gas emissions": ["emission", "gas", "CO2", "carbon", "methane"],
        "Importance of human intervention": [
            "human intervention",
            "climate action",
            "reduce emissions",
            "environmental policy",
        ],
        "Global stance": [
            "global",
            "international",
            "world",
            "countries",
            "UN",
            "Paris Agreement",
        ],
        "Significance of pollution awareness events": [
            "event",
            "awareness",
            "Earth Day",
            "campaign",
            "environmental day",
        ],
        "Weather extremes": [
            "extreme weather",
            "heatwave",
            "flood",
            "drought",
            "hurricane",
            "storm",
        ],
        "Impact of resource overconsumption": [
            "overconsumption",
            "resource depletion",
            "overuse",
            "waste",
            "consumption",
        ],
        "Donald Trump versus science": [
            "Trump",
            "Donald Trump",
            "administration",
            "climate denial",
        ],
        "Ideological positions on global warming": [
            "ideology",
            "belief",
            "skeptic",
            "denier",
            "activist",
            "environmentalist",
        ],
        "Politics": [
            "politics",
            "policy",
            "government",
            "regulation",
            "law",
            "legislation",
        ],
        "Undefined": [],
    }

    # Check each keyword in the title and assign the corresponding topic
    for topic, key_list in keywords.items():
        if any(key.lower() in title.lower() for key in key_list):
            return topic
    return "Undefined"
