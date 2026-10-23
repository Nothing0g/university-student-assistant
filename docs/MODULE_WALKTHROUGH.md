# Module walkthrough

`app/api/main.py` owns the HTTP contract, validation, startup initialization, ingestion, source listing, student listing, and audit lookup. A judge can add an endpoint or change an HTTP status here.

`app/services/core.py` contains the controlled workflow. `answer_question` performs simple intent routing, selects retrieval or deterministic tools, and returns structured evidence. `personal_tools` reads SQLite and applies source-linked rules. A judge can add a new tool or keyword route here without changing the UI.

`app/database/schema.sql` defines the Annex C tables. `scripts/load_students.py` validates and idempotently loads CSV files. A judge can load a new valid student file with the same command.

`data/documents` contains the two user-provided real DTU sources, the readable notice companion transcription, and exactly two synthetic policy documents. The synthetic PDF generator is reproducible in `scripts/create_synthetic_policies.py`.

`frontend/app.py` is a thin Streamlit client. It sends every question to the API, forwards the trusted student selector as `X-Student-Id`, renders citations and tool evidence, and calls `/ingest` for uploads.

`tests/` and `scripts/smoke_test.py` verify the foundation and live HTTP path. The current demo uses lexical retrieval so it starts quickly and offline; the dependency/configuration scaffolding preserves the intended ChromaDB and Sentence Transformers upgrade path.
