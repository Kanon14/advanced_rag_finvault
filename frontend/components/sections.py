from __future__ import annotations

from typing import Any

import streamlit as st

try:
    from frontend.services.api_client import ApiClient
except ModuleNotFoundError:
    from services.api_client import ApiClient


def init_state() -> None:
    defaults: dict[str, Any] = {
        "last_job_id": "",
        "last_health": None,
        "last_ingest": None,
        "last_status": None,
        "last_chat": None,
        "debug_events": [],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _record_debug(event: str, result: dict[str, Any]) -> None:
    st.session_state.debug_events.append({"event": event, "result": result})
    st.session_state.debug_events = st.session_state.debug_events[-20:]


def render_health_section(client: ApiClient, backend_url: str) -> None:
    st.subheader("Backend Health")
    st.caption(f"Configured backend URL: `{backend_url}`")

    if st.button("Check backend health", use_container_width=True):
        result = client.get_health()
        st.session_state.last_health = result
        _record_debug("GET /health", result)

    if st.session_state.last_health:
        result = st.session_state.last_health
        if result["ok"]:
            st.success("Backend is reachable.")
            st.json(result["data"])
        else:
            st.error(f"Health check failed: {result['error']}")
            st.json(result)


def render_ingest_section(client: ApiClient) -> None:
    st.subheader("Ingestion Request")
    st.caption("Stage 3 supports both absolute path ingestion and true file upload ingestion.")

    uploaded = st.file_uploader("Optional PDF picker (UI helper only)", type=["pdf"])

    source_type = st.selectbox("source_type", ["pdf", "text", "url"], index=0)
    default_value = f"data/{uploaded.name}" if uploaded is not None else ""
    source_value = st.text_input(
        "source_value", value=default_value, placeholder="C:/path/to/file.pdf"
    )
    ticker = st.text_input("metadata.ticker (optional)", value="MSFT")

    if st.button("Submit ingest request", use_container_width=True):
        metadata = {"ticker": ticker} if ticker else {}
        result = client.post_ingest(
            source_type=source_type, source_value=source_value, metadata=metadata
        )
        st.session_state.last_ingest = result
        _record_debug("POST /ingest", result)
        if result["ok"]:
            st.session_state.last_job_id = result["data"].get("job_id", "")

    upload_clicked = st.button("Upload selected PDF and ingest", use_container_width=True)
    if upload_clicked:
        metadata = {"ticker": ticker} if ticker else {}
        if uploaded is None:
            result = {
                "ok": False,
                "status_code": None,
                "error": "No file selected for upload.",
                "data": None,
                "request_payload": {"metadata": metadata},
            }
        else:
            result = client.post_ingest_upload(
                filename=uploaded.name,
                file_bytes=uploaded.getvalue(),
                metadata=metadata,
            )
        st.session_state.last_ingest = result
        _record_debug("POST /ingest/upload", result)
        if result["ok"]:
            st.session_state.last_job_id = result["data"].get("job_id", "")

    if st.session_state.last_ingest:
        result = st.session_state.last_ingest
        if result["ok"]:
            st.success("Ingest request accepted.")
            st.json(result["data"])
        else:
            st.error(f"Ingest request failed: {result['error']}")
            st.json(result)


def render_status_section(client: ApiClient) -> None:
    st.subheader("Ingestion Status")
    job_id = st.text_input("job_id", value=st.session_state.last_job_id or "")

    if st.button("Check ingestion status", use_container_width=True):
        result = client.get_ingest_status(job_id=job_id or "")
        st.session_state.last_status = result
        _record_debug("GET /ingest/{job_id}/status", result)

    if st.session_state.last_status:
        result = st.session_state.last_status
        if result["ok"]:
            st.info("Status received.")
            st.json(result["data"])
        else:
            st.error(f"Status request failed: {result['error']}")
            st.json(result)


def render_chat_section(client: ApiClient) -> None:
    st.subheader("Chat")
    question = st.text_area("question", value="Summarize key points from the document.")
    session_id = st.text_input("session_id", value="stage2-ui")
    top_k = st.slider("top_k", min_value=1, max_value=10, value=3)
    collection_name = st.text_input("collection_name (optional)", value="")

    if st.button("Send chat request", use_container_width=True):
        result = client.post_chat(
            question=question,
            session_id=session_id,
            top_k=top_k,
            collection_name=collection_name or None,
        )
        st.session_state.last_chat = result
        _record_debug("POST /chat", result)

    if st.session_state.last_chat:
        result = st.session_state.last_chat
        if result["ok"]:
            data = result["data"]
            st.success("Chat response received.")
            st.markdown("**Answer**")
            st.write(data.get("answer", ""))

            st.markdown("**Citations**")
            citations = data.get("citations", [])
            if citations:
                st.table(citations)
            else:
                st.write("No citations returned.")
        else:
            st.error(f"Chat request failed: {result['error']}")
            st.json(result)


def render_debug_panel(backend_url: str) -> None:
    st.subheader("Debug Panel")
    st.caption(f"Backend URL: `{backend_url}`")
    st.markdown("Latest raw request/response events")

    if st.session_state.debug_events:
        st.json(st.session_state.debug_events)
    else:
        st.write("No debug events yet.")
