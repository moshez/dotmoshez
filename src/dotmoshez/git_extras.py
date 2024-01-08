import pathlib
import os

from . import ENTRY_DATA
from gather.commands import add_argument


def make_git(args):  # pragma: no cover
    def git(*cmdargs):
        return args.run(["git", *cmdargs], cwd=args.env["PWD"])

    return git


@ENTRY_DATA.register(
    add_argument("--no-dry-run", action="store_true", default=True),
    name="git-sync",
)
def git_sync(args):  # pragma: no cover
    git = make_git(args)
    git("add", ".")
    git("commit", "-a", "-m", "checkpoint")
    git("push")


@ENTRY_DATA.register(
    add_argument("--no-dry-run", action="store_true", default=True),
    add_argument("name"),
    name="git-create",
)
def git_create(args):  # pragma: no cover
    git = make_git(args)
    target_dir = pathlib.Path(args.env["HOME"]) / "src" / args.name
    target_dir.mkdir(parents=True)
    args.env = dict(args.env, PWD=os.fspath(target_dir))
    git("init", ".")
    git("remote", "add", "origin", f"git@github.com:moshez/{args.name}")
    git("push", "-u", "origin", "trunk")
