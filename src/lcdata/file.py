from .objects import Context, Experiment, Condition
from pathlib import Path
import pandas as pd
from .util import file_sorting
from .error import FileHadlerError


def load_config(
    config_file: Path, replica_experiment: int, data_dir: Path, experiment_number: int
) -> Context:
    with open(config_file, "r") as f:
        config_raw = f.read()
        config_raw = config_raw.split("\n")[:experiment_number]
    experiments = []
    for row in config_raw:
        row = row.split(",")
        experiments.append(
            Experiment(
                name=row[0],
                number_of_experiment=row[1],
                conditions=[
                    Condition(name=condition_name) for condition_name in row[2:]
                ],
            )
        )

    return Context(
        replica_experiment=replica_experiment,
        data_dir=data_dir,
        experiment_number=experiment_number,
        experiments=experiments,
    )


def load_data(config: Context):
    files = list(config["data_dir"].iterdir())

    files = list(filter(lambda x: x.suffix == ".csv", files))
    expected_number_of_files = 2 * config["replica_experiment"]
    expected_number_of_files *= sum(
        [len(experiment["conditions"]) for experiment in config["experiments"]]
    )
    if len(files) != expected_number_of_files:
        raise FileHadlerError(
            f"Expected {expected_number_of_files} files, but got {len(files)}"
        )
    files = file_sorting(files)
    conditions_paths = []
    for index in range(0, len(files), 2):
        raw_file = files[index]
        subtracted_file = files[index + 1]
        conditions_paths.append(
            {
                "raw": raw_file,
                "subtracted": subtracted_file,
            }
        )

    conditions_data = []
    for condition in conditions_paths:
        time = pd.read_csv(condition["raw"], skiprows=1)[["Time (days)"]]
        raw_data = pd.read_csv(condition["raw"], skiprows=1)[["counts/sec"]]
        subtracted_data = pd.read_csv(condition["subtracted"], skiprows=1)[
            ["counts/sec"]
        ]
        conditions_data.append(
            {
                "time": time,
                "raw": raw_data,
                "subtracted": subtracted_data,
                "raw_path": condition["raw"],
                "subtracted_path": condition["subtracted"],
            }
        )

    current_index = 0
    for experiment in config["experiments"]:
        for condition in experiment["conditions"]:
            if "time" not in experiment:
                experiment["time"] = conditions_data[current_index]["time"]
            raw_data = [
                conditions_data[current_index + i]["raw"].rename(columns={"counts/sec": condition["name"]})
                for i in range(config["replica_experiment"])
            ]
            subtracted_data = [
                conditions_data[current_index + i]["subtracted"].rename(columns={"counts/sec": condition["name"]})
                for i in range(config["replica_experiment"])
            ]
            raw_data_paths = [
                conditions_data[current_index + i]["raw_path"]
                for i in range(config["replica_experiment"])
            ]
            subtracted_data_paths = [
                conditions_data[current_index + i]["subtracted_path"]
                for i in range(config["replica_experiment"])
            ]
            condition["raw_data"] = raw_data
            condition["subtracted_data"] = subtracted_data
            condition["raw_path"] = raw_data_paths
            condition["subtracted_path"] = subtracted_data_paths
            current_index += config["replica_experiment"]
    return None


def write_data(context: Context, output_dir: Path):
    if not output_dir.exists():
        output_dir.mkdir(parents=True)
    for experiment in context["experiments"]:
        for situation in ["raw", "subtracted"]:
            combined_data = pd.concat(
                [experiment["time"]]
                + [
                    condition[f"{situation}_data_combined"]
                    for condition in experiment["conditions"]
                ],
                axis=1,
            )
            combined_data.to_csv(
                output_dir / f"{experiment['name']}_{situation}_data_combined.csv",
                index=False,
            )
            average_data = pd.concat(
                [experiment["time"]]
                + [
                    condition[f"{situation}_data_average"]
                    for condition in experiment["conditions"]
                ],
                axis=1,
            )
            average_data.to_csv(
                output_dir / f"{experiment['name']}_{situation}_data_average.csv",
                index=False,
            )
