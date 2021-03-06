# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import argparse
import sys

from torque import exceptions
from torque import workspace


def _generate_unique_name(names: set[str], name: str) -> str:
    """TODO"""

    if name in names:
        i = 1
        new_name = f"{name}_{i}"

        while new_name in names:
            new_name = f"{name}_{i}"
            i += 1

        name = new_name

    return name


def _create(arguments: argparse.Namespace):
    """TODO"""

    ws = workspace.load(arguments.workspace)

    if not arguments.name:
        name = f"{arguments.source}_{arguments.destination}"
        name = _generate_unique_name(set(ws.dag.links.keys()), name)

    else:
        name = arguments.name

    try:
        params = workspace.process_parameters(arguments.params_file, arguments.params)

        ws.create_link(name,
                       arguments.type,
                       params,
                       arguments.source,
                       arguments.destination)

        ws.store()

    except exceptions.LinkExists as exc:
        raise RuntimeError(f"{exc}: link exists") from exc

    except exceptions.ComponentNotFound as exc:
        raise RuntimeError(f"{exc}: component not found") from exc

    except exceptions.LinkTypeNotFound as exc:
        raise RuntimeError(f"{exc}: link type not found") from exc

    except exceptions.CycleDetected as exc:
        raise RuntimeError("cycle detected") from exc

    except exceptions.InvalidName as exc:
        raise RuntimeError(f"{exc}: invalid name") from exc


def _remove(arguments: argparse.Namespace):
    """TODO"""

    ws = workspace.load(arguments.workspace)

    try:
        ws.remove_link(arguments.name)
        ws.store()

    except exceptions.LinkNotFound as exc:
        raise RuntimeError(f"{exc}: link not found") from exc


def _show(arguments: argparse.Namespace):
    """TODO"""

    ws = workspace.load(arguments.workspace)

    if arguments.name not in ws.dag.links:
        raise RuntimeError(f"{arguments.name}: link not found")

    print(f"{ws.dag.links[arguments.name]}", file=sys.stdout)


def _list(arguments: argparse.Namespace):
    # pylint: disable=W0613

    """TODO"""

    ws = workspace.load(arguments.workspace)

    for link in ws.dag.links.values():
        print(f"{link}", file=sys.stdout)


def _show_type(arguments: argparse.Namespace):
    """TODO"""

    ws = workspace.load(arguments.workspace)

    try:
        link_type = ws.repo.link(arguments.name)
        print(f"{arguments.name}: {link_type}", file=sys.stdout)

    except exceptions.LinkTypeNotFound as exc:
        raise RuntimeError(f"{exc}: link type not found") from exc


def _list_types(arguments: argparse.Namespace):
    # pylint: disable=W0613

    """TODO"""

    ws = workspace.load(arguments.workspace)
    link_types = ws.repo.links()

    for link in link_types:
        print(f"{link}: {link_types[link]}", file=sys.stdout)


def add_arguments(subparsers):
    """TODO"""

    parser = subparsers.add_parser("link", help="link management")
    subparsers = parser.add_subparsers(required=True, dest="link_cmd", metavar="command")

    create_parser = subparsers.add_parser("create", help="create link")
    create_parser.add_argument("--params-file", help="parameters file")
    create_parser.add_argument("--param", "-p", action="append", dest="params", help="link param")
    create_parser.add_argument("--name", help="link name")
    create_parser.add_argument("--type",
                               default="torquetech.dev/dependency",
                               help="link type, default: %(default)s")
    create_parser.add_argument("source", help="source component")
    create_parser.add_argument("destination", help="destination component")

    remove_parser = subparsers.add_parser("remove", help="remove link")
    remove_parser.add_argument("name", help="link name")

    show_parser = subparsers.add_parser("show", help="show link")
    show_parser.add_argument("name", help="link name")

    subparsers.add_parser("list", help="list links")

    show_type_parser = subparsers.add_parser("show-type", help="show link type")
    show_type_parser.add_argument("name", help="link type name")

    subparsers.add_parser("list-types", help="list link types")


def run(arguments: argparse.Namespace):
    """TODO"""

    cmds = {
        "create": _create,
        "remove": _remove,
        "show": _show,
        "list": _list,
        "show-type": _show_type,
        "list-types": _list_types
    }

    cmds[arguments.link_cmd](arguments)
