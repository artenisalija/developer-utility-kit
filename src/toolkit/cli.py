"""CLI entrypoint for Developer Utility Toolkit."""

from __future__ import annotations

import base64
from pathlib import Path
from typing import Annotated

import typer

from toolkit.core.detector import detect_from_path, detect_from_text
from toolkit.core.hashing import generate_hash_report
from toolkit.core.io_utils import read_text_file, safe_output_path, write_text_file
from toolkit.core.registry import TransformerRegistry
from toolkit.formatters.json_tools import format_json, minify_json, validate_json
from toolkit.formatters.xml_tools import format_xml, minify_xml, validate_xml
from toolkit.history.manager import HistoryManager
from toolkit.image_tools.pixelate import pixelate_image
from toolkit.web_tools.sitemap import fetch_sitemap_urls, generate_sitemap

app = typer.Typer(
    help=(
        "Developer Utility Toolkit.\n\n"
        "Use 'toolkit formats' to view all supported direct conversions.\n"
        "Use 'toolkit interactive' for guided conversion + full hash/checksum output."
    )
)
image_app = typer.Typer(help="Image utilities")
sitemap_app = typer.Typer(help="Sitemap utilities")
recent_app = typer.Typer(help="View and manage local command history")

app.add_typer(image_app, name="image")
app.add_typer(sitemap_app, name="sitemap")
app.add_typer(recent_app, name="recent")

DEFAULT_OUTPUT_DIR = Path(".")


def _history() -> HistoryManager:
    return HistoryManager()


def _load_input(text: str | None, file: Path | None) -> str:
    if text is None and file is None:
        raise ValueError("Provide either --text or --file")
    if text is not None and file is not None:
        raise ValueError("Use only one input source: --text or --file")
    if file is not None:
        if not file.exists() or not file.is_file():
            raise ValueError("Input file does not exist")
        return read_text_file(file)
    return text or ""


def _write_or_print(content: str, output: str | None, output_dir: Path) -> str:
    if output is None:
        typer.echo(content)
        return "stdout"
    target = safe_output_path(output_dir, output)
    write_text_file(target, content)
    typer.echo(f"Wrote output to {target}")
    return str(target)


def _print_header(text: str) -> None:
    typer.secho(f"\n{text}", bold=True)


def _print_conversion_result(source: str, target: str, content: str) -> None:
    _print_header(f"[{source}->{target}]")
    typer.echo(content)


def _print_conversion_error(source: str, target: str, error: str) -> None:
    _print_header(f"[{source}->{target}]")
    typer.secho(f"Conversion failed: {error}", fg=typer.colors.YELLOW)


def _prompt_choice(title: str, options: list[str]) -> str:
    typer.secho(f"\n{title}", bold=True)
    for idx, option in enumerate(options, start=1):
        letter = chr(ord("A") + idx - 1)
        typer.echo(f"  {idx}) [{letter}] {option}")
    choice = typer.prompt("Choice (number or letter)").strip()
    if not choice:
        raise ValueError("Format choice is required")
    if choice.isdigit():
        index = int(choice) - 1
        if 0 <= index < len(options):
            return options[index]
        raise ValueError("Invalid numeric choice")
    if len(choice) == 1 and choice.isalpha():
        index = ord(choice.upper()) - ord("A")
        if 0 <= index < len(options):
            return options[index]
    raise ValueError("Invalid choice. Use a valid number or letter.")


def _prompt_for_format(options: list[str]) -> str:
    return _prompt_choice("Select input format:", options)


def _prompt_targets(options: list[str]) -> list[str]:
    mode = _prompt_choice(
        "Select conversion mode:",
        [
            "All formats",
            "One format",
            "Multiple formats",
        ],
    )
    if mode == "All formats":
        return options
    if mode == "One format":
        return [_prompt_choice("Select target format:", options)]

    # Multiple: allow comma-separated number/letter entries.
    typer.secho("\nSelect multiple targets (comma-separated numbers or letters).", bold=True)
    for idx, option in enumerate(options, start=1):
        letter = chr(ord("A") + idx - 1)
        typer.echo(f"  {idx}) [{letter}] {option}")
    raw = typer.prompt("Targets")
    selected: list[str] = []
    for token in [item.strip() for item in raw.split(",") if item.strip()]:
        if token.isdigit():
            index = int(token) - 1
        elif len(token) == 1 and token.isalpha():
            index = ord(token.upper()) - ord("A")
        else:
            raise ValueError(f"Invalid target selection: {token}")
        if not 0 <= index < len(options):
            raise ValueError(f"Invalid target selection: {token}")
        value = options[index]
        if value not in selected:
            selected.append(value)
    if not selected:
        raise ValueError("At least one target must be selected")
    return selected


def _display_hash_report(payload: bytes, input_label: str, text_value: str | None) -> None:
    _print_header(f"Hash report source: {input_label}")
    entries = generate_hash_report(payload, text_value=text_value)
    for entry in entries:
        typer.echo(f"{entry.label}: {entry.value}")


def _derive_hash_payload(
    data: str, source: str, registry: TransformerRegistry
) -> tuple[bytes, str | None]:
    if source == "text":
        return (data.encode("utf-8"), data)
    if source == "binary":
        hex_value = registry.transform(data, "binary", "hex")
        return (bytes.fromhex(hex_value), None)
    if source == "hex":
        compact = data.strip().replace(" ", "")
        return (bytes.fromhex(compact), None)
    if source == "base64":
        return (base64.b64decode(data, validate=True), None)
    try:
        text_value = registry.transform(data, source, "text")
        return (text_value.encode("utf-8"), text_value)
    except ValueError:
        return (data.encode("utf-8"), None)


@app.command("analyze")
def analyze_command(
    text: Annotated[str | None, typer.Option(help="Inline input text")] = None,
    file: Annotated[Path | None, typer.Option(help="Input file path")] = None,
) -> None:
    """Analyze and detect input format."""
    history = _history()
    try:
        if file is not None:
            result = detect_from_path(file)
        else:
            value = _load_input(text=text, file=None)
            result = detect_from_text(value)
        typer.echo(result)
        history.add("analyze", "success", result)
    except ValueError as exc:
        history.add("analyze", "error", str(exc))
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=2) from exc


@app.command("convert")
def convert_command(
    to: Annotated[list[str] | None, typer.Option("--to", help="Output type (repeatable)")] = None,
    from_type: Annotated[str | None, typer.Option("--from", help="Input type")] = None,
    text: Annotated[str | None, typer.Option(help="Inline input text")] = None,
    file: Annotated[Path | None, typer.Option(help="Input file path")] = None,
    output: Annotated[str | None, typer.Option(help="Output filename")] = None,
    output_dir: Annotated[Path, typer.Option(help="Output directory")] = DEFAULT_OUTPUT_DIR,
) -> None:
    """Convert data using one direct input->output transformation."""
    history = _history()
    try:
        targets_raw = to or []
        if not targets_raw:
            raise ValueError("At least one --to type is required")
        if output is not None and len(targets_raw) > 1:
            raise ValueError("Single output file can only be used with one --to type")
        data = _load_input(text=text, file=file)
        detected = from_type or detect_from_text(data)
        registry = TransformerRegistry()
        targets = [item.lower().strip() for item in targets_raw]
        for idx, target in enumerate(targets):
            converted = registry.transform(data, detected, target)
            destination = output if idx == 0 else None
            if len(targets) > 1:
                typer.echo(f"[{detected}->{target}]")
            _write_or_print(converted, destination, output_dir)
        history.add("convert", "success", f"{detected}->{','.join(targets)}")
    except (ValueError, RuntimeError) as exc:
        history.add("convert", "error", str(exc))
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=2) from exc


@app.command("convert-all")
def convert_all_command(
    text: Annotated[str | None, typer.Option(help="Inline input text")] = None,
    file: Annotated[Path | None, typer.Option(help="Input file path")] = None,
    from_type: Annotated[str | None, typer.Option("--from", help="Input type override")] = None,
    ask: Annotated[bool, typer.Option(help="Prompt to choose input type")] = False,
) -> None:
    """Show all direct conversions for an input (interactive mode supported)."""
    history = _history()
    try:
        data = _load_input(text=text, file=file)
        registry = TransformerRegistry()
        supported_inputs = sorted({item[0] for item in registry.available_transformations()})
        detected = detect_from_text(data)
        source = from_type.lower().strip() if from_type else detected

        if ask:
            source = _prompt_for_format(supported_inputs)
        elif source not in supported_inputs:
            typer.echo(f"Detected '{source}' is not directly convertible.")
            source = _prompt_for_format(supported_inputs)

        available = registry.available_transformations(source)
        if not available:
            raise ValueError(f"No available conversions for '{source}'")

        _print_header(f"Input format: {source}")
        successes: list[str] = []
        failures: list[str] = []
        for _, target in available:
            try:
                converted = registry.transform(data, source, target)
                _print_conversion_result(source, target, converted)
                successes.append(target)
            except ValueError as exc:
                _print_conversion_error(source, target, str(exc))
                failures.append(target)

        target_summary = ",".join(successes) if successes else "none"
        status = "success" if successes else "error"
        if failures:
            status = "partial" if successes else "error"
        history.add("convert-all", status, f"{source}->{target_summary}")
    except (ValueError, RuntimeError) as exc:
        history.add("convert-all", "error", str(exc))
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=2) from exc


@app.command("interactive")
def interactive_command() -> None:
    """Guided mode: choose input format, enter value, print conversions + hashes."""
    history = _history()
    try:
        registry = TransformerRegistry()
        supported_inputs = sorted({item[0] for item in registry.available_transformations()})
        source = _prompt_for_format(supported_inputs)
        data = typer.prompt("Enter input value")

        available = registry.available_transformations(source)
        targets = sorted(target for _, target in available)
        selected_targets = _prompt_targets(targets)

        _print_header(f"Input format: {source}")
        successes: list[str] = []
        for target in selected_targets:
            try:
                converted = registry.transform(data, source, target)
                _print_conversion_result(source, target, converted)
                successes.append(target)
            except ValueError as exc:
                _print_conversion_error(source, target, str(exc))

        payload, text_value = _derive_hash_payload(data, source, registry)
        _display_hash_report(payload, source, text_value)
        status = "success" if successes else "error"
        history.add("interactive", status, f"{source}->{','.join(successes)}")
    except (ValueError, RuntimeError) as exc:
        history.add("interactive", "error", str(exc))
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=2) from exc


@app.command("formats")
def formats_command() -> None:
    """List all currently available direct conversion pairs."""
    registry = TransformerRegistry()
    by_input: dict[str, list[str]] = {}
    for input_type, output_type in registry.available_transformations():
        by_input.setdefault(input_type, []).append(output_type)

    if not by_input:
        typer.echo("No converters registered.")
        raise typer.Exit(code=1)

    for input_type in sorted(by_input):
        outputs = ", ".join(sorted(by_input[input_type]))
        typer.echo(f"{input_type} -> {outputs}")


@app.command("hash-all")
def hash_all_command(
    text: Annotated[str | None, typer.Option(help="Inline input text")] = None,
    file: Annotated[Path | None, typer.Option(help="Input file path")] = None,
    from_type: Annotated[str | None, typer.Option("--from", help="Input type override")] = None,
) -> None:
    """Generate all supported hash/checksum outputs for the input."""
    history = _history()
    try:
        data = _load_input(text=text, file=file)
        registry = TransformerRegistry()
        source = from_type.lower().strip() if from_type else detect_from_text(data)
        payload, text_value = _derive_hash_payload(data, source, registry)
        _display_hash_report(payload, source, text_value)
        history.add("hash-all", "success", source)
    except (ValueError, RuntimeError) as exc:
        history.add("hash-all", "error", str(exc))
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=2) from exc


@app.command("format")
def format_command(
    kind: Annotated[str, typer.Option("--kind", help="json or xml")],
    text: Annotated[str | None, typer.Option(help="Inline input text")] = None,
    file: Annotated[Path | None, typer.Option(help="Input file path")] = None,
    output: Annotated[str | None, typer.Option(help="Output filename")] = None,
    output_dir: Annotated[Path, typer.Option(help="Output directory")] = DEFAULT_OUTPUT_DIR,
) -> None:
    """Format JSON or XML content."""
    history = _history()
    try:
        data = _load_input(text=text, file=file)
        normalized = kind.lower().strip()
        if normalized == "json":
            result = format_json(data)
        elif normalized == "xml":
            result = format_xml(data)
        else:
            raise ValueError("kind must be json or xml")
        destination = _write_or_print(result, output, output_dir)
        history.add("format", "success", f"{normalized}:{destination}")
    except ValueError as exc:
        history.add("format", "error", str(exc))
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=2) from exc


@app.command("validate")
def validate_command(
    kind: Annotated[str, typer.Option("--kind", help="json or xml")],
    text: Annotated[str | None, typer.Option(help="Inline input text")] = None,
    file: Annotated[Path | None, typer.Option(help="Input file path")] = None,
) -> None:
    """Validate JSON or XML content."""
    history = _history()
    try:
        data = _load_input(text=text, file=file)
        normalized = kind.lower().strip()
        if normalized == "json":
            ok, message = validate_json(data)
        elif normalized == "xml":
            ok, message = validate_xml(data)
        else:
            raise ValueError("kind must be json or xml")
        typer.echo(message)
        history.add("validate", "success" if ok else "error", f"{normalized}:{message}")
        if not ok:
            raise typer.Exit(code=1)
    except ValueError as exc:
        history.add("validate", "error", str(exc))
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=2) from exc


@app.command("minify")
def minify_command(
    kind: Annotated[str, typer.Option("--kind", help="json or xml")],
    text: Annotated[str | None, typer.Option(help="Inline input text")] = None,
    file: Annotated[Path | None, typer.Option(help="Input file path")] = None,
    output: Annotated[str | None, typer.Option(help="Output filename")] = None,
    output_dir: Annotated[Path, typer.Option(help="Output directory")] = DEFAULT_OUTPUT_DIR,
) -> None:
    """Minify JSON or XML content."""
    history = _history()
    try:
        data = _load_input(text=text, file=file)
        normalized = kind.lower().strip()
        if normalized == "json":
            result = minify_json(data)
        elif normalized == "xml":
            result = minify_xml(data)
        else:
            raise ValueError("kind must be json or xml")
        destination = _write_or_print(result, output, output_dir)
        history.add("minify", "success", f"{normalized}:{destination}")
    except ValueError as exc:
        history.add("minify", "error", str(exc))
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=2) from exc


@image_app.command("pixelate")
def image_pixelate_command(
    input_file: Annotated[Path, typer.Option(help="Input image file path")],
    output_name: Annotated[str, typer.Option(help="Output image filename")] = "pixelated.png",
    output_dir: Annotated[Path, typer.Option(help="Output directory")] = DEFAULT_OUTPUT_DIR,
    block_size: Annotated[int, typer.Option(help="Pixel block size")] = 8,
) -> None:
    """Pixelate an image."""
    history = _history()
    try:
        output_path = safe_output_path(output_dir, output_name)
        pixelate_image(input_file, output_path, block_size=block_size)
        typer.echo(f"Wrote output to {output_path}")
        history.add("image.pixelate", "success", str(output_path))
    except (RuntimeError, ValueError) as exc:
        history.add("image.pixelate", "error", str(exc))
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=2) from exc


@sitemap_app.command("generate")
def sitemap_generate_command(
    base_url: Annotated[str, typer.Option(help="Base website URL")],
    path: Annotated[
        list[str] | None, typer.Option("--path", help="Path entries for sitemap")
    ] = None,
    paths_file: Annotated[
        Path | None, typer.Option(help="File containing one path per line")
    ] = None,
    output: Annotated[str | None, typer.Option(help="Output filename")] = None,
    output_dir: Annotated[Path, typer.Option(help="Output directory")] = DEFAULT_OUTPUT_DIR,
) -> None:
    """Generate sitemap.xml from URL and paths."""
    history = _history()
    try:
        paths = list(path or [])
        if paths_file is not None:
            data = read_text_file(paths_file)
            paths.extend(line.strip() for line in data.splitlines() if line.strip())
        if not paths:
            raise ValueError("Provide at least one --path or --paths-file entry")
        xml = generate_sitemap(base_url, paths)
        destination = _write_or_print(xml, output, output_dir)
        history.add("sitemap.generate", "success", destination)
    except ValueError as exc:
        history.add("sitemap.generate", "error", str(exc))
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=2) from exc


@sitemap_app.command("fetch")
def sitemap_fetch_command(
    url: Annotated[str, typer.Option(help="Sitemap URL")],
    timeout: Annotated[int, typer.Option(help="Request timeout in seconds")] = 10,
) -> None:
    """Fetch and list sitemap URLs."""
    history = _history()
    try:
        urls = fetch_sitemap_urls(url, timeout=timeout)
        for item in urls:
            typer.echo(item)
        history.add("sitemap.fetch", "success", f"{len(urls)} urls")
    except ValueError as exc:
        history.add("sitemap.fetch", "error", str(exc))
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=2) from exc


@recent_app.command("show")
def recent_show_command(
    limit: Annotated[int, typer.Option(help="Maximum entries to display")] = 10,
) -> None:
    """Show recent command history."""
    history = _history()
    try:
        entries = history.recent(limit=limit)
        if not entries:
            typer.echo("No history entries yet.")
            return
        for entry in entries:
            typer.echo(f"{entry.timestamp} | {entry.command} | {entry.status} | {entry.details}")
    except ValueError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=2) from exc


@recent_app.command("clear")
def recent_clear_command() -> None:
    """Clear command history."""
    history = _history()
    history.clear()
    typer.echo("History cleared.")
