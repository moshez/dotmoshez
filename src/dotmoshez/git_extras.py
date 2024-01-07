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
