from flask import Flask, request, jsonify
from flask_cors import CORS
from joblib import load
import numpy as np

app = Flask(__name__)
CORS(app) # Enable CORS for front-end communication

# Load the trained model and other data
model_data = load('trained_model/model_data.joblib')
model = model_data['model']

# A dictionary to map the labels from the dataset to the disease names
# This is now updated to match the model's zero-indexed output (0-5)
label_mapping = {
    0: 'Psoriasis',
    1: 'Seborrheic Dermatitis',
    2: 'Lichen Planus',
    3: 'Pityriasis Rosea',
    4: 'Chronic Dermatitis',
    5: 'Pityriasis Rubra Pilaris'
}

# Define the confidence threshold
CONFIDENCE_THRESHOLD = 0.50

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json(force=True)
        
        # Ensure we have the 8 required features
        required_features = [
            'itching', 'koebnerPhenomenon', 'follicularPapules', 
            'fibrosisOfPapillaryDermis', 'spongiosis', 
            'inflammatoryMononuclearInfiltrate', 'bandLikeInfiltrate', 'age'
        ]
        
        if not all(feature in data for feature in required_features):
            return jsonify({'error': 'Missing one or more required features'}), 400
            
        # Get the feature values from the request
        features = [
            data['itching'], data['koebnerPhenomenon'], data['follicularPapules'],
            data['fibrosisOfPapillaryDermis'], data['spongiosis'],
            data['inflammatoryMononuclearInfiltrate'], data['bandLikeInfiltrate'], data['age']
        ]
        
        # Make a prediction
        prediction_id = model.predict([features])[0]
        prediction_label = label_label = label_mapping[prediction_id]
        
        # Get probability distribution for all classes
        probabilities = model.predict_proba([features])[0]
        
        prob_dict = {}
        for i, prob in enumerate(probabilities):
            original_label = model.classes_[i]
            prob_dict[label_mapping[original_label]] = float(prob)

        confidence_score = max(probabilities)
        
        # Check if confidence is below the threshold
        if confidence_score < CONFIDENCE_THRESHOLD:
            prediction_label = "Indeterminate"
            
        return jsonify({
            'predictedClass': prediction_label,
            'confidence': confidence_score,
            'probabilities': prob_dict
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)