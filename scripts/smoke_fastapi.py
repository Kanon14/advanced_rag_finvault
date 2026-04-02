import importlib
import sys

from fastapi import FastAPI


def main() -> int:
    try:
        module = importlib.import_module("backend.main")
        app = getattr(module, "app", None)
        if not isinstance(app, FastAPI):
            raise TypeError("backend.main:app is missing or not a FastAPI instance")

        routes = [route.path for route in app.routes]
        print("OK: FastAPI app import/startup check passed")
        print(f"Registered routes: {routes}")
        return 0
    except Exception as exc:
        print(f"ERROR: FastAPI smoke check failed -> {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
