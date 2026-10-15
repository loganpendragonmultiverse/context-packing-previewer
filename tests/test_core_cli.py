import json
from pathlib import Path

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


@pytest.mark.parametrize("pattern", ["**/*", ".env.*", "**/.env.*", "nested/.env.production"])
def test_dotenv_variants_are_excluded_before_reads(tmp_path, monkeypatch, pattern):
    names = [
        ".env",
        ".env.local",
        ".env.production",
        ".env.example",
        "nested/.env",
        "nested/.env.local",
        "nested/.env.production",
        "nested/.env.example",
        "service.env",
    ]
    originals = {}
    for name in names:
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"SYNTHETIC_PRIVATE_CANARY=do-not-read")
        originals[path] = path.read_bytes()
    original_read = Path.read_bytes

    def guarded_read(path):
        if path in originals:
            pytest.fail("excluded dotenv file was opened")
        return original_read(path)

    monkeypatch.setattr(Path, "read_bytes", guarded_read)
    report = preview(tmp_path, [pattern])
    assert report["files"] == []
    assert report["estimated_tokens"] == 0
    assert report["omitted"]
    assert all(item["reason"] == "excluded" for item in report["omitted"])
    assert "SYNTHETIC_PRIVATE_CANARY" not in json.dumps(report)
    assert all(original_read(path) == content for path, content in originals.items())


def test_ordinary_files_still_count_next_to_dotenv(tmp_path):
    (tmp_path / ".environment").write_text("12345", encoding="utf-8")
    (tmp_path / "notes.txt").write_text("1234", encoding="utf-8")
    (tmp_path / ".env.local").write_text("SYNTHETIC_PRIVATE_CANARY", encoding="utf-8")
    report = preview(tmp_path, ["**/*"])
    assert [item["path"] for item in report["files"]] == [".environment", "notes.txt"]
    assert report["estimated_tokens"] == 3
    assert report["omitted"] == [{"path": ".env.local", "reason": "excluded"}]
