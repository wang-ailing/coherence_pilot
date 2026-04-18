import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict


PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = PROJECT_ROOT / "config" / "runtime.json"


@lru_cache(maxsize=1)
def load_runtime_config() -> Dict[str, Any]:
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def project_path(relative_path: str) -> Path:
    return PROJECT_ROOT / relative_path


def get_template_text(template_key: str) -> str:
    config = load_runtime_config()
    template_path = project_path(config["templates"][template_key])
    return template_path.read_text(encoding="utf-8")
