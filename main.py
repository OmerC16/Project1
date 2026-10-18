import streamlit as st

info = st.Page("info.py", title="Info")
model_1 = st.Page("model.py", title="Model (One feature)")
model_2 = st.Page("model_2.py", title="Model (Two features)")

pg = st.navigation([info, model_1, model_2])

pg.run()
