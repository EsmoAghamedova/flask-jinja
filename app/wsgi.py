from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


def load_app():
    app_path = Path(__file__).resolve().parents[1] / "app.py"
    spec = spec_from_file_location("app_module", app_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to locate app.py for WSGI loading.")
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.app


app = load_app()
