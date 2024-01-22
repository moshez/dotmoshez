import argparse
import contextlib
import os
import pathlib
import sys
import textwrap

from gather.commands import add_argument
from . import ENTRY_DATA
from commander_data import COMMAND
from commander_data.common import LOCAL_PYTHON as PYTHON


@ENTRY_DATA.register(add_argument("--dotfiles", required=True), name="bash-init")
def shell_init(args: argparse.Namespace) -> None:  # pragma: no cover
    home = pathlib.Path(args.env["HOME"])
    dotfiles_bin = pathlib.Path(args.dotfiles) / "bin"
    local_bin = home / ".local" / "bin"
    workon_home = home / "venv"
    target_path = args.env["PATH"]
    for bin_path in [dotfiles_bin, local_bin]:
        path_name = os.fspath(bin_path)
        if path_name in os.get_exec_path(args.env):
            continue
        target_path = f"{path_name}:{target_path}"
    venvwrapper = pathlib.Path(sys.prefix) / "bin" / "virtualenvwrapper.sh"
    print(f"export WORKON_HOME={workon_home}")
    print(f"source {os.fspath(venvwrapper)}")
    args.safe_run(COMMAND.starship.init.bash, capture_output=False)
    print(f"export PATH={target_path}")
    print(
        textwrap.dedent(
            """\
    function set_win_title(){
        echo -ne "\033]0; $(basename "$PWD") ${VIRTUAL_ENV_PROMPT} \007";
    }
    starship_precmd_user_func="set_win_title"
    """
        )
    )


@ENTRY_DATA.register(
    add_argument("--dotfiles", required=True),
    add_argument("--no-dry-run", action="store_true", default=False),
    name="bash-install",
)
def install(args: argparse.Namespace) -> None:  # pragma: no cover
    config = pathlib.Path(args.env["HOME"]) / ".config"
    dotfiles_config = pathlib.Path(args.dotfiles) / "config"
    if config.is_symlink():
        if args.no_dry_run:
            config.unlink()
    if config.exists():
        raise SystemExit("Cannot set up config directory", config)
    if args.no_dry_run:
        config.symlink_to(dotfiles_config)
    bash_profile = pathlib.Path(args.env["HOME"]) / ".bash_profile"
    python = sys.executable
    bash_init = f'eval "$({python} -m dotmoshez bash-init --dotfiles {args.dotfiles})"'
    ssh_agent = f'eval "$({python} -m dotmoshez ssh-agent-env --no-dry-run)"'
    with contextlib.ExitStack() as stack:
        if args.no_dry_run:
            fpout = stack.enter_context(bash_profile.open("a"))
        else:
            fpout = sys.stdout  # type: ignore
        print(bash_init, file=fpout)
        print(ssh_agent, file=fpout)
    args.run(PYTHON.module.pipx.install("tox", "nox", "black", "twine"))
