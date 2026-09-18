import streamlit as st

main = st.Page("main.py", title="Home")
model = st.Page("model.py", title="Model")

pg = st.navigation([main, model])

pg.run()
