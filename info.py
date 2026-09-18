import streamlit as st
import kagglehub
import pandas as pd
import os
import numpy as np
from sklearn.linear_model import LinearRegression

path = kagglehub.dataset_download(KAGGLE_DATASET)

# Constants
KAGGLE_DATASET = "igormerlinicomposer/f1-aerodynamic-stability-and-porpoising-150k-samp"
FEATURE_COLUMN = "speed_kmh"
TARGET_COLUMN = "downforce_n"
WING_ANGLE = "wing_angle_deg"
CSV_TABLE = "actaruslab_f1_telemetry_2026.csv"

st.title("Model explanation")

if (st.button("Download the Dataset")):
  with st.spinner("Downloading F1 aerodynamics dataset", show_time=True):
    global KAGGLE_DATASET
    path = kagglehub.dataset_download(KAGGLE_DATASET)
