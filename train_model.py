import pandas as pd
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import BaggingClassifier
from sklearn.model_selection import cross_val_score
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline
from joblib import dump
import numpy as np
from sklearn.preprocessing import StandardScaler
import os

# A dictionary to map the labels from the dataset to the disease names
label_mapping = {
    0: 'Psoriasis',
    1: 'Seborrheic Dermatitis',
    2: 'Lichen Planus',
    3: 'Pityriasis Rosea',
    4: 'Chronic Dermatitis',
    5: 'Pityriasis Rubra Pilaris'
}

# The 8 key predictors as identified in the research paper
# Note: The indices are adjusted for Python's 0-based indexing
key_predictor_indices = [3, 4, 6, 14, 27, 31, 32, 33]

# Load the dataset
# Path is corrected for the Docker container's file structure
df = pd.read_csv('./data/dermatology.data', header=None, na_values='?', dtype=object)

# --- Data Preparation ---
df.dropna(subset=[33], inplace=True)
df[33] = df[33].astype(int)
for col in range(33):
    df[col] = pd.to_numeric(df[col])

X_full = df.iloc[:, key_predictor_indices].values
y_full = df.iloc[:, -1].astype(int).values

y_full -= 1

# --- Final Model: Bagging with KNN ---
print("Building a Bagging Classifier using KNN models...")

# Define the base KNN model
knn_base = KNeighborsClassifier(n_neighbors=5, weights='distance')

# Define the final Bagging Classifier
# n_estimators=100 means we'll train 100 individual KNN models
bagging_model = BaggingClassifier(
    estimator=knn_base,
    n_estimators=100,
    max_samples=0.7,  # Use 70% of the dataset for each model
    random_state=42,
    n_jobs=-1  # Use all available cores
)

# Use a pipeline to handle SMOTE and Scaling
pipeline = ImbPipeline([
    ('oversampler', SMOTE(random_state=42)),
    ('scaler', StandardScaler()),
    ('classifier', bagging_model)
])

print("\nTraining the final Bagging Classifier with a KNN base...")
pipeline.fit(X_full, y_full)

# Create the directory if it does not exist
output_dir = 'trained_model'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Save the final model
print("Saving the trained model...")
dump({
    'model': pipeline,
    'predictors': key_predictor_indices,
    'label_mapping': label_mapping
}, os.path.join(output_dir, 'model_data.joblib'))

print("The Bagging KNN model has been trained and saved to trained_model/model_data.joblib")