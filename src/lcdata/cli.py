import typer
from pathlib import Path
from typing import Annotated
import sys
from .main import run_main

app = typer.Typer()


@app.command()
def main(
    data_dir: Path,
    config_file: Path,
    output_dir: Path,
):
    if not data_dir.exists():
        print(f"Error: {data_dir} does not exist", file=sys.stderr)
        sys.exit(1)
    if not data_dir.is_dir():
        print(f"Error: {data_dir} is not a directory", file=sys.stderr)
        sys.exit(1)
    if not config_file.exists():
        print(f"Error: {config_file} does not exist", file=sys.stderr)
        sys.exit(1)
    if not config_file.is_file():
        print(f"Error: {config_file} is not a file", file=sys.stderr)
        sys.exit(1)
    if config_file.suffix != ".json":
        print(f"Error: {config_file} is not a json file", file=sys.stderr)
        sys.exit(1)

    try:
        run_main(
            data_dir, config_file, output_dir
        )
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cli():
    app()
