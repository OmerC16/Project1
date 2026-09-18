import streamlit as st

main = st.Page("main.py", st.title("Home"))
model = st.Page("model.py", st.title("Model"))

pg = st.navigation([main, model])

pg.run()
