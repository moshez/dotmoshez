import argparse
import pathlib

from . import ENTRY_DATA
from gather.commands import add_argument
from commander_data.common import GIT
from commander_data import run_all


@ENTRY_DATA.register(
    add_argument("--no-dry-run", action="store_true", default=True),
    name="git-sync",
)
def git_sync(args: argparse.Namespace) -> None:  # pragma: no cover
    run_all(
        args.run,
        GIT.add("."),
        GIT.commit(a=None, m="checkpoint"),
        GIT.push,
        cwd=args.env["PWD"],
    )


@ENTRY_DATA.register(
    add_argument("--no-dry-run", action="store_true", default=True),
    add_argument("name"),
    name="git-create",
)
def git_create(args: argparse.Namespace) -> None:  # pragma: no cover
    target_dir = pathlib.Path(args.env["HOME"]) / "src" / args.name
    target_dir.mkdir(parents=True)
    run_all(
        args.run,
        GIT.init("."),
        GIT.remote.add.origin(f"git@github.com:moshez/{args.name}"),
        GIT.push(u="origin")("trunk"),
        cwd=target_dir,
    )
