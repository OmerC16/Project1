import streamlit as st
import kagglehub
import pandas as pd
import os
import numpy as np
from sklearn.linear_model import LinearRegression

KAGGLE_DATASET = "igormerlinicomposer/f1-aerodynamic-stability-and-porpoising-150k-samp"
FEATURE_COLUMNS = ["speed_kmh", "wing_angle_deg"]
TARGET_COLUMN = "downforce_n"
WING_ANGLE = "wing_angle_deg"
CSV_TABLE = "actaruslab_f1_telemetry_2026.csv"

path = kagglehub.dataset_download(KAGGLE_DATASET)

csv_path = os.path.join(path, CSV_TABLE)
data = pd.read_csv(csv_path)

X = data[FEATURE_COLUMNS]
y = data[TARGET_COLUMN].to_numpy()

X = X[:40000]
y = y[:40000]

def mse_loss(y_true, y_predict):
  return np.mean((y_true - y_predict) ** 2)

baseline_pred = np.mean(y)
baseline_loss = mse_loss(y, baseline_pred)

model = LinearRegression()
model.fit(X, y)
y_hat = model.predict(X)