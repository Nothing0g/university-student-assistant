from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"data/documents"
DISCLAIMER="Fictional policy created only to demonstrate the hackathon system. This is NOT an official DTU policy."

def make(name,title,clauses):
    text=f"{title}\n\n{DISCLAIMER}\n\nIssuer: HCLTech hackathon demo (fictional)\n"
    for h,b in clauses: text += f"\n{h}\n{b}\n"
    (OUT/f"{name}.txt").write_text(text)
    pdf=OUT/f"{name}.pdf"; c=canvas.Canvas(str(pdf),pagesize=A4); w,h=A4; y=h-25*mm
    for para in text.split("\n"):
        if y<25*mm: c.showPage(); y=h-25*mm
        c.setFont("Helvetica-Bold" if para.startswith(("SYNTHETIC","2.","3.","4.","5.")) else "Helvetica", 10 if para.startswith("SYNTHETIC") else 9)
        for line in [para[i:i+105] for i in range(0,len(para),105)] or [""]:
            c.drawString(20*mm,y,line); y-=5*mm
    c.save()

make("SYN-POLICY-BASE","SYNTHETIC DEMO — Student Academic Services Policy",[
("2.1 Attendance", "A student must have at least 75 percent attendance in a registered course to appear in an end-semester examination."),
("2.2 Attendance condonation", "A student with attendance from 65 percent up to the minimum may request condonation for no more than two courses."),
("2.3 Cross-reference", "The condonation request is subject to clause 2.1 and approval by the fictional Academic Services Office."),
("3.1 Pass marks", "A pass requires at least 40 marks out of 100 total marks."),
("3.2 External marks", "A pass also requires at least 24 marks out of 60 external marks."),
("3.3 Results", "ABSENT and DETAINED are not passing results."),
("4.1 Supplementary eligibility", "Supplementary assessment is available for FAIL or ABSENT in no more than two courses, but not for DETAINED."),
("4.2 Procedure", "The student submits the fictional form to the Academic Services Office within seven calendar days of result publication."),
("5.1 Placement CGPA", "For this fictional demo only, placement eligibility requires CGPA of at least 7.0."),
("5.2 Placement backlogs", "For this fictional demo only, active backlogs must be no more than 2."),
("5.3 Placement result condition", "A student with a DETAINED result is not eligible in this fictional demo."),
("6. Exception", "A documented accessibility or medical exception may be reviewed by the fictional committee; it does not change the calculated result automatically.")])
make("SYN-POLICY-AMEND","SYNTHETIC DEMO — Academic Services Amendment",[
("Effective date", "This amendment is effective from 2026-09-01."),
("2.1 Amendment to attendance", "This amendment supersedes SYN-POLICY-BASE#2.1 and changes the minimum attendance for an end-semester examination from 75 percent to 80 percent."),
("2.2 Unchanged condonation", "Clause 2.2 remains available from 65 percent, subject to the amended clause 2.1 and the two-course limit in clause 2.3."),
("3. Superseded real references", "For the demo precedence layer only, this fictional amendment relates to DTU-EXAM-2026-08-24#p1 and DTU-TP-2025-26#31. It does not alter official DTU policy."),
("4. Upcoming before effective date", "Before 2026-09-01 this amendment is upcoming and the baseline fictional rule applies.")])
print("Created", "SYN-POLICY-BASE.pdf", "and", "SYN-POLICY-AMEND.pdf")
