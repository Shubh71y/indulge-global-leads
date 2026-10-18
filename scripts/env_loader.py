import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
INDULGE_ENV = BASE_DIR / ".env"


def _parse_env_file(path: Path) -> dict:
    env_map = {}
    if not path.exists():
        return env_map
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    k = k.strip()
                    v = v.strip().strip("'\"")
                    if k and v:
                        env_map[k] = v
    except Exception:
        pass
    return env_map


def sync_and_load_env():
    """Loads environment variables strictly from indulge/.env."""
    indulge_vars = _parse_env_file(INDULGE_ENV)
    for k, v in indulge_vars.items():
        if k:
            os.environ[k] = v


def get_tavily_keys():
    raw = os.getenv("TAVILY_API_KEYS", "") or os.getenv("TAVILY_API_KEY", "")
    return [k.strip() for k in raw.split(",") if k.strip()]


load_env = sync_and_load_env
sync_and_load_env()
