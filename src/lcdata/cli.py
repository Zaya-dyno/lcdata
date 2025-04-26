import typer
from pathlib import Path
from typing import Annotated, TypedDict
import sys
import pandas as pd

app = typer.Typer()

class Condition(TypedDict):
    name: str
    raw_data: list[pd.DataFrame]
    subtracted_data: list[pd.DataFrame]
    raw_data_combined: pd.DataFrame
    subtracted_data_combined: pd.DataFrame
    raw_data_average: pd.DataFrame
    subtracted_data_average: pd.DataFrame
    raw_path: Path
    subtracted_path: Path

class Experiment(TypedDict):
    name: str
    number_of_experiment: int
    time: pd.DataFrame
    conditions: list[Condition]

class Context(TypedDict):
    replica_experiment: int
    data_dir: Path
    experiments: list[Experiment]


def load_config(config_file: Path, replica_experiment: int, data_dir: Path) -> Context:
    with open(config_file, "r") as f:
        config_raw = f.read()
        config_raw = config_raw.split("\n")
    experiments = []
    for row in config_raw:
        row = row.split(",")
        experiments.append(Experiment(
            name=row[0],
            number_of_experiment=row[1],
            conditions=[Condition(
                name=condition_name
            ) for condition_name in row[2:]],
        ))

    return Context(
        replica_experiment=replica_experiment,
        data_dir=data_dir,
        experiments=experiments,
    )

def letter_to_number(letter: str) -> int:
    return ord(letter.lower()) - ord("a") + 1

def value_file(file: Path) -> int:
    file_name = file.stem
    file_parts = file_name.split("_")
    n = 0
    n = n * 26 + letter_to_number(file_parts[0])
    n = n * 26 + letter_to_number(file_parts[1][0])
    n = n * 10 + int(str(file_parts[1][1:]))
    n = n * 2 + int(file_parts[2].lower() != "raw")
    return n

def file_sorting(files: list[Path]) -> list[(str,{"raw": Path,"subtracted": Path})]:
    files.sort(key=value_file)
    return files

def load_data(config: Context):
    files = list(config["data_dir"].iterdir())

    files = list(filter(lambda x: x.suffix == ".csv", files))
    expected_number_of_files = 2 * config["replica_experiment"]
    expected_number_of_files *= sum([len(experiment["conditions"]) for experiment in config["experiments"]])
    if len(files) != expected_number_of_files:
        print(f"Error: Expected {expected_number_of_files} files, but got {len(files)}")
        sys.exit(1)
    files = file_sorting(files)
    conditions_paths = []
    for index in range(0, len(files), 2):
        raw_file = files[index]
        subtracted_file = files[index + 1]
        conditions_paths.append({
            "raw": raw_file,
            "subtracted": subtracted_file,
        })

    conditions_data = []
    for condition in conditions_paths:
        time = pd.read_csv(condition["raw"], skiprows=1)[["Time (days)"]]
        raw_data = pd.read_csv(condition["raw"], skiprows=1)[["counts/sec"]]
        subtracted_data = pd.read_csv(condition["subtracted"], skiprows=1)[["counts/sec"]]
        conditions_data.append({
            "time": time,
            "raw": raw_data,
            "subtracted": subtracted_data,
            "raw_path": condition["raw"],
            "subtracted_path": condition["subtracted"],
        })


    current_index = 0
    experiment_datas = []
    for experiment in config["experiments"]:
        conditions_data_for_experiment = []
        for condition in experiment["conditions"]:
            if "time" not in experiment:
                experiment["time"] = conditions_data[current_index]["time"]
            raw_data = [conditions_data[current_index + i]["raw"] for i in range(config["replica_experiment"])]
            subtracted_data = [conditions_data[current_index + i]["subtracted"] for i in range(config["replica_experiment"])]
            raw_data_paths = [conditions_data[current_index + i]["raw_path"] for i in range(config["replica_experiment"])]
            subtracted_data_paths = [conditions_data[current_index + i]["subtracted_path"] for i in range(config["replica_experiment"])]
            condition["raw_data"] = raw_data
            condition["subtracted_data"] = subtracted_data
            condition["raw_path"] = raw_data_paths
            condition["subtracted_path"] = subtracted_data_paths
            current_index += config["replica_experiment"]
    return None

def process_data(context: Context):
    for experiment in context["experiments"]:
        print(f"Processing experiment: {experiment['name']}")
        for condition in experiment["conditions"]:
            print(f"\tProcessing condition: {condition['name']}")
            raw_data_paths = " , ".join([path.name for path in condition['raw_path']])
            subtracted_data_paths = " , ".join([path.name for path in condition['subtracted_path']])
            print(f"\t\tRaw data: {raw_data_paths}")
            print(f"\t\tSubtracted data: {subtracted_data_paths}")
            condition["raw_data_combined"] = pd.concat(condition["raw_data"], axis=1)
            condition["subtracted_data_combined"] = pd.concat(condition["subtracted_data"], axis=1)
            condition["raw_data_average"] = condition["raw_data_combined"].mean(axis=1)
            condition["subtracted_data_average"] = condition["subtracted_data_combined"].mean(axis=1)

def write_data(context: Context, output_dir: Path):
    if not output_dir.exists():
        output_dir.mkdir(parents=True)
    for experiment in context["experiments"]:
        for situation in ["raw", "subtracted"]:
            combined_data = pd.concat([experiment["time"]] + [condition[f"{situation}_data_combined"] for condition in experiment["conditions"]], axis=1)
            combined_data.to_csv(output_dir / f"{experiment['name']}_{situation}_data_combined.csv", index=False)
            average_data = pd.concat([experiment["time"]] + [condition[f"{situation}_data_average"] for condition in experiment["conditions"]], axis=1)
            average_data.to_csv(output_dir / f"{experiment['name']}_{situation}_data_average.csv", index=False)



@app.command()
def main(data_dir: Path,
         config_file: Path,
         output_dir: Path,
         replica_experiment: Annotated[int, typer.Option(help="Number replica of experiments")] = 3,
         ):
    if not data_dir.exists():
        print(f"Error: {data_dir} does not exist")
        sys.exit(1)
    if not data_dir.is_dir():
        print(f"Error: {data_dir} is not a directory")
        sys.exit(1)
    if not config_file.exists():
        print(f"Error: {config_file} does not exist")
        sys.exit(1)
    if not config_file.is_file():
        print(f"Error: {config_file} is not a file")
        sys.exit(1)
    if config_file.suffix != ".csv":
        print(f"Error: {config_file} is not a csv file")
        sys.exit(1)

    context = load_config(config_file, replica_experiment, data_dir)
    load_data(context)
    
    process_data(context)

    write_data(context, output_dir)


def cli():
    app()