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
    experiment_number: int,
    replica_experiment: Annotated[
        int, typer.Option(help="Number replica of experiments")
    ] = 3,
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
    if config_file.suffix != ".csv":
        print(f"Error: {config_file} is not a csv file", file=sys.stderr)
        sys.exit(1)

    try:
        run_main(
            data_dir, config_file, output_dir, experiment_number, replica_experiment
        )
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cli():
    app()
