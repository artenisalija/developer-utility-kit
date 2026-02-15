from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from toolkit.cli import app

runner = CliRunner()


def test_analyze_json() -> None:
    result = runner.invoke(app, ["analyze", "--text", '{"a": 1}'])
    assert result.exit_code == 0
    assert "json" in result.stdout


def test_convert_upper() -> None:
    result = runner.invoke(app, ["convert", "--text", "hello", "--to", "upper", "--from", "text"])
    assert result.exit_code == 0
    assert "HELLO" in result.stdout


def test_validate_json_invalid() -> None:
    result = runner.invoke(app, ["validate", "--kind", "json", "--text", '{"a":'])
    assert result.exit_code == 1


def test_validate_json_valid() -> None:
    result = runner.invoke(app, ["validate", "--kind", "json", "--text", '{"a": 1}'])
    assert result.exit_code == 0
    assert "Valid JSON" in result.stdout


def test_format_json() -> None:
    result = runner.invoke(app, ["format", "--kind", "json", "--text", '{"b":2,"a":1}'])
    assert result.exit_code == 0
    assert '"a": 1' in result.stdout


def test_minify_xml() -> None:
    result = runner.invoke(
        app, ["minify", "--kind", "xml", "--text", "<root>\n  <a>1</a>\n</root>"]
    )
    assert result.exit_code == 0
    assert "<a>1</a>" in result.stdout


def test_convert_missing_to_errors() -> None:
    result = runner.invoke(app, ["convert", "--text", "hello"])
    assert result.exit_code == 2


def test_convert_multiple_to_with_output_errors(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        [
            "convert",
            "--text",
            "hello",
            "--from",
            "text",
            "--to",
            "upper",
            "--to",
            "lower",
            "--output",
            "out.txt",
            "--output-dir",
            str(tmp_path),
        ],
    )
    assert result.exit_code == 2


def test_convert_from_file(tmp_path: Path) -> None:
    input_file = tmp_path / "input.txt"
    input_file.write_text("hello", encoding="utf-8")
    result = runner.invoke(
        app,
        [
            "convert",
            "--file",
            str(input_file),
            "--from",
            "text",
            "--to",
            "upper",
        ],
    )
    assert result.exit_code == 0
    assert "HELLO" in result.stdout


def test_convert_all_detected_binary() -> None:
    result = runner.invoke(app, ["convert-all", "--text", "01101000 01101001", "--from", "binary"])
    assert result.exit_code == 0
    assert "[binary->text]" in result.stdout
    assert "hi" in result.stdout


def test_convert_all_prompt_choice() -> None:
    result = runner.invoke(app, ["convert-all", "--text", "hello", "--ask"], input="E\n")
    assert result.exit_code == 0
    assert "Input format:" in result.stdout


def test_analyze_missing_input_errors() -> None:
    result = runner.invoke(app, ["analyze"])
    assert result.exit_code == 2


def test_sitemap_fetch_invalid_url_errors() -> None:
    result = runner.invoke(app, ["sitemap", "fetch", "--url", "ftp://example.com/sitemap.xml"])
    assert result.exit_code == 2


def test_recent_clear() -> None:
    runner.invoke(app, ["analyze", "--text", '{"a": 1}'])
    result = runner.invoke(app, ["recent", "clear"])
    assert result.exit_code == 0
    assert "History cleared" in result.stdout


def test_sitemap_generate_to_file(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        [
            "sitemap",
            "generate",
            "--base-url",
            "https://example.com",
            "--path",
            "/",
            "--output",
            "sitemap.xml",
            "--output-dir",
            str(tmp_path),
        ],
    )
    assert result.exit_code == 0
    assert (tmp_path / "sitemap.xml").exists()


def test_recent_commands() -> None:
    runner.invoke(app, ["analyze", "--text", '{"a": 1}'])
    result = runner.invoke(app, ["recent", "show", "--limit", "5"])
    assert result.exit_code == 0
    assert "analyze" in result.stdout
