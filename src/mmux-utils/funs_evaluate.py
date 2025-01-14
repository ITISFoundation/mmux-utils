### Allows to evaluate in different modes - batch, single set, ...
### also in OSPARC or local deployment
from typing import Callable, List
from pathlib import Path
import dakota.environment as dakenv
import datetime
import os


### Otherwise could create a class that I can instantiate and give a "model" at initialization time,
# which is given to "run dakota" as input parameter
def batch_evaluator(model: Callable, batch_input: List[dict]):
    return map(model, batch_input)  # FIXME not sure this will work


def batch_evaluator_local(model: Callable, batch_input: List[dict]):
    return [
        {"fns": [v for v in response.values()]} for response in map(model, batch_input)
    ]


def single_evaluator(model: Callable, input: dict):
    return model(input)


def create_run_dir(script_dir: Path, dir_name: str = "sampling"):
    ## part 1 - setup
    main_runs_dir = script_dir / "runs"
    current_time = datetime.datetime.now().strftime("%Y%m%d.%H%M%S%d")
    temp_dir = main_runs_dir / "_".join(["dakota", current_time, dir_name])
    os.makedirs(temp_dir)
    print("temp_dir: ", temp_dir)
    return temp_dir


def run_dakota(dakota_conf_path: Path, batch_mode: bool = True):
    print("Starting dakota")
    dakota_conf = dakota_conf_path.read_text()
    callbacks = (
        {"batch_evaluator": batch_evaluator}
        if batch_mode
        else {"evaluator": single_evaluator}  # not sure this will work
    )
    study = dakenv.study(
        callbacks=callbacks,
        input_string=dakota_conf,
    )
    study.execute()
    ## TODO access documentation of dakenv.study -- cannot, also cannot find in https://github.com/snl-dakota/dakota/tree/devel/packages
    # would need to ask Werner


if __name__ == "__main__":
    print("DONE")
