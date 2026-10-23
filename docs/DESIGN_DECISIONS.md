# Design decisions — Stage 1

The foundation keeps one FastAPI entry point, a single SQLite database, explicit Pydantic contracts, and a small Streamlit client. The later workflow will add LangGraph, retrieval, deterministic tools, and validation without changing the external contract. SQLite is used for the structured schema and audit foundation; ChromaDB is configured for a later persisted retrieval layer. The synthetic policy layer is intentionally absent until verified real-source coverage and parameter approval exist.
