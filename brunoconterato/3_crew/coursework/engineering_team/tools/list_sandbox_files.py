from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from tools.sandbox_paths import module_dir


class ListSandboxFilesInput(BaseModel):
    module_name: str = Field(
        ...,
        description='Module name, such as "calculator" or "financial reports".',
    )


class ListSandboxFilesTool(BaseTool):
    name: str = "List Sandbox Files"
    description: str = (
        "List the files inside the normalized sandbox directory for a module. "
        "Create the module directory if it does not exist."
    )
    args_schema: type[BaseModel] = ListSandboxFilesInput

    def _run(self, module_name: str) -> str:
        try:
            normalized_name, root = module_dir(module_name)
        except ValueError as error:
            return str(error)

        names = sorted(path.name for path in root.iterdir() if path.is_file())

        return "\n".join(names) if names else f"The sandbox module '{normalized_name}' is empty."
