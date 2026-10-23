from __future__ import annotations
import argparse, csv, sqlite3
from pathlib import Path
from app.database.db import connect, init_db

STUDENT_FIELDS=['student_id','full_name','programme','batch_year','current_semester','cgpa','active_backlogs']
COURSE_FIELDS=['course_code','course_name','programme','semester','credits']
ATT_FIELDS=['student_id','course_code','classes_held','classes_attended']
RESULT_FIELDS=['student_id','course_code','exam_session','exam_type','internal_marks','external_marks','total_marks','max_marks','result']

def read(p,fields):
    with open(p,newline='') as f:
        rows=list(csv.DictReader(f));
    missing=set(fields)-set(rows[0] if rows else [])
    if missing: raise ValueError(f'{p}: missing fields {sorted(missing)}')
    return rows

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--dir',default='data/test_students'); args=ap.parse_args(); d=Path(args.dir)
    students=read(d/'students.csv',STUDENT_FIELDS); courses=read(d/'courses.csv',COURSE_FIELDS); attendance=read(d/'attendance.csv',ATT_FIELDS); results=read(d/'results.csv',RESULT_FIELDS)
    ids={r['student_id'] for r in students}; codes={r['course_code'] for r in courses}
    assert len(ids)==len(students) and all(len(x)==5 and x[0]=='S' and x[1:].isdigit() for x in ids)
    assert not any(9000<=int(x[1:])<=9999 for x in ids)
    assert all(r['programme'] in {s['programme'] for s in students} for r in courses)
    assert all(0<=float(r['cgpa'])<=10 and 1<=int(r['current_semester'])<=10 for r in students)
    assert all(r['student_id'] in ids and r['course_code'] in codes and 0<int(r['classes_held']) and 0<=int(r['classes_attended'])<=int(r['classes_held']) for r in attendance)
    assert all(r['student_id'] in ids and r['course_code'] in codes and int(r['total_marks'])==int(r['internal_marks'])+int(r['external_marks']) for r in results)
    init_db()
    with connect() as c:
        c.executemany('INSERT OR REPLACE INTO students VALUES (?,?,?,?,?,?,?)',[(r['student_id'],r['full_name'],r['programme'],int(r['batch_year']),int(r['current_semester']),float(r['cgpa']),int(r['active_backlogs'])) for r in students])
        c.executemany('INSERT OR REPLACE INTO courses VALUES (?,?,?,?,?)',[(r['course_code'],r['course_name'],r['programme'],int(r['semester']),int(r['credits'])) for r in courses])
        c.executemany('INSERT OR REPLACE INTO attendance VALUES (?,?,?,?)',[(r['student_id'],r['course_code'],int(r['classes_held']),int(r['classes_attended'])) for r in attendance])
        c.executemany('INSERT OR REPLACE INTO results VALUES (?,?,?,?,?,?,?,?,?)',[(r['student_id'],r['course_code'],r['exam_session'],r['exam_type'],int(r['internal_marks']),int(r['external_marks']),int(r['total_marks']),int(r['max_marks']),r['result']) for r in results])
    print(f'Validated and loaded {len(students)} students, {len(courses)} courses, {len(attendance)} attendance rows, {len(results)} results rows')
if __name__=='__main__': main()
