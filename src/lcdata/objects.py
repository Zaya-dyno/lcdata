from typing import TypedDict
from pathlib import Path
import pandas as pd


class Condition(TypedDict):
    name: str
    raw_data: list[pd.DataFrame]
    subtracted_data: list[pd.DataFrame]
    raw_data_combined: pd.DataFrame
    subtracted_data_combined: pd.DataFrame
    raw_data_average: pd.DataFrame
    subtracted_data_average: pd.DataFrame
    raw_path: list[Path]
    subtracted_path: list[Path]


class Experiment(TypedDict):
    name: str
    number_of_condition: int
    time: pd.DataFrame
    conditions: list[Condition]


class Context(TypedDict):
    data_dir: Path
    number_of_experiment: int
    experiments: list[Experiment]
