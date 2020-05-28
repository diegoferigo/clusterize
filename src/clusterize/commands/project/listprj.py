from argparse import Namespace
from clusterize import utils
from operator import itemgetter
from pathlib import Path
from tree_format import format_tree


def listprj(args: Namespace) -> None:

    projects = utils.project.find_projects(folder=args.dir)

    if len(projects) == 0:
        print(f"No projects found in '{args.dir}'")
        return

    for project in projects:

        directory = Path(project.directory).expanduser().absolute().parts[-1]
        tree = (directory + "/", [])

        for field in project._fields:
            tree[1].append((f"{field} = {getattr(project,field)}", []))

        print(format_tree(node=tree,
                          format_node=itemgetter(0),
                          get_children=itemgetter(1)))
