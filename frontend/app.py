import streamlit as st

try:
    from frontend.components.sections import (
        init_state,
        render_chat_section,
        render_debug_panel,
        render_health_section,
        render_ingest_section,
        render_status_section,
    )
    from frontend.config import get_settings
    from frontend.services.api_client import ApiClient
except ModuleNotFoundError:
    from components.sections import (
        init_state,
        render_chat_section,
        render_debug_panel,
        render_health_section,
        render_ingest_section,
        render_status_section,
    )
    from config import get_settings
    from services.api_client import ApiClient


def main() -> None:
    settings = get_settings()
    client = ApiClient(
        base_url=settings.backend_base_url,
        timeout_seconds=settings.frontend_api_timeout_seconds,
        chat_timeout_seconds=settings.frontend_chat_timeout_seconds,
    )

    st.set_page_config(page_title="FinVault", page_icon="FV", layout="wide")
    st.title("FinVault - Stage 2 Frontend Skeleton")
    st.caption("Streamlit UI connected to mocked Stage 1 FastAPI backend.")

    init_state()

    left_col, right_col = st.columns([1, 1])

    with left_col:
        render_health_section(client, settings.backend_base_url)
        render_ingest_section(client)
        render_status_section(client)

    with right_col:
        render_chat_section(client)
        render_debug_panel(settings.backend_base_url)


if __name__ == "__main__":
    main()
