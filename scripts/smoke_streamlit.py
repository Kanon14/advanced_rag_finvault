import importlib
import sys

import streamlit as st


def main() -> int:
    try:
        module = importlib.import_module("frontend.app")
        main_func = getattr(module, "main", None)
        if not callable(main_func):
            raise TypeError("frontend.app.main is missing or not callable")

        print("OK: Streamlit import/startup check passed")
        print(f"Streamlit version: {st.__version__}")
        return 0
    except Exception as exc:
        print(f"ERROR: Streamlit smoke check failed -> {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
