from pathlib import Path
import subprocess

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


SANDBOX_DIR = Path(__file__).resolve().parents[1] / "sandbox"
SANDBOX_DIR.mkdir(parents=True, exist_ok=True)


class RunSandboxPythonFileInput(BaseModel):
    filename: str = Field(
        ...,
        description='Name of the Python file to execute, such as "solution.py".',
    )


class RunSandboxPythonFileTool(BaseTool):
    name: str = "Run Sandbox Python File"
    description: str = (
        "Execute a Python file from the sandbox inside an ephemeral Docker "
        "container and return its output."
    )
    args_schema: type[BaseModel] = RunSandboxPythonFileInput

    def _run(self, filename: str) -> str:
        sandbox_root = SANDBOX_DIR.resolve()
        path = (sandbox_root / filename).resolve()

        if path != sandbox_root and sandbox_root not in path.parents:
            return "Invalid filename: the file must remain inside the sandbox."

        if not path.is_file():
            return f"No such file in the sandbox: {filename}"

        if path.suffix.lower() != ".py":
            return "Only files with the .py extension can be executed."

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
                    f"{sandbox_root}:/workspace:ro",
                    "--workdir",
                    "/workspace",
                    "python:3.13-slim",
                    "python",
                    filename,
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
