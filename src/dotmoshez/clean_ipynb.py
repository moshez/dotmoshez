import os
import pathlib
import shutil

from . import ENTRY_DATA
from gather.commands import add_argument


@ENTRY_DATA.register(
    add_argument("--no-dry-run", action="store_true", default=True),
    name="clean-ipynb",
)
def clean_ipynb(args):  # pragma: no cover
    for root, dirs, files in os.walk(args.env["PWD"]):
        ipynb_cp = pathlib.Path(root) / ".ipynb_checkpoints"
        if not ipynb_cp.is_dir():
            continue
        shutil.rmtree(ipynb_cp)
