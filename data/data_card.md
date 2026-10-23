# Synthetic student data card

## Purpose

Fictional records for the HCLTech hackathon demo of a university student services assistant. They are not DTU records and contain no real student data.

## Generator

The initial profile fields were generated with the Manus OpenAI-compatible built-in LLM proxy using model `gpt-6-luna` on 2026-10-23. The exact prompt is stored verbatim in `data/llm_generation_prompt.txt`; model metadata and usage are in `data/llm_generation_metadata.json`.

The generator returned 30 records under a strict JSON schema. A deterministic reviewed script then created the course, attendance, and result tables and patched exact boundary cases from the approved synthetic rule values. The LLM did not produce or guarantee these exact boundary values.

## Schema and counts

- 30 students
- 2 programmes: B.Tech CSE and B.Tech ECE
- 2 admission batches: 2023 and 2024
- 6 courses
- 60 attendance rows
- 60 result rows
- SQLite fields follow the required Annex C core schema.

## Edge cases

- Attendance exactly at amendment threshold: `S1001` (`CSE101`, 80%).
- Attendance below amendment but above baseline threshold: `S1002` (`CSE101`, 77.5%).
- Failed course just below pass threshold: `S1003` (`CSE101`, 39 total marks).
- Absent result: `S1004`.
- Detained result: `S1005`.
- Multiple active backlogs: `S1006` (3).
- CGPA exactly at placement cutoff: `S1001` (7.0).

## Validation

The loader validates ID format, reserved ID exclusion, programme consistency, semester range, CGPA bounds, attendance bounds, foreign keys, total-mark arithmetic, and duplicate-safe upserts. Actual validation output is recorded in `reports/data_validation_output.txt`.

## Known limitations

The dataset is synthetic and small. Names are fictional generated names. The dataset was not independently audited for demographic representation. The real-corpus minimum in the supplied build prompt remains incomplete because only two real DTU source documents are available.
