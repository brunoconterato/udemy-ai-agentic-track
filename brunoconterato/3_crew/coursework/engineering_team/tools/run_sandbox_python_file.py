import subprocess
from typing import Literal

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from tools.sandbox_paths import module_file


class RunSandboxPythonFileInput(BaseModel):
    module_name: str = Field(
        ...,
        description='Module name, such as "calculator" or "financial reports".',
    )
    filename: str = Field(
        ...,
        description='Name of the Python file to execute, such as "solution.py".',
    )
    filetype: Literal["run", "test"]


class RunSandboxPythonFileTool(BaseTool):
    name: str = "Run Sandbox Python File"
    description: str = (
        "Execute a Python file from the sandbox inside an ephemeral Docker "
        "container and return its output."
    )
    args_schema: type[BaseModel] = RunSandboxPythonFileInput

    @staticmethod
    def _python_command(filename: str, filetype: Literal["run", "test"]) -> list[str]:
        if filetype == "test":
            return ["python", "-m", "unittest", filename]
        return ["python", filename]

    def _run(
        self, module_name: str, filename: str, filetype: Literal["run", "test"]
    ) -> str:
        try:
            resolved = module_file(module_name, filename)
        except ValueError as error:
            return str(error)

        if resolved is None:
            return "Invalid filename: the file must remain inside the module sandbox."

        _, path = resolved

        if not path.is_file():
            return f"No such file in the sandbox module: {filename}"

        if path.suffix.lower() != ".py":
            return "Only files with the .py extension can be executed."

        python_command = self._python_command(filename, filetype)

        try:
            result = subprocess.run(
                [
                    "docker",
                    "run",
                    "--rm",
                    "--network",
                    "none",
                    "--memory",
                    "256m",
                    "--cpus",
                    "1",
                    "--pids-limit",
                    "64",
                    "--read-only",
                    "--tmpfs",
                    "/tmp:size=64m",
                    "--volume",
                    f"{path.parent}:/workspace:ro",
                    "--workdir",
                    "/workspace",
                    "python:3.13-slim",
                    *python_command,
                ],
                capture_output=True,
                text=True,
                timeout=60,
                check=False,
            )
        except subprocess.TimeoutExpired:
            return "Execution timed out after 60 seconds."
        except FileNotFoundError:
            return "Docker was not found. Verify that Docker is installed and running."
        except OSError as error:
            return f"Could not execute the file: {error}"

        stdout = result.stdout.strip()
        stderr = result.stderr.strip()

        output = [f"Exit code: {result.returncode}"]

        if stdout:
            output.append(f"STDOUT:\n{stdout}")

        if stderr:
            output.append(f"STDERR:\n{stderr}")

        if not stdout and not stderr:
            output.append("The script finished without producing output.")

        return "\n\n".join(output)
