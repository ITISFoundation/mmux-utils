### Allows to evaluate in different modes - batch, single set, ...
### also in OSPARC or local deployment
from typing import Callable, List
from pathlib import Path
import dakota.environment as dakenv


### Otherwise could create a class that I can instantiate and give a "model" at initialization time,
# which is given to "run dakota" as input parameter
def batch_evaluator(model: Callable, batch_input: List[dict]):
    return map(model, batch_input)  # FIXME not sure this will work


def single_evaluator(model: Callable, input: dict):
    return model(input)


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
