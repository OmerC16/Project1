import streamlit as st

mainPage = st.Page("main.py", st.title("Home"))
model = st.Page("model.py", st.title("Model"))

pg = st.navigation([mainPage, model])

pg.run()
