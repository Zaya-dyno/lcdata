from .objects import Context, Experiment, Condition
from pathlib import Path
import pandas as pd
from .util import file_sorting
from .error import FileHadlerError
import json


def load_config(
    config_file: Path, data_dir: Path
) -> Context:
    with open(config_file, "r") as f:
        config_data = json.load(f)
    
    experiments = []
    total_files = 0
    for exp_data in config_data["experiments"]:
        experiments.append(
            Experiment(
                name=exp_data["name"],
                number_of_condition=exp_data["number_of_condition"],
                conditions=[
                    Condition(
                        name=condition["name"],
                        raw_path=[Path(p) for p in condition["raw_files"]],
                        subtracted_path=[Path(p) for p in condition["subtracted_files"]]
                    ) for condition in exp_data["conditions"]
                ],
            )
        )
        total_files += sum([len(condition["raw_files"]) for condition in exp_data["conditions"]])

    return Context(
        data_dir=data_dir,
        experiments=experiments,
        total_files=total_files,
    )


def load_data(config: Context):
    files = list(config["data_dir"].iterdir())

    files = list(filter(lambda x: x.suffix == ".csv", files))

    if len(files) != config["total_files"]:
        raise FileHadlerError(
            f"Expected {config['total_files']} files, but got {len(files)}"
        )

    for experiment in config["experiments"]:
        time = pd.read_csv(experiment["raw_path"][0], skiprows=1)[["Time (days)"]].rename(columns={"Time (days)": "time/days"})
        experiment["time"] = time
        for condition in experiment["conditions"]:
            raw_data = [
                pd.read_csv(raw_path, skiprows=1)[["counts/sec"]].rename(columns={"counts/sec": condition["name"]})
                for raw_path in condition["raw_path"]
            ]
            subtracted_data = [
                pd.read_csv(subtracted_path, skiprows=1)[["counts/sec"]].rename(columns={"counts/sec": condition["name"]})
                for subtracted_path in condition["subtracted_path"]
            ]
            condition["raw_data"] = raw_data
            condition["subtracted_data"] = subtracted_data
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
