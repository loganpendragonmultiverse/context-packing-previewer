from pathlib import Path
from unittest.mock import patch

import pytest

from context_packing_previewer.core import preview, render_markdown


def test_symlinked_components_are_never_read(tmp_path):
    root = tmp_path / "root"
    root.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "ordinary.txt").write_text("synthetic")
    link = root / "link"
    try:
        link.symlink_to(outside, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("symlinks unavailable")
    with patch.object(Path, "read_bytes", side_effect=AssertionError("symlink content read")):
        assert preview(root, ["link/*.txt"])["files"] == []
        with pytest.raises(ValueError, match="symlink"):
            preview(link, ["*"])


@pytest.mark.parametrize("pattern", ["../outside/*.txt", "sub/../../*", "/tmp/*.txt"])
def test_escaping_patterns_refused(tmp_path, pattern):
    with pytest.raises(ValueError, match="relative"):
        preview(tmp_path, [pattern])


@pytest.mark.parametrize(
    "limits",
    [{"budget": True}, {"budget": 1.5}, {"max_file_bytes": False}, {"max_file_bytes": 1.5}],
)
def test_exact_integer_limits(tmp_path, limits):
    with pytest.raises(ValueError, match="positive"):
        preview(tmp_path, ["*"], **limits)


def test_budget_boundaries_unicode_omissions_and_literal_names(tmp_path):
    (tmp_path / "a.py").write_text("1234")
    report = preview(tmp_path, ["*.py"], budget=1)
    assert report["estimated_tokens"] == 1 and report["risk"] == "near-budget"
    assert len(report["files"]) == 1
    (tmp_path / "bad.txt").write_bytes(b"\xff")
    (tmp_path / "large.txt").write_text("123456")
    name = "pipe|" + chr(96) + "<x>.txt"
    (tmp_path / "ordinary.txt").write_text("12345")
    report = preview(tmp_path, ["*"], budget=10, max_file_bytes=5)
    assert report["risk"] == "within-budget"
    assert {x["reason"] for x in report["omitted"]} == {"not-utf8", "too-large"}
    next(item for item in report["files"] if item["path"] == "ordinary.txt")["path"] = name
    text = render_markdown(report)
    assert "\\|" in text and "&#96;" in text and "&lt;x&gt;" in text
    assert "a.py" in text
