from crewai.tools import BaseTool
from pathlib import Path


SANDBOX_DIR = Path(__file__).parents[1] / "sandbox"
SANDBOX_DIR.mkdir(parents=True, exist_ok=True)


class ListSandboxFilesTool(BaseTool):
    name: str = "List Sandbox Files"
    description: str = (
        "List the filenames currently available in the sandbox directory."
    )

    def _run(self) -> str:
        names = sorted(path.name for path in SANDBOX_DIR.iterdir() if path.is_file())

        return "\n".join(names) if names else "The sandbox is empty."
