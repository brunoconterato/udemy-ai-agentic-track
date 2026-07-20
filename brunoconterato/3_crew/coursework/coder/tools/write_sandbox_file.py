from pathlib import Path

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


SANDBOX_DIR = Path(__file__).resolve().parents[1] / "sandbox"
SANDBOX_DIR.mkdir(parents=True, exist_ok=True)


class WriteSandboxFileInput(BaseModel):
    filename: str = Field(
        ...,
        description='Name of the file to write, such as "solution.py".',
    )
    content: str = Field(
        ...,
        description="Complete text content to write into the file.",
    )


class WriteSandboxFileTool(BaseTool):
    name: str = "Write Sandbox File"
    description: str = "Create or overwrite a text file inside the sandbox directory."
    args_schema: type[BaseModel] = WriteSandboxFileInput

    def _run(self, filename: str, content: str) -> str:
        sandbox_root = SANDBOX_DIR.resolve()
        path = (sandbox_root / filename).resolve()

        if path != sandbox_root and sandbox_root not in path.parents:
            return "Invalid filename: the file must remain inside the sandbox."

        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        except OSError as error:
            return f"Could not write {filename}: {error}"

        return f"Wrote {len(content)} characters to {filename}"
