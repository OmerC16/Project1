import streamlit as st

home = st.Page("home.py", title="Home")
model = st.Page("model.py", title="Model")

pg = st.navigation([home, model])

pg.run()
