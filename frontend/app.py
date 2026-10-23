import os
import streamlit as st
import requests

st.set_page_config(page_title="University Student Services Assistant", page_icon="🎓")
st.title("University Student Services Assistant")
st.caption("Stage 1 foundation — policy rules and student tools are not enabled yet.")
st.info("Policy rules in the eventual demo will be synthetic. Real DTU documents will be used for retrieval.")
api = os.getenv("API_BASE_URL", "http://localhost:8000")
question = st.text_area("Question", placeholder="Ask a university services question")
if st.button("Ask"):
    if not question.strip():
        st.warning("Enter a question first.")
    else:
        try:
            result = requests.post(f"{api}/ask", json={"question": question}, timeout=10)
            st.json(result.json())
        except requests.RequestException as exc:
            st.error(f"API unavailable: {exc}")
