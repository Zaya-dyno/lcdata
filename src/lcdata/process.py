from .objects import Context
import pandas as pd


def process_data(context: Context):
    for experiment in context["experiments"]:
        print(f"Processing experiment: {experiment['name']}")
        for condition in experiment["conditions"]:
            print(f"\tProcessing condition: {condition['name']}")
            raw_data_paths = " , ".join([path.name for path in condition["raw_path"]])
            subtracted_data_paths = " , ".join(
                [path.name for path in condition["subtracted_path"]]
            )
            print(f"\t\tRaw data: {raw_data_paths}")
            print(f"\t\tSubtracted data: {subtracted_data_paths}")
            condition["raw_data_combined"] = pd.concat(condition["raw_data"], axis=1)
            condition["subtracted_data_combined"] = pd.concat(
                condition["subtracted_data"], axis=1
            )
            condition["raw_data_average"] = condition["raw_data_combined"].mean(axis=1)
            condition["subtracted_data_average"] = condition[
                "subtracted_data_combined"
            ].mean(axis=1)
