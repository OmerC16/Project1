import streamlit as st
import kagglehub
import pandas as pd
import os
import numpy as np
from sklearn.linear_model import LinearRegression
import time

# Constants
KAGGLE_DATASET = "igormerlinicomposer/f1-aerodynamic-stability-and-porpoising-150k-samp"
FEATURE_COLUMN = "speed_kmh"
TARGET_COLUMN = "downforce_n"
WING_ANGLE = "wing_angle_deg"
CSV_TABLE = "actaruslab_f1_telemetry_2026.csv"

st.title("Model explanation")
st.info("First we need to choose and download the dataset.\nThe dataset I chose is a F1 car's Aerodynamics data")
if (st.button("Download dataset")):
  path = kagglehub.dataset_download(KAGGLE_DATASET)
  csv_path = os.path.join(path, CSV_TABLE)
  data = pd.read_csv(csv_path)
  st.dataframe(pd.DataFrame(data[:10]))
  st.warning("The provided table displays the first 10 rows of the dataset")
