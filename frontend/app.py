import os, json
import requests
import streamlit as st

st.set_page_config(page_title="University Student Services Assistant", page_icon="🎓", layout="wide")
API=os.getenv("API_BASE_URL","http://localhost:8000")
st.title("University Student Services Assistant")
st.caption("Evidence-grounded demo: retrieval finds policy passages, Python tools calculate student results.")
st.info("Policy rules in this demo are SYNTHETIC. Real DTU documents are used for retrieval. Synthetic rules are not official DTU policy.")

try:
    health=requests.get(f"{API}/health",timeout=4).json()
    students=requests.get(f"{API}/students",timeout=4).json().get("students",[])
except requests.RequestException as exc:
    health={"status":"offline"}; students=[]; st.error(f"API unavailable: {exc}")

with st.sidebar:
    st.header("Demo controls")
    st.write(f"Service: **{health.get('status','unknown')}**")
    st.write(f"LLM mode: **{health.get('llm','unknown')}**")
    options=["No student / general"]+[f"{s['student_id']} — {s['programme']} — CGPA {s['cgpa']}" for s in students]
    choice=st.selectbox("Synthetic demo student", options)
    student_id=None if choice.startswith("No student") else choice.split(" — ")[0]
    st.caption("Personal questions use only the trusted selected student header.")
    if st.button("New conversation"):
        st.session_state.messages=[]; st.rerun()

if "messages" not in st.session_state: st.session_state.messages=[]
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["text"])
        if m.get("data"):
            with st.expander("Evidence and audit details"):
                st.json(m["data"])

examples=["What does the placement policy say about PPO reporting?","What are the supplementary exam rules?","What is my placement eligibility?","What is the attendance requirement?"]
cols=st.columns(4)
for i,e in enumerate(examples):
    if cols[i].button(e, use_container_width=True): st.session_state.pending=e
question=st.chat_input("Ask a policy or student-services question") or st.session_state.pop("pending",None)
if question:
    st.session_state.messages.append({"role":"user","text":question})
    headers={"X-Student-Id":student_id} if student_id else {}
    try:
        r=requests.post(f"{API}/ask",headers=headers,json={"question":question},timeout=20)
        data=r.json()
        text=data.get("answer",r.text)
        if data.get("citations"):
            text += "\n\n**Citations**\n"+"\n".join(f"- `{c['doc_id']}` — {c.get('title')} — page {c.get('page')} / section {c.get('section')}" + (f" — **{c['label']}**" if c.get('synthetic') else "") for c in data["citations"])
        st.session_state.messages.append({"role":"assistant","text":text,"data":data})
    except requests.RequestException as exc:
        st.session_state.messages.append({"role":"assistant","text":f"Operational error: {exc}"})
    st.rerun()

st.divider()
st.subheader("Live document ingestion")
with st.expander("Upload a text-readable document"):
    uploaded=st.file_uploader("PDF or text file",type=["pdf","txt","md"])
    if uploaded:
        metadata=st.text_area("Annex B metadata JSON",value=json.dumps({"doc_id":"DEMO-UPLOAD-1","title":"Demo uploaded source","issuer":"Demo issuer","authority_level":3,"doc_type":"notice","version":"1","effective_from":"2026-01-01","effective_to":"","supersedes":"","scope_programmes":"ALL","scope_batches":"ALL","provenance":"User upload for demo","retrieved_on":"2026-10-23","synthetic":"N"},indent=2))
        if st.button("Ingest document"):
            files={"file":(uploaded.name,uploaded.getvalue(),uploaded.type)}
            r=requests.post(f"{API}/ingest",files=files,data={"metadata":metadata},timeout=30)
            st.json(r.json())
