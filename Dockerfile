# Stage 1: Build the model
FROM python:3.9-slim as builder

WORKDIR /app

# Copy and install dependencies for model training
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the data and training script
COPY backend/train_model.py .
COPY data/dermatology.data ./data/
COPY data/dermatology.names ./data/

# Run the training script to generate the model file
RUN python3 train_model.py

# Stage 2: Final production image
FROM python:3.9-slim

WORKDIR /app

# Copy only the necessary files from the builder stage
COPY --from=builder /app/trained_model ./trained_model/
COPY backend/app.py .

# Install only the production dependencies, including imblearn which the model needs
RUN pip install --no-cache-dir flask gunicorn joblib pandas scikit-learn numpy xgboost flask-cors imblearn

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application using Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]