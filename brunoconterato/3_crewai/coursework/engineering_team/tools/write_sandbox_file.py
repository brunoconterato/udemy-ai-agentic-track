from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from tools.sandbox_paths import module_file


class WriteSandboxFileInput(BaseModel):
    module_name: str = Field(
        ...,
        description='Module name, such as "calculator" or "financial reports".',
    )
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
    description: str = (
        "Create or overwrite a text file inside a module directory in the sandbox."
    )
    args_schema: type[BaseModel] = WriteSandboxFileInput

    def _run(self, module_name: str, filename: str, content: str) -> str:
        try:
            resolved = module_file(module_name, filename)
        except ValueError as error:
            return str(error)

        if resolved is None:
            return "Invalid filename: the file must remain inside the module sandbox."

        _, path = resolved

        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        except OSError as error:
            return f"Could not write {filename}: {error}"

        return f"Wrote {len(content)} characters to {filename}"
