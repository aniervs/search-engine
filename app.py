from search_engine import engine

import streamlit as st
text = st.text_input('Put what you want to search here')
st.write(engine.do_search(text))