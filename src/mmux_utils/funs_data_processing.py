from typing import List, Optional, Tuple, Union
import os
import json
import numpy as np
import pandas as pd
from pathlib import Path


def _parse_data(file: str) -> List[str]:
    data = []
    with open(file) as f:
        data = [line.strip().split() for line in f]
    return data


def _parse_json_dict(file: str):

    with open(file) as f:
        data_dict = json.load(f)["tasks"]

    columns = list(data_dict[0]["input"]["InputFile1"]["value"].keys())
    ## FIXME manual fix, we should be using all output keys
    # columns += list(data_dict[0]["output"]["OutputFile1"]["value"].keys())
    columns += ["-AFpeak"]

    data = []
    for d in data_dict:
        input_data = list(d["input"]["InputFile1"]["value"].values())
        ## FIXME manual fix, we should be using all output keys
        # output_data = list(d["output"]["OutputFile1"]["value"].values())
        output_data = [d["output"]["OutputFile1"]["value"]["AFmax_4um"]]

        data.append(input_data + output_data)

    return columns, data


def process_json_file(file: str) -> str:
    columns, data = _parse_json_dict(file)
    df = pd.DataFrame(data, columns=columns)
    df[r"%eval_id"] = np.arange(1, len(df) + 1)
    df = df[
        [r"%eval_id"] + [col for col in df.columns if col != r"%eval_id"]
    ]  # move eval_id to the front

    processed_file = file.replace(".json", "_json.txt")
    df.to_csv(processed_file, sep=" ", index=False)
    return processed_file


def get_variable_names(file: str) -> List[str]:
    file = Path(file)
    assert file.exists(), f"File {file} does not exist"
    _, ext = os.path.splitext(file)
    if ext == ".dat" or ext == ".txt":
        lines = _parse_data(file)
        return lines[0]
    elif ext == ".json":
        columns, data = _parse_json_dict(file)
        return columns
    elif ext == ".csv":
        df = pd.read_csv(file)
        return df.columns.tolist()
    else:
        raise ValueError(f"File {file} is not a DAT / TXT / JSON / CSV file")


def load_data(files: List[Path]) -> pd.DataFrame:
    dfs = []
    if isinstance(files, (str, Path)):
        files = [files]

    for file in files:
        file = Path(file) if isinstance(file, str) else file
        assert file.exists(), f"File {file} does not exist"
        _, ext = os.path.splitext(file)
        if ext == ".dat" or ext == ".txt":
            lines = _parse_data(file)
            dfs.append(pd.DataFrame(lines[1:], columns=lines[0]))
        elif ext == ".json":
            columns, data = _parse_json_dict(file)
            dfs.append(pd.DataFrame(data=data, columns=columns))
        elif ext == ".csv":
            dfs.append(pd.read_csv(file))
        else:
            raise ValueError(f"File {file} is not a DAT / TXT / JSON / CSV file")

    df = pd.concat(dfs, ignore_index=True)
    return df


def process_input_file(
    files: Union[Path, List[Path]],
    columns_to_remove: List[str] = ["interface"],
    N: Optional[int] = None,
    keep_idxs: Optional[List[int]] = None,
    filter_highest_N: Optional[int] = None,
    output_variable: Optional[str] = None,
) -> str:
    if isinstance(files, (str, Path)):
        files = [files]

    df = load_data(files)

    for c in columns_to_remove:
        if c in df.columns:
            df.drop(c, axis=1, inplace=True)
        else:
            print(f"Column {c} not found in the dataframe")

    if r"%eval_id" in df.columns:
        df[r"%eval_id"] = np.arange(1, len(df) + 1)

    # allows to only take the first N rows
    df = df.iloc[:N] if N is not None else df

    if filter_highest_N is not None:
        output_variable = df.columns[-1] if output_variable is None else output_variable
        df = df.sort_values(by=output_variable, ascending=False).iloc[filter_highest_N:]

    ## allow to only keep certain idxs
    if keep_idxs is not None:
        original_len = len(df)
        df = df[keep_idxs]
        print(f"Keeping only {len(df)} rows (of {original_len})")

    processed_file = (
        "_".join([os.path.splitext(f)[0] for f in files]) + "_processed.txt"
    )
    df.to_csv(processed_file, sep=" ", index=False)
    return processed_file


def get_results(file, key="-AFpeak"):
    df = load_data(file)

    results = df[key].values

    results = [float(r) for r in results]
    return np.array(results)
