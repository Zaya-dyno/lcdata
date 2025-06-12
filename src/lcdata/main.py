from pathlib import Path
from .file import load_config, load_data, write_data
from .process import process_data


def run_main(
    data_dir: Path,
    config_file: Path,
    output_dir: Path,
):
    context = load_config(config_file, data_dir)
    load_data(context)

    process_data(context)

    write_data(context, output_dir)
