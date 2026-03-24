import os
from pathlib import Path

_BASE_DIR = Path(__file__).resolve().parent

DEFAULT_CONFIG = {
    "data_cache_dir": str(_BASE_DIR / "data_cache"),
}

_config = DEFAULT_CONFIG.copy()


def get_config():
    return _config.copy()
