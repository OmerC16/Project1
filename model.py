import streamlit as st
import kagglehub
import pandas as pd
import os
import numpy as np
from sklearn.linear_model import LinearRegression

# Constants
KAGGLE_DATASET = "igormerlinicomposer/f1-aerodynamic-stability-and-porpoising-150k-samp"
FEATURE_COLUMN = "speed_kmh"
TARGET_COLUMN = "downforce_n"
WING_ANGLE = "wing_angle_deg"
CSV_TABLE = "actaruslab_f1_telemetry_2026.csv"

# Download dataset from kagglehub
path = kagglehub.dataset_download(KAGGLE_DATASET)
csv_path = os.path.join(path, CSV_TABLE)
data = pd.read_csv(csv_path)

# Define X and y variables
X = data.loc[data[WING_ANGLE].between(25, 30), FEATURE_COLUMN].to_numpy()
y = data.loc[data[WING_ANGLE].between(25, 30), TARGET_COLUMN].to_numpy()

# baseline model calculation and loss
baseline_prediction = np.mean(y)
baseline_loss = np.mean(np.abs(y - baseline_prediction))

# Create the Linear Regression model
X_reshaped = X.reshape(-1, 1)
model = LinearRegression()
model.fit(X_reshaped, y)

# Get w and b from model
w = model.coef_[0]
b = model.intercept_
  
# Calculate loss for the model
y_hat = model.predict(X_reshaped)
model_loss = np.mean(np.abs(y - y_hat))

# Actual prediction
st.title("Predict the downforce produced by a F1 car by it's speed")
st.badge("Note that the prediction is relevant to when the wing is at an angle of 5 - 10 degrees (So the car is moving at a straight line)", color="yellow")
number = st.number_input("Enter a speed (200 - 300) kmh", value=100, placeholder="Enter speed")
if (number >= 200 and number <= 300):
  number = np.array([[number]])
  prediction = model.predict(number)[0]
  st.write()
else:
  st.badge("Please enter a speed that is in the specified range.\nSpeed entered: " + str(number), color="red")
