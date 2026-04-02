import streamlit as st


def main() -> None:
    st.set_page_config(page_title="FinVault", page_icon="FV", layout="wide")
    st.title("FinVault - Stage 0")
    st.caption("Setup scaffold only. No RAG logic implemented yet.")
    st.success("Frontend placeholder is running.")


if __name__ == "__main__":
    main()
