from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from tools.sandbox_paths import module_file


class ReadSandboxFileInput(BaseModel):
    module_name: str = Field(
        ...,
        description='Module name, such as "calculator" or "financial reports".',
    )
    filename: str = Field(
        ...,
        description='Name of the file to read, such as "solution.py".',
    )


class ReadSandboxFileTool(BaseTool):
    name: str = "Read Sandbox File"
    description: str = (
        "Read and return the text content of a file stored inside a module "
        "directory in the sandbox."
    )
    args_schema: type[BaseModel] = ReadSandboxFileInput

    def _run(self, module_name: str, filename: str) -> str:
        try:
            resolved = module_file(module_name, filename)
        except ValueError as error:
            return str(error)

        if resolved is None:
            return "Invalid filename: the file must remain inside the module sandbox."

        _, path = resolved

        if not path.is_file():
            return f"No such file in the sandbox module: {filename}"

        try:
            return path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return f"The file is not valid UTF-8 text: {filename}"
        except OSError as error:
            return f"Could not read {filename}: {error}"
