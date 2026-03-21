import importlib
from pathlib import Path

PREFIX = "/api/v1"

_EXCLUDE = {"routes.py", "__init__.py"}
_routes_dir = Path(__file__).parent
_package = "app.api.v1.routes"

routes = []
for _file in sorted(_routes_dir.glob("*.py")):
    print(_file.name)
    if _file.name in _EXCLUDE or _file.name.startswith("_"):
        continue
    _module = importlib.import_module(f"{_package}.{_file.stem}")
    if hasattr(_module, "router"):
        routes.append(
            {
                "router": _module.router,
                "prefix": PREFIX,
                "tags": [_file.stem.capitalize()],
            }
        )
