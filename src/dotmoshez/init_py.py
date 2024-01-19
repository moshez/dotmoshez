from __future__ import annotations
import argparse
import logging
import pathlib
from typing import Optional, Mapping
import subprocess

import attrs
from commander_data import run_all
from commander_data.common import GIT, LOCAL_PYTHON
from gather.commands import add_argument
import hyperlink

from . import ENTRY_DATA

LOGGER = logging.getLogger(__name__)


@attrs.frozen
class DetailsBuilder:  # pragma: no cover
    name: Optional[str] = attrs.field(default=None)
    organization: Optional[str] = attrs.field(default=None)
    description: Optional[str] = attrs.field(default=None)
    maintainer_name: Optional[str] = attrs.field(default=None)
    maintainer_email: Optional[str] = attrs.field(default=None)

    def inform(self, name: str, value: Optional[str]) -> DetailsBuilder:
        if getattr(self, name) is not None:
            return self
        return attrs.evolve(self, **{name: value})

    def data(self) -> Mapping[str, str]:
        res = attrs.asdict(self)
        not_ready = [key for key, value in res.items() if value is None]
        if len(not_ready) != 0:
            raise ValueError("not all values retrieved", not_ready)
        return res


def parse_args(
    db: DetailsBuilder, args: argparse.Namespace
) -> DetailsBuilder:  # pragma: no cover
    for field in attrs.fields(type(db)):
        db = db.inform(field.name, getattr(args, field.name))
    return db


def parse_remote(
    db: DetailsBuilder, git_remote_output: str
) -> DetailsBuilder:  # pragma: no cover
    link = hyperlink.parse(git_remote_output.strip())
    organization, name = link.path[-2:]
    db = db.inform("organization", organization)
    db = db.inform("name", name.removesuffix(".git"))
    return db


def parse_user(
    db: DetailsBuilder, git_user_cofig: str
) -> DetailsBuilder:  # pragma: no cover
    details = dict(line.split(None, 1) for line in git_user_cofig.splitlines())
    for key, value in details.items():
        db = db.inform("maintainer_" + key.removeprefix("user."), value)
    return db


def get_details(
    args: argparse.Namespace,
) -> tuple[Mapping[str, str], bool]:  # pragma: no cover
    db = parse_args(DetailsBuilder(), args)
    cwd = pathlib.Path(args.env["PWD"])
    try:
        called = args.safe_run(GIT.remote.get_url.origin, cwd=cwd)
    except subprocess.CalledProcessError:
        has_git = False
        LOGGER.info("Git info not available")
    else:
        db = parse_remote(db, called.stdout)
        has_git = True
    called = args.safe_run(GIT.config(get_regexp=r"^user\."), cwd=cwd)
    db = parse_user(db, called.stdout)
    return db.data(), has_git


ARGS_TO_FIELDS = dict(
    name="project_name",
    description="short_description",
)


@ENTRY_DATA.register(
    add_argument("--no-dry-run", action="store_true", default=False),
    *[
        add_argument("--" + field.name.replace("_", "_"))
        for field in attrs.fields(DetailsBuilder)
    ],
)
def init(args: argparse.Namespace) -> None:  # pragma: no cover
    data, has_git = get_details(args)
    args.run(
        LOCAL_PYTHON.module.copier.copy(
            "gh:moshez/python-standard.git",
            args.env["PWD"],
            data={ARGS_TO_FIELDS.get(key, key): value for key, value in data.items()},
        ),
    )
    if not has_git:
        url = f"https://github.com/{data['organization']}/{data['name']}.git"
        run_all(
            args.run,
            GIT.init("."),
            GIT.remote.add.origin(url),
            GIT.commit(allow_empty=None, m="Initial commit"),
            GIT.push(set_upstream="origin")("trunk"),
            cwd=args.env["PWD"],
        )
