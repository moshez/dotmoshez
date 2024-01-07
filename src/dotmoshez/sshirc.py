import os

from . import ENTRY_DATA
from gather.commands import add_argument


@ENTRY_DATA.register(
    add_argument("--no-dry-run", action="store_true", default=True),
    add_argument("--container", required=True),
    add_argument("--host", required=True),
    add_argument("--user", required=True),
)
def sshirc(args): # pragma: no cover
    execlp = getattr(args, "execlp", os.execlp)
    command = ["tmux", "at"]
    dockerize = ["sudo", "docker", "exec", "-it", "-u", args.user, args.container] + command
    ssh_opts = []
    for key, value in dict(ServerAliveInterval=5, ServerAliveCountMax=2).items():
        ssh_opts.extend(["-o", f"{key}={value}"])
    sshize = ["ssh", "ssh", *ssh_opts, "-t", f"{args.user}@{args.host}"] + dockerize
    execlp(*sshize)