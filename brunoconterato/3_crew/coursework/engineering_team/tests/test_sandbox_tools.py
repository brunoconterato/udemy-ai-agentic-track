import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from tools import sandbox_paths
from tools.list_sandbox_files import ListSandboxFilesTool
from tools.read_sandbox_file import ReadSandboxFileTool
from tools.run_sandbox_python_file import RunSandboxPythonFileTool
from tools.write_sandbox_file import WriteSandboxFileTool


class SandboxToolsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.sandbox_patch = patch.object(
            sandbox_paths, "SANDBOX_DIR", Path(self.temp_dir.name)
        )
        self.sandbox_patch.start()

    def tearDown(self) -> None:
        self.sandbox_patch.stop()
        self.temp_dir.cleanup()

    def test_normalizes_module_name(self) -> None:
        normalized, path = sandbox_paths.module_dir(" Relatório de Vendas ")

        self.assertEqual(normalized, "relatorio_de_vendas")
        self.assertEqual(path.name, normalized)
        self.assertTrue(path.is_dir())

    def test_list_creates_empty_module_directory(self) -> None:
        result = ListSandboxFilesTool()._run("New Module")

        self.assertEqual(result, "The sandbox module 'new_module' is empty.")
        self.assertTrue((Path(self.temp_dir.name) / "new_module").is_dir())

    def test_write_and_read_are_scoped_to_module(self) -> None:
        write_result = WriteSandboxFileTool()._run(
            "Module A", "solution.py", "print('ok')"
        )
        read_result = ReadSandboxFileTool()._run("module-a", "solution.py")

        self.assertIn("Wrote 11 characters", write_result)
        self.assertEqual(read_result, "print('ok')")
        self.assertFalse((Path(self.temp_dir.name) / "solution.py").exists())

    def test_path_traversal_cannot_escape_module_directory(self) -> None:
        result = WriteSandboxFileTool()._run("calculator", "../outside.py", "x")

        self.assertEqual(
            result, "Invalid filename: the file must remain inside the module sandbox."
        )
        self.assertFalse((Path(self.temp_dir.name) / "outside.py").exists())

    def test_run_uses_module_directory_and_unittest_for_test_filetype(self) -> None:
        module_dir = Path(self.temp_dir.name) / "calculator"
        module_dir.mkdir()
        (module_dir / "test_solution.py").write_text("", encoding="utf-8")

        completed = SimpleNamespace(returncode=0, stdout="ok", stderr="")
        with patch("tools.run_sandbox_python_file.subprocess.run", return_value=completed) as run:
            result = RunSandboxPythonFileTool()._run(
                "Calculator", "test_solution.py", "test"
            )

        command = run.call_args.args[0]
        self.assertEqual(
            command[-5:],
            ["python:3.13-slim", "python", "-m", "unittest", "test_solution.py"],
        )
        self.assertIn(f"{module_dir}:/workspace:ro", command)
        self.assertIn("STDOUT:\nok", result)


if __name__ == "__main__":
    unittest.main()
