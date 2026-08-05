from pathlib import Path

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


SANDBOX_DIR = Path(__file__).resolve().parents[1] / "sandbox"
SANDBOX_DIR.mkdir(parents=True, exist_ok=True)


class ReadSandboxFileInput(BaseModel):
    filename: str = Field(
        ...,
        description='Name of the file to read, such as "solution.py".',
    )


class ReadSandboxFileTool(BaseTool):
    name: str = "Read Sandbox File"
    description: str = (
        "Read and return the text content of a file stored in the sandbox "
        "directory."
    )
    args_schema: type[BaseModel] = ReadSandboxFileInput

    def _run(self, filename: str) -> str:
        sandbox_root = SANDBOX_DIR.resolve()
        path = (sandbox_root / filename).resolve()

        if path != sandbox_root and sandbox_root not in path.parents:
            return "Invalid filename: the file must remain inside the sandbox."

        if not path.is_file():
            return f"No such file in the sandbox: {filename}"

        try:
            return path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return f"The file is not valid UTF-8 text: {filename}"
        except OSError as error:
            return f"Could not read {filename}: {error}"