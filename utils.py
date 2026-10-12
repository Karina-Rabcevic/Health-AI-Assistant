import pandas as pd
import joblib
from sklearn.impute import KNNImputer
from constants import CATEGORICAL_MAPPINGS, QUESTIONS

def predict_heart_disease(user_data):
    model = joblib.load("Lab_3_ch/random_forest_model.pkl")
    scaler = joblib.load("Lab_3_ch/minmax_scaler.pkl")
    
    features = list(QUESTIONS.keys())
    data = pd.DataFrame([user_data], columns=features)

    for feature in CATEGORICAL_MAPPINGS:
        if feature in data:
            data[feature] = data[feature].map(CATEGORICAL_MAPPINGS[feature])
    
    imputer = KNNImputer(n_neighbors=5)
    data = pd.DataFrame(imputer.fit_transform(data), columns=data.columns)

    data_scaled = scaler.transform(data)
    data = pd.DataFrame(data_scaled, columns=data.columns)
    
    probabilities = model.predict_proba(data)[0]
    return probabilities[1]

