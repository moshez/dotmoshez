import os
import subprocess
import pathlib

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
    
def parse_environment(env_path):
    try:
        content = env_path.read_text()
    except OSError:
        content = ""
    for line in content.replace(";", "\n").splitlines():
        line = line.split("#", 1)[0]
        line = line.strip()
        if line == "":
            continue
        try:
            key, value = line.split("=", 1)
        except ValueError:
            continue
        yield key, value

def is_agent_up(env, safe_run):
    try:
        pid = env["SSH_AGENT_PID"]
    except KeyError:
        return False
    results = safe_run(["ps", "-ef"])
    lines = iter(results.stdout.splitlines())
    fields = next(lines).split()
    for a_line in lines:
        values = dict(zip(fields, a_line.split()))
        if values["PID"] == pid:
            return True
    return False
        
@ENTRY_DATA.register(
    add_argument("--no-dry-run", action="store_true", default=False),
    add_argument("--env-path", default=pathlib.Path.home() / ".ssh" / "agent-environment"),
    name="ssh-agent-env",
)
def ssh_agent_env(args):
    args.env_path = pathlib.Path(args.env_path)
    env = dict(parse_environment(args.env_path))
    if not is_agent_up(env, args.safe_run):
        bring_up_agent(args.env_path, args.run)
    print(args.env_path.read_text())
