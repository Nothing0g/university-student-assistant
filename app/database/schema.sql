PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS students (
  student_id TEXT PRIMARY KEY,
  full_name TEXT NOT NULL,
  programme TEXT NOT NULL,
  batch_year INTEGER NOT NULL,
  current_semester INTEGER NOT NULL CHECK(current_semester BETWEEN 1 AND 10),
  cgpa REAL NOT NULL CHECK(cgpa BETWEEN 0 AND 10),
  active_backlogs INTEGER NOT NULL CHECK(active_backlogs >= 0)
);
CREATE TABLE IF NOT EXISTS courses (
  course_code TEXT PRIMARY KEY,
  course_name TEXT NOT NULL,
  programme TEXT NOT NULL,
  semester INTEGER NOT NULL,
  credits INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS attendance (
  student_id TEXT NOT NULL,
  course_code TEXT NOT NULL,
  classes_held INTEGER NOT NULL CHECK(classes_held > 0),
  classes_attended INTEGER NOT NULL CHECK(classes_attended BETWEEN 0 AND classes_held),
  PRIMARY KEY(student_id, course_code),
  FOREIGN KEY(student_id) REFERENCES students(student_id),
  FOREIGN KEY(course_code) REFERENCES courses(course_code)
);
CREATE TABLE IF NOT EXISTS results (
  student_id TEXT NOT NULL,
  course_code TEXT NOT NULL,
  exam_session TEXT NOT NULL,
  exam_type TEXT NOT NULL CHECK(exam_type IN ('REGULAR', 'SUPPLEMENTARY')),
  internal_marks INTEGER NOT NULL,
  external_marks INTEGER NOT NULL,
  total_marks INTEGER NOT NULL,
  max_marks INTEGER NOT NULL,
  result TEXT NOT NULL CHECK(result IN ('PASS', 'FAIL', 'ABSENT', 'DETAINED')),
  PRIMARY KEY(student_id, course_code, exam_session, exam_type),
  FOREIGN KEY(student_id) REFERENCES students(student_id),
  FOREIGN KEY(course_code) REFERENCES courses(course_code)
);
CREATE TABLE IF NOT EXISTS rule_registry (
  rule_id TEXT PRIMARY KEY,
  description TEXT NOT NULL,
  parameter TEXT NOT NULL,
  operator TEXT NOT NULL,
  value TEXT NOT NULL,
  scope_programmes TEXT NOT NULL,
  scope_batches TEXT NOT NULL,
  effective_from TEXT NOT NULL,
  effective_to TEXT NOT NULL DEFAULT '',
  source_doc_id TEXT NOT NULL,
  source_section TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS source_register (
  doc_id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  issuer TEXT NOT NULL,
  authority_level INTEGER NOT NULL CHECK(authority_level BETWEEN 1 AND 5),
  doc_type TEXT NOT NULL,
  version TEXT NOT NULL,
  effective_from TEXT NOT NULL,
  effective_to TEXT NOT NULL DEFAULT '',
  supersedes TEXT NOT NULL DEFAULT '',
  scope_programmes TEXT NOT NULL,
  scope_batches TEXT NOT NULL,
  provenance TEXT NOT NULL,
  retrieved_on TEXT NOT NULL,
  synthetic TEXT NOT NULL CHECK(synthetic IN ('Y', 'N'))
);
CREATE TABLE IF NOT EXISTS audit_records (
  trace_id TEXT PRIMARY KEY,
  created_at TEXT NOT NULL,
  payload_json TEXT NOT NULL
);
