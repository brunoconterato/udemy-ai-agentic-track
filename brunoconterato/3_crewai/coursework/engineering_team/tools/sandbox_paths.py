import re
import unicodedata
from pathlib import Path


SANDBOX_DIR = Path(__file__).resolve().parents[1] / "sandbox"


def normalize_module_name(module_name: str) -> str:
    """Return a safe, stable directory name for a module."""
    normalized = unicodedata.normalize("NFKD", module_name)
    normalized = normalized.encode("ascii", "ignore").decode("ascii").lower()
    normalized = re.sub(r"[^a-z0-9]+", "_", normalized).strip("_")

    if not normalized:
        raise ValueError("The module name must contain at least one letter or number.")

    return normalized


def module_dir(module_name: str) -> tuple[str, Path]:
    """Create and return the normalized module name and its sandbox directory."""
    normalized_name = normalize_module_name(module_name)
    path = SANDBOX_DIR.resolve() / normalized_name
    path.mkdir(parents=True, exist_ok=True)
    return normalized_name, path


def module_file(module_name: str, filename: str) -> tuple[str, Path] | None:
    """Resolve a filename while keeping it inside the module directory."""
    normalized_name, root = module_dir(module_name)
    path = (root / filename).resolve()

    if path == root or root not in path.parents:
        return None

    return normalized_name, path
