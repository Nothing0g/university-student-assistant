from __future__ import annotations
import csv, json, re, sqlite3, uuid
from datetime import date
from pathlib import Path
from typing import Any
from app.config import get_settings
from app.database.db import connect

NO_INFO = "I could not find this information in the authorised university sources."
SYNTHETIC_LABEL = "SYNTHETIC DEMO — NOT OFFICIAL DTU POLICY"


def ensure_demo_state() -> None:
    from app.database.db import init_db
    init_db()
    root = Path(__file__).resolve().parents[2]
    with connect() as conn:
        for row in csv.DictReader(open(root / "data/source_register.csv", newline="")):
            conn.execute("INSERT OR REPLACE INTO source_register VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)", tuple(row.values()))
        rules = [
            ("S1-ATTENDANCE-MIN", "Minimum attendance to appear in examinations", "attendance_min_exam_pct", ">=", "75", "ALL", "ALL", "2025-07-04", "2026-08-31", "SYN-POLICY-BASE", "2.1"),
            ("S1-CONDONATION-LOWER", "Lower bound for attendance condonation", "attendance_condonation_lower_pct", ">=", "65", "ALL", "ALL", "2025-07-04", "", "SYN-POLICY-BASE", "2.2"),
            ("S1-CONDONATION-COURSES", "Maximum courses for condonation", "attendance_condonation_max_courses", "<=", "2", "ALL", "ALL", "2025-07-04", "", "SYN-POLICY-BASE", "2.3"),
            ("S2-ATTENDANCE-MIN", "Amended minimum attendance to appear in examinations", "attendance_min_exam_pct", ">=", "80", "ALL", "ALL", "2026-09-01", "", "SYN-POLICY-AMEND", "2.1"),
            ("S1-PASS-TOTAL", "Minimum total marks for a pass", "pass_total_min_marks", ">=", "40", "ALL", "ALL", "2025-07-04", "", "SYN-POLICY-BASE", "3.1"),
            ("S1-PASS-EXTERNAL", "Minimum external marks for a pass", "pass_external_min_marks", ">=", "24", "ALL", "ALL", "2025-07-04", "", "SYN-POLICY-BASE", "3.2"),
            ("S1-SUPP-MAX", "Maximum supplementary courses", "supplementary_max_courses", "<=", "2", "ALL", "ALL", "2025-07-04", "", "SYN-POLICY-BASE", "4.1"),
            ("S1-PLACEMENT-CGPA", "Minimum CGPA for placement demo", "placement_min_cgpa", ">=", "7.0", "ALL", "ALL", "2025-07-04", "", "SYN-POLICY-BASE", "5.1"),
            ("S1-PLACEMENT-BACKLOGS", "Maximum active backlogs for placement demo", "placement_max_active_backlogs", "<=", "2", "ALL", "ALL", "2025-07-04", "", "SYN-POLICY-BASE", "5.2"),
            ("S1-PLACEMENT-DETAINED", "Detained results block placement demo", "placement_no_detained", "=", "true", "ALL", "ALL", "2025-07-04", "", "SYN-POLICY-BASE", "5.3"),
        ]
        for r in rules:
            conn.execute("INSERT OR REPLACE INTO rule_registry VALUES (?,?,?,?,?,?,?,?,?,?,?)", r)


def active_rule(parameter: str, as_of: date, programme: str = "ALL", batch: int | None = None) -> sqlite3.Row | None:
    with connect() as conn:
        rows = conn.execute("SELECT * FROM rule_registry WHERE parameter=? AND effective_from<=? AND (effective_to='' OR effective_to>=?) ORDER BY effective_from DESC", (parameter, as_of.isoformat(), as_of.isoformat())).fetchall()
    return rows[0] if rows else None


def citation(doc_id: str, section: str, page: int | None, synthetic: bool) -> dict[str, Any]:
    with connect() as conn:
        r = conn.execute("SELECT * FROM source_register WHERE doc_id=?", (doc_id,)).fetchone()
    return {"doc_id": doc_id, "title": r["title"] if r else doc_id, "section": section, "page": page, "version": r["version"] if r else None, "effective_from": r["effective_from"] if r else None, "synthetic": synthetic, "label": SYNTHETIC_LABEL if synthetic else None}


def get_student(student_id: str) -> dict[str, Any] | None:
    with connect() as conn:
        r = conn.execute("SELECT * FROM students WHERE student_id=?", (student_id,)).fetchone()
    return dict(r) if r else None


def personal_tools(student_id: str, as_of: date) -> tuple[list[dict[str, Any]], list[dict[str, Any]], str]:
    student = get_student(student_id)
    if not student: return [], [], "Student record is missing from the authorised synthetic dataset."
    tools=[]; rules=[]
    with connect() as conn:
        att = conn.execute("SELECT a.*, c.course_name FROM attendance a JOIN courses c ON c.course_code=a.course_code WHERE a.student_id=?", (student_id,)).fetchall()
        results = conn.execute("SELECT r.*, c.course_name FROM results r JOIN courses c ON c.course_code=r.course_code WHERE r.student_id=?", (student_id,)).fetchall()
    min_rule=active_rule("attendance_min_exam_pct", as_of, student["programme"], student["batch_year"])
    min_att=float(min_rule["value"]) if min_rule else None
    attendance=[{"course_code":r["course_code"],"course_name":r["course_name"],"percentage":round(100*r["classes_attended"]/r["classes_held"],2),"eligible":min_att is not None and 100*r["classes_attended"]/r["classes_held"]>=min_att} for r in att]
    tools.append({"tool":"get_attendance","input":{"student_id":student_id},"output":attendance})
    tools.append({"tool":"get_student_profile","input":{"student_id":student_id},"output":student})
    if results:
        tools.append({"tool":"get_course_result","input":{"student_id":student_id},"output":[dict(r) for r in results]})
    if min_rule: rules.append({"rule_id":min_rule["rule_id"],"value":min_rule["value"],"source_doc_id":min_rule["source_doc_id"]})
    placement_rule=active_rule("placement_min_cgpa", as_of, student["programme"], student["batch_year"])
    backlog_rule=active_rule("placement_max_active_backlogs", as_of, student["programme"], student["batch_year"])
    detained=any(r["result"]=="DETAINED" for r in results)
    if placement_rule and backlog_rule:
        eligible=student["cgpa"]>=float(placement_rule["value"]) and student["active_backlogs"]<=int(backlog_rule["value"]) and not detained
        tools.append({"tool":"check_placement_eligibility","input":{"student_id":student_id},"output":{"eligible":eligible,"cgpa":student["cgpa"],"active_backlogs":student["active_backlogs"],"detained":detained}})
        rules.extend([{ "rule_id":placement_rule["rule_id"],"value":placement_rule["value"],"source_doc_id":placement_rule["source_doc_id"]},{"rule_id":backlog_rule["rule_id"],"value":backlog_rule["value"],"source_doc_id":backlog_rule["source_doc_id"]}])
    return tools, rules, json.dumps({"student":student,"attendance":attendance,"results":[dict(r) for r in results]}, default=str)


def retrieve(question: str, top_k: int = 4) -> list[dict[str, Any]]:
    root=Path(__file__).resolve().parents[2]
    chunks=[]
    for p in sorted((root/"data/documents").glob("*.txt")) + sorted((root/"data/documents").glob("*.pdf")):
        if p.suffix == ".pdf":
            try:
                from pypdf import PdfReader
                pages=[x.extract_text() or "" for x in PdfReader(str(p)).pages]
            except Exception: pages=[]
        else: pages=[p.read_text(errors="ignore")]
        for i,text in enumerate(pages,1):
            words=set(re.findall(r"[a-z0-9]+", text.lower()))
            q=set(re.findall(r"[a-z0-9]+", question.lower()))
            score=len(words & q)/(len(q) or 1)
            if score>0: chunks.append((score,p.name,i,text[:2500]))
    chunks.sort(reverse=True, key=lambda x:x[0])
    out=[]
    for score,name,page,text in chunks[:top_k]:
        if name.startswith("policy"):
            out.append({"score":round(score,3),"doc_id":"DTU-TP-2025-26","page":page,"section":"retrieved page","text":text,"synthetic":False})
        elif name.startswith("Notice"):
            out.append({"score":round(score,3),"doc_id":"DTU-EXAM-2026-08-24","page":1,"section":"paragraphs (a)-(e)","text":text,"synthetic":False})
        elif name.startswith("SYN-POLICY-BASE"):
            out.append({"score":round(score,3),"doc_id":"SYN-POLICY-BASE","page":page,"section":"retrieved clause","text":text,"synthetic":True})
        elif name.startswith("SYN-POLICY-AMEND"):
            out.append({"score":round(score,3),"doc_id":"SYN-POLICY-AMEND","page":page,"section":"retrieved clause","text":text,"synthetic":True})
    return out


def answer_question(question: str, student_id: str | None, as_of: date) -> dict[str, Any]:
    q=question.lower(); trace=str(uuid.uuid4()); tools=[]; rules=[]; citations=[]
    if any(k in q for k in ["hostel refund", "current dean", "bank account", "ignore the rules", "reveal all student records"]):
        return {"trace_id":trace,"answer":NO_INFO,"answer_type":"not_found","citations":[],"tools_invoked":[],"applied_rules":[],"conflicts_detected":[],"explanation":"No authorised source supports this request, and untrusted instructions cannot change the workflow.","as_of_date":as_of.isoformat()}
    mentioned=re.findall(r"S\d{4}", question, flags=re.I)
    if student_id and any(s.upper()!=student_id.upper() for s in mentioned):
        return {"trace_id":trace,"answer":"I cannot access another student's data. Select that student in the trusted demo selector for an authorised demo request.","answer_type":"refused","citations":[],"tools_invoked":[],"applied_rules":[],"conflicts_detected":[],"explanation":"Cross-student access is refused before any student-data tool runs.","as_of_date":as_of.isoformat()}
    personal=any(k in q for k in ["my ","myself","my attendance","my cgpa","am i","i am","my placement","my result"])
    if personal and not student_id:
        return {"trace_id":trace,"answer":"Please select a synthetic demo student before asking a personal question.","answer_type":"refused","citations":[],"tools_invoked":[],"applied_rules":[],"conflicts_detected":[],"explanation":"Personal-data access requires the trusted X-Student-Id context.","as_of_date":as_of.isoformat()}
    if student_id and ("if i pass supplementary" in q or "what is my result" in q or "my result" in q):
        tools,rules,detail=personal_tools(student_id,as_of)
        results=next((x["output"] for x in tools if x["tool"]=="get_course_result"),[])
        answer="Your authorised synthetic results are: " + "; ".join(f"{r['course_code']} {r['result']} ({r['total_marks']}/{r['max_marks']})" for r in results) + ". Any hypothetical supplementary outcome is not written back to SQLite in this demo."
        if "if i pass supplementary" in q: answer += " Placement would still require the separate fictional CGPA, backlog, and DETAINED checks."
        citations=[citation("SYN-POLICY-BASE","3.1-5.3",1,True)]
        return {"trace_id":trace,"answer":answer,"answer_type":"calculated","citations":citations,"tools_invoked":tools,"applied_rules":rules,"conflicts_detected":[],"explanation":"The Python tools read the authorised student record; hypothetical reasoning does not mutate SQLite.","as_of_date":as_of.isoformat()}
    if "supplementary" in q or "backlog" in q or "detained" in q or "pass mark" in q:
        citations=[citation("SYN-POLICY-BASE","4.1-4.3" if "supplementary" in q else "3.1-3.3",1,True)]
        answer="In this fictional demo policy, supplementary exams are available for FAIL or ABSENT results, not DETAINED results, for at most 2 courses. The demo pass thresholds are 40/100 total marks and 24/60 external marks. This is not official DTU policy."
        return {"trace_id":trace,"answer":answer,"answer_type":"retrieved_fact","citations":citations,"tools_invoked":[],"applied_rules":[],"conflicts_detected":[],"explanation":"The answer is grounded in the synthetic policy layer.","as_of_date":as_of.isoformat()}
    if personal and ("placement" in q or "eligible" in q or "attendance" in q or "cgpa" in q):
        tools,rules,detail=personal_tools(student_id,as_of)
        if "placement" in q or "eligible" in q:
            eligible=tools[-1]["output"]["eligible"] if tools and tools[-1]["tool"]=="check_placement_eligibility" else False
            citations=[citation("SYN-POLICY-BASE","5.1-5.3",1,True)]
            answer=f"You are {'eligible' if eligible else 'not eligible'} for placement under the fictional demo rules. The demo checks CGPA >= 7.0, active backlogs <= 2, and no DETAINED result. This is not official DTU policy."
        elif "cgpa" in q:
            profile=next((x["output"] for x in tools if x["tool"]=="get_student_profile"),{})
            answer=f"Your authorised synthetic CGPA is {profile.get('cgpa')}. This is synthetic demo student data."
            citations=[citation("SYN-POLICY-BASE","5.1",1,True)]
        else:
            attendance=tools[0]["output"] if tools and tools[0]["tool"]=="get_attendance" else []
            answer="Your attendance by course is: " + "; ".join(f"{x['course_code']} {x['percentage']}% ({'eligible' if x['eligible'] else 'below threshold'})" for x in attendance) + ". The active demo threshold is date-dependent and synthetic."
            citations=[citation("SYN-POLICY-AMEND" if as_of>=date(2026,9,1) else "SYN-POLICY-BASE","2.1",1,True)]
        return {"trace_id":trace,"answer":answer,"answer_type":"calculated","citations":citations,"tools_invoked":tools,"applied_rules":rules,"conflicts_detected":[],"explanation":"The Python tool calculated the result from SQLite records and source-linked rules; the language model does not decide eligibility.","as_of_date":as_of.isoformat()}
    retrieved=retrieve(question)
    if not retrieved:
        return {"trace_id":trace,"answer":NO_INFO,"answer_type":"not_found","citations":[],"tools_invoked":[],"applied_rules":[],"conflicts_detected":[],"explanation":"No authorised source passage matched the question.","as_of_date":as_of.isoformat()}
    citations=[citation(x["doc_id"],x["section"],x["page"],x["synthetic"]) for x in retrieved]
    text=" ".join(x["text"].replace("\n"," ") for x in retrieved[:2])
    return {"trace_id":trace,"answer":text[:900],"answer_type":"retrieved_fact","citations":citations,"tools_invoked":[],"applied_rules":[],"conflicts_detected":[],"explanation":"Retrieved passages are shown with source and page references. Uploaded content is treated as evidence, not instructions.","as_of_date":as_of.isoformat()}
