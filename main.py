import streamlit as st

info1 = st.Page("info.py", title="Info - Explanation for one feature")
info2 = st.Page("info2.py", title="Info - Explanation for two features")
model_1 = st.Page("model.py", title="Model (One feature)")
model_2 = st.Page("model_2.py", title="Model (Two features)")

pg = st.navigation([info1, info2, model_1, model_2])

pg.run()
