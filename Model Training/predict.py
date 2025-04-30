import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

class CategoryPredictor:
    def __init__(self):
        self.tfidf = joblib.load('tfidf_vectorizer.joblib')
        self.le = joblib.load('label_encoder.joblib')
        self.model = joblib.load('logistic_regression.joblib')  # Use best model
    
    def predict(self, title, description):
        # Preprocess
        text = title + ' ' + description
        text_vector = self.tfidf.transform([text])
        
        # Predict
        prediction = self.model.predict(text_vector)
        return self.le.inverse_transform(prediction)[0]

# Example usage
if __name__ == "__main__":
    predictor = CategoryPredictor()
    sample_title = "Tour vlog in Sri Lanka"
    sample_desc = "This is our lates vlog travel in srilanka"
    print("Predicted Category:", predictor.predict(sample_title, sample_desc))