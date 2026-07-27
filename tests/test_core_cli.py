import json

import pytest

from context_packing_previewer.cli import main
from context_packing_previewer.core import estimate_tokens, preview, render_markdown


def test_preview_filters_and_estimates(tmp_path):
    (tmp_path / "a.py").write_text("print('hello')\n", encoding="utf-8")
    (tmp_path / "secret.env").write_text("TOKEN=nope", encoding="utf-8")
    (tmp_path / "binary.bin").write_bytes(b"a\0b")
    report = preview(tmp_path, ["**/*"], budget=2)
    assert report["risk"] == "over-budget"
    assert report["files"][0]["path"] == "a.py"
    assert {item["reason"] for item in report["omitted"]} == {"excluded", "binary"}
    assert estimate_tokens("12345") == 2
    assert "a.py" in render_markdown(report)


def test_validation(tmp_path):
    with pytest.raises(ValueError, match="directory"):
        preview(tmp_path / "missing", ["**/*"])
    with pytest.raises(ValueError, match="positive"):
        preview(tmp_path, ["**/*"], budget=0)


def test_cli_json_and_safe_output(tmp_path, capsys):
    (tmp_path / "notes.txt").write_text("some notes", encoding="utf-8")
    assert main([str(tmp_path), "--include", "*.txt", "--format", "json"]) == 0
    assert json.loads(capsys.readouterr().out)["files"][0]["path"] == "notes.txt"
    output = tmp_path / "report.md"
    output.write_text("keep", encoding="utf-8")
    assert main([str(tmp_path), "--output", str(output)]) == 2
    assert output.read_text(encoding="utf-8") == "keep"
