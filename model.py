from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB

# Sample training data
texts = [
    "power cut in my area",
    "electricity not working",
    "water leakage problem",
    "no water supply",
    "internet is slow",
    "wifi not working",
]

labels = [
    "Electricity",
    "Electricity",
    "Water",
    "Water",
    "Internet",
    "Internet",
]

# Convert text to numbers
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(texts)

# Train model
model = MultinomialNB()
model.fit(X, labels)

def predict_category(text):
    x = vectorizer.transform([text])
    return model.predict(x)[0]