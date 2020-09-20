import os
import random
import string
import glob
import itertools as it

import click
from jina.flow import Flow


RANDOM_SEED = 14


def input_index_data(patterns, size):
    def iter_file_exts(ps):
        return it.chain.from_iterable(glob.iglob(p, recursive=True) for p in ps)

    d = 0
    if isinstance(patterns, str):
        patterns = [patterns]
    for g in iter_file_exts(patterns):
        yield g
        d += 1
        if size is not None and d > size:
            break


def config():
    os.environ["PARALLEL"] = str(2)
    os.environ["SHARDS"] = str(2)
    os.environ["COLOR_CHANNEL_AXIS"] = str(0)
    os.environ["JINA_PORT"] = os.environ.get("JINA_PORT", str(45678))
    os.environ["WORKDIR"] = "./workspace"
    os.makedirs(os.environ["WORKDIR"], exist_ok=True)
    os.environ["JINA_PORT"] = os.environ.get("JINA_PORT", str(45678))


@click.command()
@click.option("--task", "-t")
@click.option("--num_docs", "-n", default=10)
def main(task, num_docs):
    config()
    DATA_BLOB = "./data/*.mp4"
    if task == "index":
        f = Flow().load_config("flow-index.yml")
        with f:
            f.index(input_fn=input_index_data(DATA_BLOB, size=num_docs), batch_size=2)
    elif task == "query":
        f = Flow().load_config("flow-query.yml")
        f.use_rest_gateway()
        with f:
            f.block()
    elif task == "dryrun":
        f = Flow.load_config("flow-query.yml")
        with f:
            pass
    else:
        raise NotImplementedError(
            f"unknown task: {task}. A valid task is either `index` or `query` or `dryrun`."
        )


if __name__ == "__main__":
    main()
